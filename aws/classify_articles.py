import boto3
from datetime import datetime, timedelta
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from tqdm import tqdm

# Define device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Get articles from the last seven days with null category
    seven_days_ago = datetime.now() - timedelta(days=7)
    response = table.scan(
        FilterExpression='#date >= :seven_days_ago and attribute_not_exists(category)',
        ExpressionAttributeNames={'#date': 'date'},
        ExpressionAttributeValues={':seven_days_ago': seven_days_ago.isoformat()}
    )
    articles = response['Items']

    # Prepare title_subtitle field
    for article in articles:
        article['title_subtitle'] = article['title'] + ' #:# ' + article.get('subtitle', '')

    # Translate
    translation_model_name = "VietAI/envit5-translation"
    translated_texts = translate_batch(['vi:' + article['title_subtitle'] for article in articles], model_name=translation_model_name, batch_size=20)
    
    for article, translated_text in zip(articles, translated_texts):
        article['title_subtitle_en'] = translated_text

    categories = [
        'Monetary Policy and Central Bank Updates',
        'Banking Regulations and Compliance',
        'Interest Rate Changes',
        'Economic Indicators and Market Trends',
        'Credit and Loan Products',
        'Unsecured Loan Market Trends',
        'Digital Banking Innovations',
        'Fintech Developments',
        'Cybersecurity in Finance',
        'Data Privacy and Protection in Banking',
        'Credit Scoring and Risk Assessment',
        'Consumer Credit Trends',
        'Banking Mergers and Acquisitions',
        'Financial Institution Performance Reports',
        'Customer Experience and Service Improvements',
        'Mobile and Online Banking',
        'Personal Finance and Wealth Management',
        'Investment Banking News',
        'Retail Banking Trends',
        'Payment Systems and Digital Currencies',
        'Fraud and Anti-Money Laundering (AML)',
        'Financial Inclusion Initiatives',
        'Sustainability and Green Finance',
        'Economic Recovery and Stimulus Measures',
        'Startups and Venture Capital in Finance',
        'Market and Stock Exchange News',
        'Corporate Lending and Business Financing',
        'Real Estate and Mortgage Markets',
        'International Banking and Finance News',
        'Emerging Technologies (AI, Blockchain) in Finance'
    ]

    classification_results = classify_text_batch_pipeline(
        texts=[article['title_subtitle_en'] for article in articles],
        categories=categories,
        model_name='facebook/bart-large-mnli',
        batch_size=4
    )

    # Update articles with classification results
    for article, result in zip(articles, classification_results):
        article['category'] = result['category']
        article['tags'] = result['tags']

        # Update DynamoDB
        table.update_item(
            Key={'url': article['url']},
            UpdateExpression='SET category = :category, tags = :tags, title_subtitle = :title_subtitle, title_subtitle_en = :title_subtitle_en',
            ExpressionAttributeValues={
                ':category': article['category'],
                ':tags': article['tags'],
                ':title_subtitle': article['title_subtitle'],
                ':title_subtitle_en': article['title_subtitle_en']
            }
        )

    return {
        'statusCode': 200,
        'body': f'Classified {len(articles)} articles'
    }

def classify_text_batch_pipeline(texts, categories, model_name, batch_size=4):
    classifier = pipeline("zero-shot-classification", model=model_name)
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = classifier(batch, categories, multi_label=True)
        
        for result in batch_results:
            category = result['labels'][0]
            tags = [label for label, score in zip(result['labels'], result['scores']) if score > 0.5]
            results.append({'category': category, 'tags': tags})

    return results

def translate_batch(text_list, model_name, batch_size=8, max_length=512):
    """
    text_list (list): List of texts to be translated.
    model_name (str): Name of the translation model.
    batch_size (int): Number of texts to process in each batch.
    max_length (int): Maximum length of the translated text.
    return: List of translated texts.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)  
    translator = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    translated_texts = []
    # Process the text list in batches
    for i in range(0, len(text_list), batch_size):
        batch_texts = text_list[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", padding=True).to(device)
        outputs = translator.generate(inputs.input_ids, max_length=max_length)
        translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translated_texts.extend(translations)
    return translated_texts

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))
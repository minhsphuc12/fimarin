from copy import deepcopy, copy
import nltk
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import torch

# Define device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def to_device(obj, device=device):
    if isinstance(obj, torch.nn.Module):
        return obj.to(device)
    elif isinstance(obj, torch.Tensor):
        return obj.to(device)
    elif isinstance(obj, (list, tuple)):
        return [to_device(x, device) for x in obj]
    elif isinstance(obj, dict):
        return {k: to_device(v, device) for k, v in obj.items()}
    else:
        return obj

def split_article_into_parts(article, max_length):
    # Tokenize the article into sentences
    sentences = sent_tokenize(article)
    
    parts = []
    current_part = ""
    
    for sentence in sentences:
        if len(current_part) + len(sentence) + 1 <= max_length:
            current_part += sentence + " "
        else:
            parts.append(current_part.strip())
            current_part = sentence + " "
    
    # Add the last part if it exists
    if current_part:
        parts.append(current_part.strip())
    
    return [x for x in parts if x != '']

def translate_pipeline(text, model_name, max_length=512):
    global device
    translator = pipeline("translation", model=model_name).to(device)
    
    return [x['translation_text'] for x in translator(text, max_length=max_length)]

def translate_pipeline_batch(texts, model_name, batch_size=4, **kwargs):
    global device
    translator = pipeline("translation", model=model_name).to(device)
    translated_texts = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i + batch_size]
        outputs = translator(batch_texts, **kwargs)
        translated_texts.extend(outputs)
    return [x['translation_text'] for x in translated_texts]


def translate_batch(text_list, model_name, batch_size=8, max_length=512):
    """
    text_list (list): List of texts to be translated.
    translator: Translation model.
    tokenizer: Tokenizer for the model.
    batch_size (int): Number of texts to process in each batch.
    list: List of translated texts.
    """
    global device
    tokenizer = AutoTokenizer.from_pretrained(model_name)  
    translator = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    translated_texts = []
    # Process the text list in batches
    for i in tqdm(range(0, len(text_list), batch_size)):
        batch_texts = text_list[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", padding=True).to(device)
        outputs = translator.generate(inputs.input_ids, max_length=max_length)
        translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translated_texts.extend(translations)
    return translated_texts

def translate_batch_vi_en(text_list, to_en=True, model_name="VietAI/envit5-translation", **kwargs):
    text_list_cp = deepcopy(text_list)
    if to_en:
        text_list_cp = ['vi:' + x for x in text_list_cp]
    else:
        text_list_cp = ['en:' + x for x in text_list_cp]
    return translate_batch(text_list=text_list_cp, model_name=model_name, **kwargs)

def classify_text(text, categories, model_name):
    global device
    classifier = pipeline("zero-shot-classification", model=model_name).to(device)
    result = classifier(text, candidate_labels=categories)
    predicted_category = result['labels'][0]
    return predicted_category

def classify_text_batch_pipeline(texts, categories, model_name, batch_size=4):
    global device
    def _classify_text(text, categories, classifier):
        result = classifier(text, candidate_labels=categories)
        return result['labels'][0]

    classifier = pipeline("zero-shot-classification", model=model_name).to(device)
    
    results = [None] * len(texts)
    
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        future_to_index = {executor.submit(_classify_text, text, categories, classifier): i for i, text in enumerate(texts)}
        
        for future in tqdm(as_completed(future_to_index), total=len(future_to_index)):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                print(f'Text {index} generated an exception: {exc}')
                results[index] = None
    
    return results

# Function to classify a batch of texts
def classify_texts_batch(texts, categories, model_name, batch_size=15):
    global device
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
    
    def classify_texts_single_batch(text_batch, tokenizer, model, categories):
        # Tokenize the texts and the categories
        inputs = tokenizer(text_batch, padding=True, truncation=True, return_tensors="pt").to(device)
        candidate_labels = tokenizer(categories, padding=True, truncation=True, return_tensors="pt")
        
        batch_size = len(text_batch)
        category_size = len(categories)
        
        # Repeat the input ids and attention masks for each candidate label
        repeated_inputs = {k: v.repeat_interleave(category_size, dim=0) for k, v in inputs.items()}
        # Repeat the candidate labels for each input
        repeated_labels = {k: v.repeat(batch_size, 1) for k, v in candidate_labels.items()}

        # Combine inputs and labels for model input
        combined_inputs = {
            "input_ids": torch.cat((repeated_inputs["input_ids"], repeated_labels["input_ids"]), dim=1),
            "attention_mask": torch.cat((repeated_inputs["attention_mask"], repeated_labels["attention_mask"]), dim=1)
        }
        
        # Get model outputs
        with torch.no_grad():
            outputs = model(**combined_inputs)
        
        # Compute the probabilities
        logits = outputs.logits.view(batch_size, category_size, -1)[:, :, 0]
        probabilities = logits.softmax(dim=-1)
        
        # Get the highest scoring category for each text
        best_category_indices = probabilities.argmax(dim=-1)
        best_categories = [categories[idx] for idx in best_category_indices]

        return best_categories

    results = []

    for i in tqdm(range(0, len(texts), batch_size)):
        text_batch = list(texts[i:i + batch_size])
        # text_batch = list(texts[:20])
        batch_categories = classify_texts_single_batch(text_batch, tokenizer, model, categories)
        results.extend(batch_categories)

    return results


# summarize = pipeline('summarization', model='VietAI/vit5-base-vietnews-summarization')

# def summarize_pipeline(text, model_name, **kwargs):
#     '''
#     Args:
#         max_length: default 150
#         min_length: default 30 
#         do_sample: default False
#     '''    
#     summarizer = pipeline("summarization", model=model_name)
#     summary = summarizer(text, **kwargs)
#     return summary[0]['summary_text']

def summarize_pipeline(texts, model_name, **kwargs):
    '''
    Args:
        max_length: default 150
        min_length: default 30 
        do_sample: default False
    '''    
    global device
    summarizer = pipeline("summarization", model=model_name).to(device)
    summaries = summarizer(texts, **kwargs)
    return [x['summary_text'] for x in summaries]


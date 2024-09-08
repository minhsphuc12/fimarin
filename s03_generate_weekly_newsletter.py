import pymongo
from datetime import datetime, timedelta
from openai import OpenAI
import os
from dotenv import load_dotenv
import openai
# Load environment variables
load_dotenv()

# Set up OpenAI API key

def connect_to_mongodb(host="mongodb://localhost:27017/"):
    client = pymongo.MongoClient(host=host)
    return client

def group_articles_by_category(articles):
    grouped = {}
    for article in articles:
        category = article.get('category', 'Uncategorized')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(article)
    return grouped

def extract_news(days):
    client = connect_to_mongodb()
    db = client['news']
    collection = db['articles']

    # Calculate the date 'days' ago
    cutoff_date = (datetime.now() - timedelta(days=days))#.strftime("%Y-%m-%d")
    # Query for articles within the specified date range
    articles = collection.find({
        'date': {'$gte': cutoff_date}
    })

    return list(articles)
    # Convert the cursor to a list and parse the date strings to datetime objects

datanest_categories = ['Credit and Loan Products',
    'Unsecured Loan Market Trends',
    'Digital Banking Innovations',
    'Fintech Developments',
    'Cybersecurity in Finance',
    'Data Privacy and Protection in Banking',
    'Credit Scoring and Risk Assessment',
    'Consumer Credit Trends',
    'Fraud and Anti-Money Laundering (AML)',
    'Financial Inclusion Initiatives']

def generate_newsletter(articles, model='gpt-4o'):
    # Group articles by category
    grouped_articles = {category: articles for category, articles in group_articles_by_category(articles).items() if category in datanest_categories}
    
    # Initialize OpenAI client
    client = OpenAI()
    newsletter_content = "# Weekly Newsletter\n\n"
    all_articles = []
    
    for category, category_articles in grouped_articles.items():
        newsletter_content += f"## {category.capitalize()}\n\n"
        
        # Prepare article information for the prompt
        article_info = "\n".join([f"- Title: {article['title']}\n  Subtitle: {article.get('subtitle', 'N/A')}\n  Summary: {article.get('summary', 'N/A')}\n  URL: {article.get('url', 'N/A')}" for article in category_articles])
        all_articles.extend(category_articles)
        
        # Generate content for each category
        prompt = f"""
        Generate a newsletter section for the '{category}' category. Focus on the most important and impactful news from the past week.
        Summarize key points, highlight trends, and provide insights. Use the following article information:

        {article_info}

        News included in the newsletter should be relevant to the context of our company Datanest: Datanest is credit scoring company that provide credit score and potential customer leads from telco data, clients are banks and other financial institutions in Vietnam, Datanest care about data privacy, security and accuracy of the data, and all related news about the process of unsecured loan applications. 
        
        Your response should be well-structured, engaging, and informative. Aim for about 200-300 words per category.
        Include the URL after mentioning each news item.

        Your response should only include 3-4 categories.

        REMEMBER, THE OUTPUT MUST BE IN VIETNAMESE.
        """

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a skilled news editor creating a weekly newsletter."},
                {"role": "user", "content": prompt}
            ]
        )

        newsletter_content += response.choices[0].message.content + "\n\n"

    # Generate executive summary
    exec_summary_prompt = f"""
    Generate an executive summary of the top 10 most important news items from the following articles:

    {newsletter_content}

    Each summary should be one line long and focus on the most critical information.
    The output should be in Vietnamese and formatted as a bullet point list.
    """

    exec_summary_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a skilled news editor creating an executive summary."},
            {"role": "user", "content": exec_summary_prompt}
        ]
    )

    executive_summary = "## Tóm tắt tin tức quan trọng\n\n" + exec_summary_response.choices[0].message.content + "\n\n"

    # Add executive summary to the beginning of the newsletter
    newsletter_content = executive_summary + newsletter_content

    return newsletter_content

def main():
    days = 1  # Extract news from the last 7 days
    
    articles = extract_news(days)
    print(f'Number of articles: {len(articles)}')
    # print(articles)
    newsletter = generate_newsletter(articles)

    # Ensure the output directory exists
    output_dir = os.path.expanduser('~/fimarin_output')
    os.makedirs(output_dir, exist_ok=True)
    print(output_dir)

    # Save the newsletter to a file
    output_file = os.path.join(output_dir, f'unused_weekly_newsletter_{datetime.now().strftime("%Y%m%d")}.md')
    with open(output_file, 'w') as f:
        f.write(newsletter)

    print(f"Weekly newsletter generated successfully to {output_file}!")


if __name__ == "__main__":
    main()
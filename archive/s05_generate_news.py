import time
from tqdm import tqdm
import pandas as pd, numpy as np
from datetime import datetime
import helpers
from importlib import reload
reload(helpers)
import dotenv

today_date = datetime.today().strftime('%Y-%m-%d')
today_date = '2024-07-16'

df = pd.read_csv(f's04_summarize_content.{today_date}.csv', index_col=0)
df.head(1).T

## gpt
import openai
from openai import OpenAI

def create_newsletter_api(df, api_key, model="gpt-4o", max_tokens=2048):
    """
    Generate a newsletter from a list of news articles using an LLM.
    
    Parameters:
    - df: dataframe
    - model: The LLM model to use, default is "gpt-4o".
    - max_tokens: The maximum number of tokens to use in the response, default is 2048.

    Returns:
    - A string containing the generated newsletter.
    """

    # Prepare the prompt with the list of news articles
    # news_articles_text = "\n\n".join([f"{i+1}. {news}" for i, news in enumerate(news_list)])
    news_records = df.to_dict(orient='records')
    news_articles_text = "\n\n".join([f"\n#TITLE:{record['title_subtitle']}#CONTENT:\n{record['content']}\n\n" for record in news_records])
    
    prompt = f"""
    You are an expert journalist and editor. You are tasked with creating a well-structured and engaging newsletter from a list of news articles. The newsletter should have the following features:
    REMEMBER, THE OUTPUT MUST BE IN VIETNAMESE.

    1. Title: Provide a catchy and informative title for the newsletter.
    2. Introduction: Write a brief introduction that outlines the main themes and significance of the news articles in the newsletter.
    3. Sections: Organize the articles into the following sections:
       - Top Stories: Summarize the top 3-5 most significant news articles that represent the most important events or trends.
       - Business & Finance: Summarize news related to business, finance, markets, and the economy.
       - Technology: Summarize news related to technology, innovation, and advancements.
       - Legal & Regulatory: Summarize news related to legal matters, regulations, and government policies.
       - Market Trends: Summarize news that highlights current trends in various markets.
       - Product & Services: Summarize news related to product launches, service updates, or other related announcements.
       - General News: Summarize other news that doesn’t fit into the above categories but is still important to include.
    4. Closing Remarks: Write a brief conclusion that wraps up the newsletter, possibly hinting at upcoming events or things to watch for in the near future.

    For each section, choose the most relevant articles and provide concise summaries. Ensure that the newsletter flows logically, with smooth transitions between sections. Use clear, engaging language that is appropriate for a general audience.
    REMEMBER, THE OUTPUT MUST BE IN VIETNAMESE.

    Here is the list of news articles:

    {news_articles_text}
    """

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert journalist and editor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract the text of the response
    newsletter = response.choices[0].message.content.strip()
    return newsletter

# Generate the newsletter
env = dict(dotenv.dotenv_values())
api_key=env['OPENAI_API_KEY']
newsletter = create_newsletter_api(df, api_key=api_key, max_tokens=2048)
print(newsletter)

### open llm

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def create_newsletter_opensource(df, model_name="google/gemma-2-2b-it", max_length=1024):
    """
    Generate a newsletter from a list of news articles using an open-source LLM.
    
    Parameters:
    - df: dataframe
    - model_name: The Hugging Face model to use, default is "Writer/gemma-2-9b".
    - max_length: The maximum length for the generated text in tokens, default is 1024.

    Returns:
    - A string containing the generated newsletter.
    """

    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Move model to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # Prepare the prompt
    news_records = df[['title_subtitle_en', 'content_summarize_en']].to_dict(orient='records')
    news_articles_text = "\n\n".join([f"\n#TITLE:{record['title_subtitle_en']}#CONTENT:\n{record['content_summarize_en']}\n\n" for record in news_records])
    
    prompt = f"""
    You are an expert journalist and editor. You are tasked with creating a well-structured and engaging newsletter from a list of news articles. The newsletter should have the following features:
    
    1. Title: Provide a catchy and informative title for the newsletter.
    2. Introduction: Write a brief introduction that outlines the main themes and significance of the news articles in the newsletter.
    3. Sections: Organize the articles into the following sections:
       - Top Stories: Summarize the top 3-5 most significant news articles that represent the most important events or trends.
       - Business & Finance: Summarize news related to business, finance, markets, and the economy.
       - Technology: Summarize news related to technology, innovation, and advancements.
       - Legal & Regulatory: Summarize news related to legal matters, regulations, and government policies.
       - Market Trends: Summarize news that highlights current trends in various markets.
       - Product & Services: Summarize news related to product launches, service updates, or other related announcements.
       - General News: Summarize other news that doesn’t fit into the above categories but is still important to include.
    4. Closing Remarks: Write a brief conclusion that wraps up the newsletter, possibly hinting at upcoming events or things to watch for in the near future.

    For each section, choose the most relevant articles and provide concise summaries. Ensure that the newsletter flows logically, with smooth transitions between sections. Use clear, engaging language that is appropriate for a general audience.

    Here is the list of news articles:
    

    {news_articles_text}
    """

    # Encode the prompt
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length).to(device)

    # Generate the newsletter
    a = time.time()
    outputs = model.generate(
        inputs.input_ids,
        max_length=int(max_length*1.1),
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )
    print(time.time()-a)

    outputs
    # Decode the output
    newsletter = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return newsletter

# Example usage
news_list = [
    "Article 1: The stock market surged today as major indices hit record highs...",
    "Article 2: A new smartphone was launched by a major tech company today...",
    "Article 3: A landmark legal ruling was made today, affecting privacy laws...",
    # Add more articles here...
]

# Generate the newsletter
newsletter_opensource = create_newsletter_opensource(df)
print(newsletter_opensource)
import os
import pandas as pd
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_last_n_days_data(reference_date, n_days):
    """
    Read news data from the last n days, starting from the reference date.

    Args:
    reference_date (str): The date to start backtracking from, in 'YYYY-MM-DD' format.
    n_days (int): Number of days to look back.

    Returns:
    pd.DataFrame or None: Concatenated DataFrame of data from the last n days, or None if no data found.
    """
    reference_date = datetime.strptime(reference_date, '%Y-%m-%d')
    data_frames = []

    for i in range(n_days):
        date = (reference_date - timedelta(days=i)).strftime('%Y-%m-%d')
        filename = f's04_summarize_content.{date}.csv'
        
        if os.path.exists(filename):
            df = pd.read_csv(filename, index_col=0)
            data_frames.append(df)
    
    return pd.concat(data_frames, ignore_index=True) if data_frames else None

def generate_newsletter(data):
    """
    Generate a weekly newsletter using OpenAI's GPT-3.5 model.
    """
    prompt = f"""
    Generate a weekly newsletter in Vietnamese based on the following news summaries:

    {data['content_summarize_en'].to_string(index=False)}

    The newsletter should include:
    1. A brief introduction
    2. Top 3-5 highlights of the week
    3. Short summaries of each news item
    4. A conclusion

    Format the newsletter in Markdown.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates newsletters."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].message['content'].strip()

def save_newsletter(content, filename):
    """
    Save the generated newsletter to a file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Get data from the last seven days
    today = '2024-07-18'
    # today = datetime.now().strftime('%Y-%m-%d')
    data = get_last_n_days_data(today, 7)
    
    if data is None or data.empty:
        print("No data found for the last seven days.")
        return

    # Generate the newsletter
    newsletter_content = generate_newsletter(data)

    # Save the newsletter
    filename = f'weekly_newsletter_{today}.md'
    save_newsletter(newsletter_content, filename)
    
    print(f"Newsletter generated and saved as {filename}")

if __name__ == "__main__":
    main()

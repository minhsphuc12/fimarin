# News Aggregator and Analysis System

## Steps

- Get several top coding LLM (Deepseek Coder, code llama) with support tools (ollama, gradio, langchain, llamaindex, etc.) inside telco (VT first because we have GPU there)
- Setup LLM to work with GPU
- Step web portal to use chatbot
- Code documentation every code inside etl and other critical packages
- Revise code to insert comment into every code chunks
- Use LLM to revise, summarize and control every commit

## Vector Database Setup

### Qdrant (Local Solution)

// ... (existing Qdrant setup instructions) ...

### Pinecone (Cloud Solution)

To use Pinecone as a cloud-based vector database solution, follow these steps:

1. Sign up for a Pinecone account at https://www.pinecone.io/

2. Create a new project and obtain your API key.

3. Set up your environment variables:
   - Add the following to your `.env` file:
     ```
     PINECONE_API_KEY=your_pinecone_api_key
     NEWS_INDEX_NAME=your_index_name
     ```

4. Install the Pinecone client:
   ```
   pip install pinecone-client
   ```

5. Use the `s05_embed_news_to_pinecone.py` script to embed and upload your news articles to Pinecone.

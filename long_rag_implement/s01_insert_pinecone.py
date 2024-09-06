# !pip install -q transformers==4.41.2
# !pip install -q bitsandbytes==0.43.1
# !pip install -q accelerate==0.31.0
# !pip install -q langchain==0.2.5
# !pip install -q langchainhub==0.1.20
# !pip install -q langchain-chroma==0.1.1
# !pip install -q langchain-community==0.2.5
# !pip install -q langchain_huggingface==0.0.3
# !pip install -q python-dotenv==1.0.1
# !pip install -q pypdf==4.2.0
# !pip install -q numpy==1.24.4
# !pip install faiss-gpu
# !pip install langchain_pinecone
# !pip install pinecone
# !pip install sentence-transformers
# !pip install load_dotenv


import os
import math
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import ReadTheDocsLoader

# Loadn file .env
load_dotenv()

# # Retrieve the API key from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# # Initialize Pinecone with the new API
pc = Pinecone(api_key=PINECONE_API_KEY)

# embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to load multiple PDFs
def load_multiple_pdfs(file_paths):
    loader = PyPDFLoader
    documents = []
    for file_path in file_paths:
        pdf_loader = loader(file_path)
        documents.extend(pdf_loader.load())  # Append all pages' texts from each PDF
    return documents

# List of PDF files to load
file_paths = ["./your_workspace/" + path for path in os.listdir('./your_workspace/')]


def preprocess_text(text):
    # Dictionary of common math symbols and their textual equivalents
    math_symbols = {
        '∫': 'integral',
        '∑': 'sum',
        '∏': 'product',
        '√': 'sqrt',
        '∞': 'infinity',
        '∂': 'partial',
        '∇': 'nabla',
        '∆': 'delta',
        '≈': 'approximately',
        '≠': 'not equal',
        '≤': 'less than or equal to',
        '≥': 'greater than or equal to',
        '∈': 'element of',
        '∉': 'not an element of',
        '⊂': 'subset of',
        '⊃': 'superset of',
        '∩': 'intersection',
        '∪': 'union',
    }

    # Replace common math symbols with textual equivalents
    for symbol, text_equiv in math_symbols.items():
        text = text.replace(symbol, f' {text_equiv} ')

    # Handle superscripts and subscripts
    text = re.sub(r'(\w+)(\^|\^{)(\w+)}?', r'\1 to the power of \3', text)  # x^2 -> x to the power of 2
    text = re.sub(r'(\w+)(_|_{)(\w+)}?', r'\1 subscript \3', text)  # x_1 -> x subscript 1

    # Handle Greek letters
    greek_letters = {
        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'epsilon',
        'θ': 'theta', 'λ': 'lambda', 'μ': 'mu', 'π': 'pi', 'σ': 'sigma', 'φ': 'phi', 'ω': 'omega'
    }
    for greek, english in greek_letters.items():
        text = re.sub(rf'\b{greek}\b', english, text, flags=re.IGNORECASE)

    # Replace common LaTeX-style commands
    latex_commands = {
        r'\frac': 'fraction', r'\lim': 'limit', r'\sin': 'sine', r'\cos': 'cosine', r'\tan': 'tangent',
        r'\log': 'logarithm', r'\exp': 'exponential', r'\sum': 'sum', r'\prod': 'product'
    }
    for command, replacement in latex_commands.items():
        text = text.replace(command, replacement)

    # Remove any remaining LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)

    # Remove any remaining special characters, but keep basic punctuation
    text = re.sub(r'[^\w\s.,;!?()-]', ' ', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def bulk_upload_to_pinecone(file_paths, embeddings, index_name, batch_size=500):
    # ingest_docs(file_paths)
    documents = load_multiple_pdfs(file_paths)

    # Split documents into manageable chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(documents)

    total_docs = len(docs)
    num_batches = math.ceil(total_docs / batch_size)

    for i in range(num_batches):
        start = i * batch_size
        end = min((i + 1) * batch_size, total_docs)
        batch_docs = docs[start:end]
        try:
          print(f"Going to add {len(batch_docs)} to Pinecone")
          PineconeVectorStore.from_documents(batch_docs, embeddings, index_name=index_name)
          print("****Loading to vectorstore done ***")
        except Exception as e:
          print(f"Error adding batch {i + 1}: {e}")
          continue

    print(f"Finished uploading {total_docs} vectors to Pinecone index '{index_name}'")


if __name__ == "__main__":
    bulk_upload_to_pinecone(file_paths, embeddings, index_name=INDEX_NAME)
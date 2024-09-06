import os
import torch
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import BitsAndBytesConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface.llms import HuggingFacePipeline
from langchain import hub
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Loadn file .env
load_dotenv()

# # Retrieve the API key from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# # Initialize Pinecone with the new API
pc = Pinecone(api_key=PINECONE_API_KEY)

# embeddings
EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Vicuna model with quantization configuration
MODEL_NAME = "lmsys/vicuna-7b-v1.5"

nf4_config = BitsAndBytesConfig(
  load_in_4bit = True ,
  bnb_4bit_quant_type = "nf4",
  bnb_4bit_use_double_quant = True ,
  bnb_4bit_compute_dtype = torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
  MODEL_NAME,
  quantization_config = nf4_config,
  low_cpu_mem_usage = True,
)

# Set up the tokenizer and pipeline
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map = "auto",
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9
)
chat = HuggingFacePipeline(pipeline=generation_pipeline)


## Setup Prompt
prompt = hub.pull("rlm/rag-prompt")
docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=EMBEDDINGS)
rag_chain = (
  {"context": docsearch.as_retriever() , "question": RunnablePassthrough()}
  | prompt
  | chat
  | StrOutputParser()
)

def format_docs(docs):
  return "\n\n".join(doc.page_content for doc in docs)

def run_rag_chain(rag_chain, question: str):
    '''
    Run the RAG chain with the given question.
    rag_chain: The RAG chain to use.
    question: The question to ask the chain.
    '''
    try:
        output = rag_chain.invoke(question)
        # Extract the answer part from the output
        answer = output.split("Answer: ")[1].strip()
        return answer
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

USER_QUESTION = "What is Term Frequency–Inverse Document Frequency?"
answer = run_rag_chain(rag_chain, USER_QUESTION)
if answer:
    print(answer)
else:
    print("Failed to generate an answer.")
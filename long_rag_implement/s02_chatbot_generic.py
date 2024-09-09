import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

# Load .env file
load_dotenv()

# Retrieve API keys from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

class RAGChatbot:
    def __init__(self, generator='gpt-3.5-turbo', embedder='sentence-transformers/all-MiniLM-L6-v2'):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

        # Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=embedder)

        # Initialize OpenAI ChatGPT-4
        self.llm = ChatOpenAI(model_name=generator, temperature=0.7, api_key=OPENAI_API_KEY)

        # Setup Vector Store
        self.docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=self.embeddings)

        # Setup Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.chains.combine_documents import create_stuff_documents_chain

        qa_system_prompt = """You are an assistant for question-answering tasks. 
        Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know. 
        Use three sentences maximum and keep the answer concise.{context}"""
        qa_prompt = ChatPromptTemplate.from_messages([("system", qa_system_prompt), MessagesPlaceholder("chat_history"),("human", "{question}"),])
        # question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # from langchain import hub
        # prompt = hub.pull("rlm/rag-prompt")

        
        # Setup RAG Chain
        self.rag_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.docsearch.as_retriever(),
            memory=self.memory,
            verbose=True,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            get_chat_history=lambda h: h  # This prevents reformatting of chat history
        )

    def chat(self, question: str) -> str:
        """
        Ask a question to the chatbot.
        
        :param question: The question to ask
        :return: The chatbot's response
        """
        try:
            response = self.rag_chain({"question": question})
            return response['answer'].strip()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "I'm sorry, I encountered an error while processing your question."

# Usage example
if __name__ == "__main__":
    # chatbot = RAGChatbot()
    chatbot = RAGChatbot(generator='gpt-4o')
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Goodbye!")
            break
        response = chatbot.chat(user_input)
        print(f"Chatbot: {response}")
        
    chatbot.chat("explain reinforcement learning like i am 5")
    chatbot.chat("what did I just ask you to do?")
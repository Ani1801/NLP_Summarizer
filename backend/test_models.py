import os
from dotenv import load_dotenv

load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

def check_models():
    print("Testing HuggingFaceEmbeddings...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v = embeddings.embed_query("Hello world")
        print(f"✅ Embeddings working! Dimension: {len(v)}")
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        
    print("Testing ChatGoogleGenerativeAI...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("Google_API_KEY")
        )
        print("✅ LLM instantiation successful.")
    except Exception as e:
        print(f"❌ LLM failed: {e}")

if __name__ == "__main__":
    check_models()

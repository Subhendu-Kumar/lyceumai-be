from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

gemini = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

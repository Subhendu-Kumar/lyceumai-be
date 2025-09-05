import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

syllabus_vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="class-syllabus",
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
    chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
)

class_material_vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="class-materials",
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
    chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
)

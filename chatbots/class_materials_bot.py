from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Annotated
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool, InjectedToolArg
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from utils.gemini_util import gemini
from utils.chroma_util import class_material_vector_store

from pydantic import BaseModel

# -------------------------------
# FastAPI Router
# -------------------------------
chat_router = APIRouter(prefix="/chat", tags=["ChatBot"])


# -------------------------------
# TOOLS
# -------------------------------
@tool
def retrieve_documents(
    query: str, material_id: Annotated[str, InjectedToolArg]
) -> List[Dict[str, Any]]:
    """Retrieve top documents from Chroma DB for a given material_id and query."""
    try:
        docs = class_material_vector_store.similarity_search(
            query, k=3, filter={"material_id": material_id}
        )
        return [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    except Exception as e:
        return [{"error": str(e)}]


@tool
def search_wikipedia(query: str) -> str:
    """Fetch a brief summary from Wikipedia for the given query."""
    try:
        print("wiki search query:", query)
        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        return wiki.run(query)
    except Exception as e:
        return f"Error fetching Wikipedia info: {e}"


# -------------------------------
# STATE
# -------------------------------
class ChatState(dict):
    query: str
    material_id: str
    history: List[Dict[str, str]]
    docs: List[Dict[str, Any]]
    wiki_info: str
    final_answer: str
    need_wiki: bool


# -------------------------------
# GRAPH NODES
# -------------------------------
def retrieve_docs_node(state: ChatState):
    """Step 1: Retrieve documents from Chroma"""
    docs = retrieve_documents.invoke(
        {"query": state["query"], "material_id": state["material_id"]}
    )
    state["docs"] = json.loads(docs) if isinstance(docs, str) else docs
    return state


def decide_need_wiki_node(state: ChatState):
    """Step 2: Ask the LLM whether Wikipedia search is needed."""
    context = "\n".join([d.get("content", "") for d in state.get("docs", [])])

    decision_prompt = f"""
You are a reasoning assistant. The user asked: "{state['query']}".
Here are the documents retrieved from the class material:

{context[:1500]}

Decide if the above documents are sufficient to answer the question.
If the context is unrelated, incomplete, or off-topic, respond with 'YES' (Wikipedia needed).
If it’s sufficient and clear, respond with 'NO' (Wikipedia not needed).

Answer only with YES or NO.
"""

    llm_response = gemini.invoke([HumanMessage(content=decision_prompt)])
    text = llm_response.content.strip().upper()

    state["need_wiki"] = "YES" in text
    return state


def search_wikipedia_node(state: ChatState):
    """Step 3: If LLM decides Wikipedia is needed, fetch it."""
    wiki = search_wikipedia.invoke({"query": state["query"]})
    state["wiki_info"] = wiki if isinstance(wiki, str) else str(wiki)
    return state


def generate_response_node(state: ChatState):
    """Step 4: Generate the final Gemini response."""
    context = ""
    if state.get("docs"):
        context += "\n".join([d.get("content", "") for d in state["docs"]])
    if state.get("wiki_info"):
        context += f"\nWikipedia Info:\n{state['wiki_info']}"

    messages = []
    for h in state.get("history", []):
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        else:
            messages.append(AIMessage(content=h["content"]))

    messages.append(
        HumanMessage(
            content=f"Answer the question using the following context:\n{context}\n\nQuestion: {state['query']}"
        )
    )

    response = gemini.invoke(messages)
    state["final_answer"] = response.content
    return state


# -------------------------------
# GRAPH DEFINITION
# -------------------------------
graph = StateGraph(ChatState)

graph.add_node("retrieve_docs", retrieve_docs_node)
graph.add_node("decide_need_wiki", decide_need_wiki_node)
graph.add_node("search_wiki", search_wikipedia_node)
graph.add_node("generate_response", generate_response_node)

graph.set_entry_point("retrieve_docs")
graph.add_edge("retrieve_docs", "decide_need_wiki")

# Conditional edge based on Gemini decision
graph.add_conditional_edges(
    "decide_need_wiki",
    lambda state: "search_wiki" if state.get("need_wiki") else "generate_response",
    {
        "search_wiki": "search_wiki",
        "generate_response": "generate_response",
    },
)

graph.add_edge("search_wiki", "generate_response")
graph.add_edge("generate_response", END)

chat_graph = graph.compile()


# -------------------------------
# FASTAPI REQUEST MODEL
# -------------------------------
class RequestData(BaseModel):
    query: str
    material_id: str
    history: List[Dict[str, str]] = []


# -------------------------------
# FASTAPI ENDPOINT
# -------------------------------
@chat_router.post("/query")
async def classroom_chat(req_data: RequestData):
    """
    Handles chatbot interactions via LangGraph flow.
    """
    try:
        if not req_data.query or not req_data.material_id:
            raise HTTPException(
                status_code=400, detail="query and material_id are required"
            )

        # Initialize state
        state = ChatState(
            query=req_data.query,
            material_id=req_data.material_id,
            history=req_data.history,
            docs=[],
            wiki_info="",
            final_answer="",
            need_wiki=False,
        )

        # Run graph pipeline
        final_state = chat_graph.invoke(state)

        return JSONResponse(
            {
                "response": final_state["final_answer"],
                "docs_used": len(final_state.get("docs", [])),
                "wiki_used": bool(final_state.get("wiki_info")),
                "need_wiki": final_state.get("need_wiki", False),
                "docs": final_state.get("docs", []),
                "wiki_info": final_state.get("wiki_info", ""),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

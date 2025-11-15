from langchain import hub
from typing import Optional
from utils.gemini_util import gemini
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from utils.chroma_util import syllabus_vector_store
from fastapi import APIRouter, HTTPException, status
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools.tavily_search import TavilySearchResults


agent_router = APIRouter(prefix="/agent", tags=["Classroom AI Agent"])


class AgentResponse(BaseModel):
    ans: Optional[str] = Field(default=None, description="Normal answer if type is ans")


@tool(
    description="Search the syllabus vector store for relevant information based on the query"
)
def search_syllabus(query: str) -> str:
    try:
        results = syllabus_vector_store.similarity_search(query, k=3)
        if not results or len(results) == 0:
            return "SYLLABUS_NOT_FOUND:This topic is not covered in the syllabus or is out of scope."
        context = "\n\n".join([doc.page_content for doc in results])
        answer_prompt = f"""Based on the following syllabus content, answer the user's question.
        If the content doesn't contain relevant information, state that the topic is not in the syllabus.
        
        Syllabus Content:
        {context}
        
        User Question: {query}
        
        Answer:
        """
        response = gemini.invoke(answer_prompt)
        return f"SYLLABUS_ANSWER:{response.content}"
    except Exception as e:
        return f"SYLLABUS_ERROR:Error searching syllabus: {str(e)}"


search_tool = TavilySearchResults(max_results=4)

tools = [search_syllabus, search_tool]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm=gemini, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=5
)


def process_agent_response(response: dict) -> AgentResponse:
    output = response.get("output", "")
    return AgentResponse(ans=output)


@agent_router.post(
    "/chat", response_model=AgentResponse, status_code=status.HTTP_200_OK
)
async def chat_with_agent():
    try:
        user_query = "Explain the concept of photosynthesis as per the syllabus."
        response = agent_executor.invoke({"input": user_query})
        structured_response = process_agent_response(response)
        return structured_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}",
        )

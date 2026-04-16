from dotenv import load_dotenv
from typing import Annotated,Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel,Field
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from openrouter import OpenRouter
import os

load_dotenv()

prompt = 'helo'

llm  = ChatOllama(
    model='gemma2:2b',
    temprature=0,
)




class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder = StateGraph(State)

def gem(state:State):
    return {'messages': llm.invoke(state['messages'])}

graph_builder.add_node('gem',gem)
graph_builder.add_edge(START,'gem')
graph_builder.add_edge('gem',END)


graph = graph_builder.compile()

user_input = input('enter a message:')
state = graph.invoke({'messages':[{'role':'user','content':user_input}]})

print(state['messages'][-1].content)
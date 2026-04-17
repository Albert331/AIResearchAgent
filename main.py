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
    model='gemma3:4b',
    temprature=0,
)

class MessageClassifier(BaseModel):
    message_type: Literal['emotional','logical']= Field(
        ...,
        description='classify is the message requires an emotional or logical response',
    )


class State(TypedDict):
    messages:Annotated[list,add_messages]
    messageType:str | None




def classify_message(state:State):
    last_message = state['messages'][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([{
        'role':'system',
        'content':"""classify the user message as either emotional or logical
        - 'emotional': if the user asks for emotional support ,therapy,deals with feelings or sarcasm
        - 'logical' : if the user asks for facts, information, logical analysis or practical solutions
                        
        """
    },
    {
        'role':'user',
        'content':last_message.content,
    }
    ])
    return {'messageType':result.message_type}

def router(state:State):
    message_type = state.get('messageType', 'logical')
    if message_type == 'emotional':
        return{'next':'therapist'}

    return {'next':'logical'}


def logical_agent(state:State):
    last_message = state['messages'][-1]

    messages = [
        {
            'role': 'system',
            'content': """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses.
                """
        },
        {
            'role': 'user',
            'content': last_message.content
        }
    ]
    response = llm.invoke(messages)
    return {'messages': {'role': 'gem', 'content': response.content}}



def therapist_agent(state:State):
    last_message = state['messages'][-1]

    messages = [
        {
            'role':'system',
            'content':"""You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked.
            
            """
        },
        {
            'role' :'user',
            'content':last_message.content
        }
    ]
    response = llm.invoke(messages)
    return{'messages': {'role':'gem','content':response.content}}





graph_builder = StateGraph(State)

graph_builder.add_node('classifier',classify_message)
graph_builder.add_node('router',router)
graph_builder.add_node('logical',logical_agent)
graph_builder.add_node('therapist',therapist_agent())

graph_builder.add_edge(START,'classifier')
graph_builder.add_edge('classifier','router')
graph_builder.add_conditional_edges(
    'router',
    lambda state: state.get('next')
)


graph = graph_builder.compile()



from dotenv import load_dotenv
from typing import Annotated,List
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from pydantic import BaseModel,Field

from weboperations import serp_search,reddit_search_api

#dataseit id

load_dotenv()

llm = ChatOllama(
    model='gemma3:4b',
    temperature=0
)

class State(TypedDict):
    messages: Annotated[list,add_messages]
    user_ques:str | None
    google_res: str|None
    bing_res: str|None
    reddit_res : str | None
    selected_redit_url : list[str] | None
    reddit_post_data : list | None
    google_analysis: str|None
    bing_analysis: str|None
    reddit_analysis: str|None
    final_ans : str | None

def google_search(state: State):
    user_question = state.get('user_ques','')
    print(f'gogol search for : {user_question}')
    google_res = serp_search(user_question,engine='google')
    print(f'{google_res}')
    return {'google_res':google_res}

def bing_search(state: State):
    user_question = state.get('user_ques', '')
    print(f'bing search for : {user_question}')
    bing_res = serp_search(user_question,engine='bing')
    print(f'{bing_res}')
    return {'bing_res':bing_res}
    return {'bing_res': bing_res}

def reddit_search(state: State):
    user_question = state.get('user_ques', '')
    print(f'redit search for : {user_question}')
    reddit_res = reddit_search_api(user_question)
    print(reddit_res)
    return {'reddit_res': reddit_res}

def reddit_post_analysis(state: State):
    return {'selected_redit_url':[]}

def reddit_post(state: State):
    return {'reddit_post_data':[]}

def google_analysis(state: State):
    return {'google_analysis':''}

def bing_analysis(state: State):
    return {'bing_analysis':''}

def reddit_analysis(state: State):
    return {'reddit_analysis':''}

def final_analysis(state: State):
    return {'final_ans':''}


gb=StateGraph(State)

gb.add_node('google_search',google_search)
gb.add_node('bing_search',bing_search)
gb.add_node('reddit_search',reddit_search)
gb.add_node('reddit_post_analysis',reddit_post_analysis)
gb.add_node('reddit_post',reddit_post)
gb.add_node('google_analysis',google_analysis)
gb.add_node('bing_analysis',bing_analysis)
gb.add_node('reddit_analysis',reddit_analysis)
gb.add_node('final_analysis',final_analysis)

gb.add_edge(START,'google_search')
gb.add_edge(START,'bing_search')
gb.add_edge(START,'reddit_search')

gb.add_edge('google_search','reddit_post_analysis')
gb.add_edge('bing_search','reddit_post_analysis')
gb.add_edge('reddit_search','reddit_post_analysis')

gb.add_edge('reddit_post_analysis','reddit_post')

gb.add_edge('reddit_post','google_analysis')
gb.add_edge('reddit_post','bing_analysis')
gb.add_edge('reddit_post','reddit_analysis')

gb.add_edge('google_analysis','final_analysis')
gb.add_edge('bing_analysis','final_analysis')
gb.add_edge('reddit_analysis','final_analysis')

gb.add_edge('final_analysis',END)

graph = gb.compile()

def smort_gemma():
    print('researching gemma on duty')
    print('type exit to bie bie\n')

    while True:
        user_msg = input('me: ')
        if user_msg == 'exit':
            print('bie bie ')
            break

        state = {
            'messages': [{'role':'user','content':user_msg}],
            'user_ques':user_msg,
            'google_res':  None,
            'bing_res':  None,
            'reddit_res':  None,
            'selected_redit_url':  None,
            'reddit_post_data':  None,
            'google_analysis':  None,
            'bing_analsis':  None,
            'reddit_analysis':  None,
            'final_ans': None,

        }

        print('\n startin the hunt.... on gogol bing redit\n')
        final_state = graph.invoke(state)

        if final_state.get('final_analysis'):
            print(f'VERDICT:\n{final_state.get("final_analysis")}')

        print('=' * 80)

smort_gemma()
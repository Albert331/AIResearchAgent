from certifi import contents
from dotenv import load_dotenv
from typing import Annotated,List

from dotenv.cli import enumerate_env
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import BaseModel,Field

from prompts import (get_reddit_analysis_messages,get_google_analysis_messages,get_bing_analysis_messages,get_reddit_url_analysis_messages,get_synthesis_messages)

from weboperations import serp_search, reddit_search_api, reddit_post_retrieval

#dataseit id

load_dotenv()

llm = ChatOllama(
    model='gemma3:4b',
    temperature=0
)

class RedditAnalysis(BaseModel):
    selected_urls:List[str] = Field(
        description="List of Reddit URLs that contain valuable information for answering the user's question"
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
    user_req = state.get('user_ques','')
    reddit_result = state.get('reddit_res','')
    if not reddit_result:
        return None

    structured_llm = llm.with_structured_output(RedditAnalysis)
    messages = get_reddit_url_analysis_messages(user_req,reddit_result)

    try:
        analysis = structured_llm.invoke(messages)
        selected_urls = analysis.selected_urls

        for i, url in enumerate(selected_urls):
            print(f'{i},{url}')

    except Exception as e:
        print(e)
        selected_urls = []




    return {'selected_redit_url':[selected_urls}

def reddit_post(state: State):
        print('getting reddit post comments ')
        selected_urls = state.get('selected_redit_url',[])

        if not selected_urls:
            return {'reddit_post_data':[]}

        print(f'analysis of {len(selected_urls)} urls ongoing ')
        reddit_post_data = reddit_post_retrieval(selected_urls)

        if reddit_post_data:
            print('succescfull got posts')
        else:
            print('failed to get data')
            return {'reddit_post_data':reddit_post_data}


        return {'reddit_post_data':[]}

def google_analysis(state: State):
    print('analysing google results')
    user_ques = state.get('user_ques','')
    google_res = state.get('google_res','')

    messages = get_google_analysis_messages(user_ques,google_res)
    reply = llm.invoke(messages)

    return {'google_analysis':reply.content}

def bing_analysis(state: State):
    print('analysing bing results')
    user_ques = state.get('user_ques', '')
    bing_res = state.get('bing_res', '')

    messages = get_binggoogle_analysis_messages(user_ques, bing_res)
    reply = llm.invoke(messages)
    return {'bing_analysis':reply.content}

def reddit_analysis(state: State):
    print('analysing reddit results')
    user_ques = state.get('user_ques', '')
    reddit_res = state.get('reddit_res', '')
    reddit_res = state.get('reddit_res', '')
    reddit_post_data = state.get('reddit_post_data','')

    messages = get_reddit_analysis_messages(user_ques, reddit_post_data,reddit_post_data)
    reply = llm.invoke(messages)
    return {'reddit_post_data':reply.content}

def final_analysis(state: State):
    print('final result')
    user_ques = state.get('user_ques', '')
    google_analysis = state.get('google_analysis','')
    bing_analysis = state.get('bing_analysis','')
    reddit_analysis = state.get('reddit_analysis','')

    messages = get_synthesis_messages(google_analysis,bing_analysis,reddit_analysis)
    reply = llm.invoke(messages)

    return {'final_ans':reply.content,'messages':[{'role':'ai','content':reply.content}]}


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
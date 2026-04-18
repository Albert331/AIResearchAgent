import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

from tornado.web import url

from snapshot_operations import download_snapshot,snapshot_status

load_dotenv()

def make_api_request(url,**kwargs):
    api_key = os.getenv("BRIGHT_DATA_API")

    headers ={
        'Authorization': f"Bearer {api_key}",
        "content-type": "application/json",

    }

    try:
        response = requests.post( url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print( f'api failed: {err}')
        return None
    except Exception as err:
        print(f'unknown error{err}')
        return None



def serp_search(query , engine='google'):
    if engine == 'google':
        base_url = 'https://google.com/search'
    elif engine == 'bing':
        base_url = 'https://bing.com/search'
    else:
        raise ValueError(f' {engine} not supported')

    url = 'https://api.brightdata.com/request'

    payload = {
        'zone':'gemmaresearch',
        'url':f'{base_url}?q={quote_plus(query)}&brd_json=1',
        'format':'raw',
    }

    full_response = make_api_request(url,json=payload)
    if not full_response:
        return None

    extracted_data ={
        'knowledge':full_response.get('knowledge',{}),
        'organic':full_response.get('organic',[]),
    }

    return extracted_data

def trigger_and_download_snapshot(trigger_url,params,data,operation_name='operation'):
    result = make_api_request(trigger_url,params=params,json=data)
    print(result)

    if not result:
        return None

    snapshot_id = result.get('snapshot_id')
    if not snapshot_id:
        return None

    if not snapshot_status(snapshot_id):
        return None

    raw_data = download_snapshot(snapshot_id)
    return raw_data






def reddit_search_api(keyword,date='All time', sort_by='Hot',num_of_posts=1):
    trigger_url = 'https://api.brightdata.com/datasets/v3/trigger'

    params = {
        'dataset_id':'gd_lvz8ah06191smkebj4',
        'include_errors':'true',
        'type':'discover_new',
        "discover_by": "keyword",

    }

    data = [{
        'keyword': keyword,
        'date': date,
        'sort_by': sort_by,
        'num_of_posts': num_of_posts,
    }]

    raw_data = trigger_and_download_snapshot(
        trigger_url,params,data,operation_name= 'reddit'
    )

    if not raw_data:
        return None

    parsed_data = []
    for post in raw_data:
        parsed_post = {
            'title':post.get('title'),
            'url':post.get('url'),
        }
        parsed_data.append(parsed_post)

    return {'parsed_posts': parsed_data,'total_found':len(parsed_data)}


def reddit_post_retrieval(urls,days_back=10,load_all_replies=False,comment_limit=''):
    if not urls:
        return None

    trigger_url = 'https://api.brightdata.com/datasets/v3/trigger'
    params = {
        'dataset_id':'gd_mgnh0p8w16o65lmhp',
        'include_errors':'true',

    }

    data = [
        {
            'url': url,
            'days_back':days_back,
            'load_all_replies':load_all_replies,
            'comment_limit':comment_limit,
        }

        for url in urls
    ]

    raw_data = trigger_and_download_snapshot(
        trigger_url,params,data,operation_name= 'reddit comments'
    )
    if not raw_data:
        return None

    parsed_comments = []
    for comment in raw_data:
        parsed_comment = {
            'comment_id':comment.get('comment_id'),
            'content':comment.get('comment'),
            'date': comment.get('date_posted'),
        }

        parsed_comments.append(parsed_comment)


    return {'comments':parsed_comments,'total_retrieved':len(parsed_comments)}
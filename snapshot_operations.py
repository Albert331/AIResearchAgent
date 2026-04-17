import os
import time
import requests
from dotenv import load_dotenv
from typing import List,Dict,Optional,Any

load_dotenv()

def snapshot_status(snapshot_id:str,max_attempts: int = 50,delay: int = 5) -> bool:
    api_key = os.getenv('BRIGHT_DATA_API')
    progress_url = f'https://api.brightdata.com/datasets/v3/progress/{snapshot_id}'
    headers = {'Authorization': f'Bearer {api_key}'}

    for attempt in range(max_attempts):
        try:
            print(f"checking reddit snapshot progress | attempt {attempt+1} out of {max_attempts}")
            response = requests.get(progress_url,headers=headers)
            response.raise_for_status()

            progress_data = response.json()
            status = progress_data.get('status')

            if status == 'ready':
                print('snapshot aqquired ')
                return True
            elif status=='running':
                print('snapshot waiting for the data')
                time.sleep(delay)
            else:
                print(f'idk what this is : {status}')
                time.sleep(delay)

        except Exception as e:
            print(f'ERROR ERROR ERROR\n{e}')
            time.sleep(delay)

    print(f'too much time spend waiting. i go.')
    return False


def download_snapshot(snapshot_id:str,format: str ='json') -> Optional[List[Dict[Any,Any]]]:
    api_key = os.getenv('BRIGHT_DATA_API')
    progress_url = f'https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={format}'
    headers = {'Authorization': f'Bearer {api_key}'}

    try:
        print('downloading the snapshot')
        response = requests.get(progress_url,headers=headers)
        response.raise_for_status()

        data = response.json()
        print("data aqquired we ball")
        return data
    except Exception as e:
        print(f'ERROR ERROR ERROR\n{e}')
        return None

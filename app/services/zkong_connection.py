from config import config
conf = config['development']

import os
import json
import requests
import mimetypes

BEARER_TOKEN = conf.BEARER_TOKEN

"""
#######################
API CALLS DAS IMAGENS
#######################
"""

def check_status_code(response):
    if response.status_code == 200:
        print("Requisição bem-sucedida!")
        print(response.json())
    else:
        print(f"Falha na requisição. Status: {response.status_code}")
        print(response.text)

def get_items_frombump(label_id: list=[]):  # Removed content_id parameter
    url = 'https://esl-eu.zkong.com/lcd/content/list?pageNum=1&pageSize=10'
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'content-type': 'application/json;charset=UTF-8',
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }

    data = {
        "width": "",
        "labelIds": label_id,
        "name": "",
        "merchantId": 1741766483922,  # Updated merchantId
        "storeId": 0
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    #print(json.dumps(response.json(), indent=4))
    return response.json()

def upload_item_tobump(file_path:str):
    url = 'https://esl-eu.zkong.com/lcd/content/uploadVideo?parentId=0&isSystem=false'  # Updated endpoint
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }

    mime_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, mime_type)}
        response = requests.post(url, headers=headers, files=files)
    check_status_code(response)

def delete_item_frombump(item_id:int):
    url = f'https://esl-eu.zkong.com/lcd/content/delete?id={item_id}'
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }
    response = requests.delete(url, headers=headers)
    check_status_code(response)

# DEF PARA LISTA GERENCIAMENTO


def tag_entity_atbump(item_type:int, item_id:int, tag_id:int):
    url = 'https://esl-eu.zkong.com/lcd/label/labelEntity'
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'content-type': 'application/json;charset=UTF-8',
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }
    data = {
        "type": item_type,
        "entityIds": [item_id],
        "labelIds": [tag_id]
    }
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def criar_tag_pai(tag_name:str, tag_pid:int):
    url = 'https://esl-eu.zkong.com/lcd/label/saveOrUpdate'
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'content-type': 'application/json;charset=UTF-8',
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }
    data = {
        "name": tag_name,
        "pid": tag_pid,
        "id": None
    }
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def delete_tag(tag_id:int):
    url = f'https://esl-eu.zkong.com/lcd/label/delete?id={tag_id}'
    headers = {
        'authority': 'esl-eu.zkong.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'authorization': BEARER_TOKEN,
        'language': 'en',
        'origin': 'https://esl-eu.zkong.com',
        'referer': 'https://esl-eu.zkong.com/'
    }
    response = requests.post(url, headers=headers)
    check_status_code(response)


"""
#######################
API CALLS DE PUBLICAÇÃO
#######################
"""

def list_campaigns():
    url = 'https://esl-eu.zkong.com/lcd/publication/list?pageNum=1&pageSize=10'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Authorization': BEARER_TOKEN,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Language': 'en',
        'Origin': 'https://esl-eu.zkong.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    data = {
        "isDraft": 1,
        "storeId": 1741922345748,
        "status": None,
        "auditStatus": None,
        "startDate": "2025-3-8 00:00:00",
        "endDate": "2025-3-14 23:59:59",
        "expired": 0
    }
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def create_campaign(name_campaing:str, mp4_id:int, mp4_name:str, mp4_url:str, mp4_thumbnailUrl:str, time_seconds:int):
    url = 'https://esl-eu.zkong.com/lcd/publication/save'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Authorization': BEARER_TOKEN,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Language': 'en',
        'Origin': 'https://esl-eu.zkong.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    data = {
        "merchantId": 1741766483922,
        "agencyId": 1558577702698,
        "storeId": 1741922345748,
        "isDraft": 1,
        "name": name_campaing,
        "audioSettings": [],
        "defaultStoreList": [{"storeId": 1741922345748, "storeName": "BumpMedia"}],
        "displaySettingVos": [
            {
                "content": {
                    "id": mp4_id,
                    "parentId": 0,
                    "contentType": 1,
                    "name": mp4_name,
                    "agencyId": 1558577702698,
                    "merchantId": 1741766483922,
                    "storeId": 0,
                    "createdTime": 1741926727000,
                    "updatedTime": 1741926727000,
                    "description": None,
                    "url": mp4_url,
                    "timeLength": 9,
                    "width": 1920,
                    "height": 158,
                    "size": 95527,
                    "contentCount": 1,
                    "thumbnailUrl": mp4_thumbnailUrl,
                    "auditStatus": 2,
                    "createUserId": 8357,
                    "parent": None,
                    "eslUsed": 0,
                    "publishStatus": None
                },
                "showTimeInSecond": time_seconds,
                "type": 1
            }
        ],
        "publicationScope": 1,
        "publicationTargets": [
            {
                "storeVo": {"storeId": 1741922345748, "storeName": "BumpMedia"},
                "targetDetails": []
            }
        ],
        "playTimeRule": {"type": 4}
    }
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def update_campaign(campaign_id):
    url = 'https://esl-eu.zkong.com/lcd/publication/save'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Authorization': BEARER_TOKEN,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Language': 'en',
        'Origin': 'https://esl-eu.zkong.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    data = {
        "id": campaign_id,
        "merchantId": 1741766483922,
        "agencyId": 1558577702698,
        "storeId": 1741922345748,
        "isDraft": 1,
        "name": "teste1diogo",
        "audioSettings": [],
        "defaultStoreList": [{"storeId": 1741922345748, "storeName": "BumpMedia", "timeZone": None}],
        "displaySettingVos": [
            {
                "type": 1,
                "layout": None,
                "content": {
                    "id": 5493,
                    "parentId": 0,
                    "contentType": 1,
                    "name": "slogan_animado2025031401312334.mp4",
                    "agencyId": 1558577702698,
                    "merchantId": 1741766483922,
                    "storeId": 0,
                    "createdTime": 1741926803000,
                    "updatedTime": 1741926803000,
                    "description": None,
                    "url": "group1/M00/31/96/CgAAXWfTsZOACRuuAAFv1xAR2HQ678.mp4",
                    #"compressUrl": "group1/M00/31/96/CgAAXWfTsZSAJd27AAXokj_T5Hg513.mp4",
                    "timeLength": 8,
                    "width": 1920,
                    "height": 158,
                    "size": 94167,
                    "contentCount": 1,
                    "thumbnailUrl": "group1/M00/31/96/CgAAXWfTsZOAAKmaAAAFApxnHn8323.jpg",
                    "auditStatus": 2,
                    "createUserId": 8357,
                    "parent": None,
                    "eslUsed": 0,
                    "publishStatus": None
                },
                "showTimeInSecond": 9994
            }
        ],
        "publicationScope": 1,
        "publicationTargets": [
            {
                "storeVo": {"storeId": 1741922345748, "storeName": "BumpMedia", "externalStoreId": None, "merchantId": 1741766483922, "timeZone": None},
                "targetDetails": [{"targetCode": "1741922345748", "detail": None}]
            }
        ],
        "playTimeRule": {
            "type": 2,
            "startDate": "2025-03-14",
            "endDate": "2025-03-21",
            "playTimes": [{"startTime": "17:00", "endTime": "18:59"}]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def delete_campaign(campaign_id):
    url = 'https://esl-eu.zkong.com/lcd/publication/batchDelete'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Authorization': BEARER_TOKEN,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Language': 'en',
        'Origin': 'https://esl-eu.zkong.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    data = [campaign_id]
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)

def delete_multiple_campaigns(campaign_ids):
    url = 'https://esl-eu.zkong.com/lcd/publication/batchDelete'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Authorization': BEARER_TOKEN,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Language': 'en',
        'Origin': 'https://esl-eu.zkong.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    data = campaign_ids
    response = requests.post(url, headers=headers, json=data)
    check_status_code(response)


def get_or_upload_to_publish(file_way: str):
    response_dict = get_items_frombump()
    file_name = os.path.basename(file_way)
    mp4_info = ["","","",""]

    for item in response_dict['data']['list']:
        if item['name'] == file_name:
            mp4_info[0]= item['id']
            mp4_info[1]= file_name
            mp4_info[2]= item['url']
            mp4_info[3]= item['thumbnailUrl']
            create_campaign("teste5diogo", mp4_info[0], mp4_info[1], mp4_info[2], mp4_info[3], 60)
            return "success"

    upload_item_tobump(file_way)
    response_dict = get_items_frombump()
    print(response_dict)
    
    for item in response_dict['data']['list']:
        if item['name'] == file_name:
            mp4_info[0]= item['id']
            mp4_info[1]= file_name
            mp4_info[2]= item['url']
            mp4_info[3]= item['thumbnailUrl']
            create_campaign("teste5diogo!", mp4_info[0], mp4_info[1], mp4_info[2], mp4_info[3], 60)
            return "success"
    



if __name__ == "__main__":
    # lógica:
    # fazer um get, verificar o arquivo
    # caso já online fazer o publish
    # caso não online fazer upload, fazer get, fazer publish
    pass


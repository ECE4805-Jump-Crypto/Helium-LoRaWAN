import src.utils as utils
import requests 
import sys
payload = {
    "hotspotIds": [
        "11qnNraUGFErgjjNnk7QPHBvL7zCr7kcBWPM33hN1eEWrEvzBSP"
    ]
}


headers = {
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}


response = requests.post('https://etl.hotspotty.org/api/v1/hotspots/history/summary-v4-lean/', headers=headers, json=payload)
print(response.status_code)
print(response.text)
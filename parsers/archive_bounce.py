# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time
from raven import Client

client = Client(
'https://aee9ceb609b549fe8a85339e69c74150:8604fd36d8b04fbd9a70a81bdada5cdf@sentry.io/1223891')




s3A =  "gab1DoriNh68SrP6:HGF7XXfbz73ThYkF"

def download_via_archive(url):
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'LOW %s' %s3A
    }

    data = 'url=%s/&if_not_archived_within=1d&capture_outlinks=0' % url

    req = requests.post('https://web.archive.org/save', headers=headers, data=data, verify=False)


    result = req.json()
    job_id = result['job_id'];

    original_url = url
    done = False
    while done == False:
        time.sleep(2)
        statusReq = requests.get('https://web.archive.org/save/status/%s' % job_id, headers=headers, verify=False)
        statusData = statusReq.json()
        status = statusData["status"]
        original_url = statusData["original_url"]

        if status == "success" :
            done = True

        if status == "error":
            print("job failed " + statusData["message"]);
            return false
        
        time.sleep(2)
        
    
  
    done = False
    while done == False:
        time.sleep(2)
        urlCheck = requests.get('https://archive.org/wayback/available?url=%s' % original_url, headers=headers, verify=False)
        availableData = urlCheck.json()
        if availableData["archived_snapshots"]:
            snapshot = availableData["archived_snapshots"]["closest"]
            newUrl = snapshot["url"]
            return newUrl
        else: 
            time.sleep(2)


 

 

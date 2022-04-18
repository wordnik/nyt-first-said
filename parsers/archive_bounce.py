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
    job_id = result.get('job_id');

    original_url = url
    done = job_id == None
    if done:
        print(result)
    while done == False:
        time.sleep(2)
        statusReq = requests.get('https://web.archive.org/save/status/%s' % job_id, headers=headers, verify=False)
        statusData = statusReq.json()
        status = statusData["status"]
  
        if status == "success" :
            original_url = statusData["original_url"]

            done = True

        if status == "error":
            print("job failed " + statusData["message"]);
            print(statusData)
            time.sleep(30)
            return download_via_archive(url)
        
        time.sleep(2)
        
    
  
    i= 0;
    while i < 5:
        i+=1
        time.sleep(2)
        urlCheck = requests.get('https://archive.org/wayback/available?url=%s' % original_url, headers=headers, verify=False)
        availableData = urlCheck.json()
        print(availableData)

        if availableData["archived_snapshots"]:
            snapshot = availableData["archived_snapshots"]["closest"]
            newUrl = snapshot["url"]
            return newUrl
        else: 
            time.sleep(6)

    time.sleep(20)            
    return download_via_archive(url)


 

 

#!/usr/bin/env python3
import os
#import sys

import requests
from bs4 import BeautifulSoup
import lxml
import wget

#env_path:str = os.getenv('PATH')
#uid:int = os.getuid()

url = "https://www.thunderbird.net/zh-TW/"
result = requests.get(url)
soup = BeautifulSoup(result.text,'lxml')
download_links = set()
hypertag = soup.select('a.matomo-track-download')
for e in hypertag:
    # print("linux64" in e['href'])
    if "os=linux64" in e['href'] :
        print(e['href'])
        download_links.add(e['href'])
print(download_links)
if len(download_links) == 1: 
    for i in download_links:
        print(i)
    # ret = os.popen('wget ' + i)
    # print(ret)
    target_link = i[i.find('thunderbird-'):].replace('SSL&os=','').replace('&lang=','-')+'.tar.bz2'
    print("target " + target_link)
    wget.download(i, target_link)

else:
    print('There are multiple download links...\n Please check!\n')

if os.path.exists(target_link):
    
    os.system("sudo tar jxvf {}".format(target_link))

    if os.path.exists("thunderbird"):
        target_dir = input("Please input the directory where the folder move >> [default : /opt/ ]")
        if target_dir=="" : target_dir = "/opt/"
        os.system("sudo rm -fr {}thunderbird".format(target_dir))
        os.system("sudo mv thunderbird {}".format(target_dir))
    else:
        print("Woops! there might be got some problem of the compressed package")
else:
    print("No target file downloaded! Please check on the official website.")

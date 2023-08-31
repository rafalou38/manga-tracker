import requests
from pyquery import PyQuery as pq
from tinydb import TinyDB, Query
from time import sleep
import random
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cookie": "suggestedService=comic; cpg_shown_cnt=1; cpg_shown=true",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers",
}


def fetchNaverProject(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching a naver project:", response.text)
        return

    id = re.search(r"\d+", url)[0]
    q = pq(response.text)
    cnt = int(q(".end_total_episode>strong").text())
    title = q(".end_head>h2").text()
    img_src = q(".pic_area>img").attr("src")

    return [id, title, img_src, cnt]

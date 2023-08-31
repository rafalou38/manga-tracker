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
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers",
}


def fetchKuaikanmanhuaProject(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching a Kuaikanmanhua project:", response.text)
        return

    q = pq(response.text)
    cnt = q("div.topic-episode div.detail:last-of-type")[0].text
    cnt = re.search(r"\d+", cnt)[0]
    cnt = int(cnt)
    title = q("h3.title").text()
    img_src = q("img.img").attr("src")

    return [re.search(r"\d+", url)[0], title, img_src, cnt]

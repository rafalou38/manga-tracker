from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_NEW_URL")
assert WEBHOOK_URL

import requests
from bs4 import BeautifulSoup
from time import sleep
import random
import re
from main import domains
import pickle

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    # "TE": "trailers",
}
KKM = "https://www.kuaikanmanhua.com/tag/0?region=1&pays=0&state=0&sort=3&page=1"
NAVER = "https://comic.naver.com/api/webtoon/titlelist/new?order=update"
NAVER_COMICS = "https://series.naver.com/comic/recentList.series"


try:
    with open("oldMangas.pkl", "rb") as f:
        mangasIds = pickle.load(f)
except:
    mangasIds = set()


def save():
    with open("oldMangas.pkl", "wb") as f:
        pickle.dump(mangasIds, f)


def publish(domain, id, url, title, img):
    globalId = domain + "-" + str(id)
    if globalId not in mangasIds:
        print(
            f"\033[34;1;4m{domain}\033[24m: \033[32m\033[22;32m nouveau manga: {title}\033[0m"
        )

        r = requests.post(
            WEBHOOK_URL,
            json={
                "username": domain,
                "avatar_url": domains[domain][1],
                "embeds": [
                    {
                        "url": url,
                        "title": title,
                        "image": {"url": img},
                        "color": 5763719,
                    }
                ],
            },
        )
        if r.status_code != 200:
            sleep(40)
            return

        mangasIds.add(globalId)
        sleep(2)


def newNaver():
    response = requests.get(NAVER, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching new Kuaikanmanhua projects:", response.text)
        return

    data = response.json()

    for e in data["titleList"]:
        id = e["titleId"]
        title = e["titleName"]
        img_src = e["thumbnailUrl"]
        publish(
            "naver",
            id,
            f"https://comic.naver.com/webtoon/list?titleId=814362{id}",
            title,
            img_src,
        )


def newNaverComic():
    response = requests.get(NAVER_COMICS, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching new Kuaikanmanhua projects:", response.text)
        return

    html = response.text
    soup = BeautifulSoup(html, features="lxml")

    elems = soup.select("ul.lst_thum li")
    for e in elems:
        a = e.find("a")
        url = a.attrs["href"]
        title = a.attrs["title"]
        id = str(url.split("=")[-1])

        age = e.select_one(".n19")
        if age:
            continue

        img_src = e.select_one("img").attrs["src"]

        publish(
            "naver-comics",
            id,
            f"https://series.naver.com/comic/detail.series?productNo={id}",
            title,
            img_src,
        )


def newKKM():
    response = requests.get(KKM, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching new Kuaikanmanhua projects:", response.text)
        return

    html = response.text

    soup = BeautifulSoup(html, features="lxml")

    elems = soup.select("div.ItemSpecial")
    for e in elems:
        url = e.find("a").attrs["href"]
        id = str(url.split("/")[-1])

        title = e.select_one(".itemTitle").getText()
        img_src = re.search(r'"([\w:\\.-]+?)"[\s,]+?' + id, html)[1]
        img_src = bytes(img_src, "utf-8").decode("unicode_escape")
        publish(
            "kuaikanmanhua",
            id,
            f"https://www.kuaikanmanhua.com/web/topic/{id}/",
            title,
            img_src,
        )


def checkWhatsNew():
    print("checking for new projects")
    newNaver()
    print("Naver OK")
    newKKM()
    print("KKM OK")
    newNaverComic()
    print("Naver comics OK")
    save()

from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
assert WEBHOOK_URL

import requests
from pyquery import PyQuery as pq
from tinydb import TinyDB, Query
from time import sleep
import random
from projects import reloadProjects
import re

from naver import fetchNaverProject
from kakao import fetchKakaoProject
from kuaikanmanhua import fetchKuaikanmanhuaProject
from ridibooks import fetchRidibooksProject

db = TinyDB("db.json")

DOMAIN_REGEX = r"(https?:\/\/[\w.]*?)(\w+)(\.\w+\/)"


domains = {
    "kakao": [
        fetchKakaoProject,
        "https://page.kakao.com/public/favicon/ico_web_square_192.png",
    ],
    "naver": [
        fetchNaverProject,
        "https://ssl.pstatic.net/static/nstore/series_favicon_152.ico",
    ],
    "kuaikanmanhua": [
        fetchKuaikanmanhuaProject,
        "https://static3w.kuaikanmanhua.com/_nuxt/static-kkfront-pc/image/logo.f38006f.png",
    ],
    "ridibooks": [
        fetchRidibooksProject,
        "https://static.ridicdn.net/books-backend/p/8cd996/books/dist/favicon/favicon-256x256.png",
    ],
}


def post_chapter(domain, title, url, img, old_chapter, new_chapter):
    for i in range(old_chapter + 1, new_chapter + 1):
        r = requests.post(
            WEBHOOK_URL,
            json={
                "username": domain,
                "avatar_url": domains[domain][1],
                "embeds": [
                    {
                        "url": url,
                        "title": title,
                        "description": f"Nouveau chapitre: **{i}**",
                        "thumbnail": {"url": re.sub("^\/\/", "https://", img)},
                        "color": 5763719,
                    }
                ],
            },
        )
    r.raise_for_status()


def fetchProject(url):
    fetchFn = lambda *_: print(
        f"\033[31mErreur: url non supportée: \033[1m{url}\033[0m]"
    )
    domain = re.match(DOMAIN_REGEX, url)[2]

    print(domain + " -> ", end="", flush=True)

    try:
        [id, title, img_src, cnt] = domains[domain][0](url)
        id = domain + "-" + str(id)
    except Exception as e:
        print(f"\033[31mErreur: impossible de verifier: \033[1m{url}\033[0m")
        raise e

    query = db.search(Query()["manga-id"] == id)
    if query:
        doc = query[0]
    else:
        doc = {"manga-id": id, "title": title, "cnt": cnt}
    if doc["cnt"] < cnt:
        new = cnt - doc["cnt"]
        print(
            f"\033[34;1;4m{title}\033[24m: \033[32m{new}\033[22;32m nouveau chapitre{ 's' if new != 1 else '' } \033[0m"
        )
        post_chapter(domain, title, url, img_src, doc["cnt"], cnt)
        doc["cnt"] = cnt
    else:
        print(
            f"\033[34;1;4m{title}\033[24m: \033[22;97m Aucun nouveau chapitre \033[0m"
        )

    db.upsert(doc, Query()["manga-id"] == id)


projects = []
while True:
    # Attendre entre 5m et 1h
    projects = reloadProjects()

    for i, url in enumerate(projects):
        print(i + 1, "/", len(projects), end=" ", flush=True)
        fetchProject(url)
        sleep(60 * random.random() * 7 + 2)

    break

# print(fetchKuaikanmanhuaProject("https://www.kuaikanmanhua.com/web/topic/11045/"))

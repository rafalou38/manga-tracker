from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
assert WEBHOOK_URL
WEBHOOK_TRAD_COMIC = os.getenv("WEBHOOK_TRAD_COMIC")
assert WEBHOOK_TRAD_COMIC
WEBHOOK_TRAD_NOVEL = os.getenv("WEBHOOK_TRAD_NOVEL")
assert WEBHOOK_TRAD_NOVEL

from multiprocessing import Process
import requests
from pyquery import PyQuery as pq
from tinydb import TinyDB, Query
from time import sleep
import random
import re

from projects import reloadProjects, Project
from naver import fetchNaverProject
from kakao import fetchKakaoProject
from kuaikanmanhua import fetchKuaikanmanhuaProject
from ridibooks import fetchRidibooksProject
from perf import fetchPerf
import new

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
    "naver-comics": [
        fetchNaverProject,
        "https://ssl.pstatic.net/static/comic/images/og_tag_v2.png",
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


def post_chapter_trad(project: Project, title, img_src, old_cnt, new_cnt):
    for i in range(old_cnt + 1, new_cnt + 1):
        ping = ""
        if project.role:
            ping = f"<@&{project.role}>"
        r = requests.post(
            WEBHOOK_TRAD_COMIC if project.type == "comic" else WEBHOOK_TRAD_NOVEL,
            json={
                "username": "Sorties Perf",
                "avatar_url": "https://perf-scan.fr/icon.png",
                "content": f"""
<:nkmoney:967083636107145218> <@&1151571404546904104> {ping}
🫧  CHAPITRE {i}
<a:PinkFlame:1133669310875848804> {title}
<a:bunwaking:761828350867800065> https://perf-scan.fr/series/martial-peak/chapitre-{i}
""",
            },
        )
    r.raise_for_status()


def fetchProject(db, url):
    domain = re.match(DOMAIN_REGEX, url)[2]

    # print(domain + " -> ", end="", flush=True)

    try:
        domainData = domains[domain]
        if domainData:
            [id, title, img_src, cnt] = domainData[0](url)
            id = domain + "-" + str(id)
        else:
            return
    except Exception as e:
        print(
            domain + " -> ",
            f"\033[31mErreur: impossible de verifier: \033[1m{url}\033[0m",
        )
        raise e

    query = db.search(Query()["manga-id"] == id)
    if query:
        doc = query[0]
    else:
        doc = {"manga-id": id, "title": title, "cnt": cnt}
    if doc["cnt"] < cnt:
        new = cnt - doc["cnt"]
        print(
            "[RAW]",
            domain + " -> ",
            f"\033[34;1;4m{title}\033[24m: \033[32m{new}\033[22;32m nouveau chapitre{ 's' if new != 1 else '' } \033[0m",
        )
        post_chapter(domain, title, url, img_src, doc["cnt"], cnt)
        doc["cnt"] = cnt
    else:
        print(
            "[RAW]",
            domain + " -> ",
            f"\033[34;1;4m{title}\033[24m: \033[22;97m Aucun nouveau chapitre \033[0m",
        )

    db.upsert(doc, Query()["manga-id"] == id)


def checkRaw():
    db = TinyDB("db.json")

    while True:
        print(">> Start checking raw updates")
        projects = reloadProjects()
        for i, project in enumerate(projects):
            if project.raw_url != "":
                # print("[RAW]: ", i + 1, "/", len(projects), end=" ", flush=True)
                fetchProject(db, project.raw_url)
                sleep(60 * random.random() + 2)
        print("<< Finished checking raw updates")
        sleep(60 * random.random() * 60 + 20)


def checkTrad():
    db = TinyDB("db.json")
    while True:
        projects = reloadProjects()
        print(">> [TRAD] Checking trad updates")
        for i, project in enumerate(projects):
            if project.trad_url != "":
                # print("[TRAD]", i + 1, "/", len(projects), end=" ", flush=True)
                [id, title, img_src, cnt] = fetchPerf(project.trad_url)
                id = "perf-" + str(id)

                query = db.search(Query()["manga-id"] == id)
                if query:
                    doc = query[0]
                else:
                    doc = {"manga-id": id, "title": title, "cnt": cnt}
                if doc["cnt"] < cnt:
                    new = cnt - doc["cnt"]
                    print(
                        f"[TRAD] \033[34;1;4m{title}\033[24m: \033[32m{new}\033[22;32m nouveau chapitre{ 's' if new != 1 else '' } \033[0m"
                    )
                    post_chapter_trad(project, title, img_src, doc["cnt"], cnt)
                    doc["cnt"] = cnt
                else:
                    print(
                        f"[TRAD] \033[34;1;4m{title}\033[24m: \033[22;97m Aucun nouveau chapitre \033[0m"
                    )

                db.upsert(doc, Query()["manga-id"] == id)

        print(">> [TRAD] Done")
        sleep(60 * random.random() * 5)


def hourly():
    while True:
        new.checkWhatsNew()
        sleep(60 * random.random() * 60)


if __name__ == "__main__":
    t_raw = Process(target=checkRaw)
    t_raw.start()

    t_hourly = Process(target=hourly)
    t_hourly.start()

    t_trad = Process(target=checkTrad)
    t_trad.start()

    t_trad.join()

# print(fetchKuaikanmanhuaProject("https://www.kuaikanmanhua.com/web/topic/11045/"))

import requests
from bs4 import BeautifulSoup
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


def fetchRidibooksProject(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("There was an error fetching a ridibooks project:", response.text)
        return

    soup = BeautifulSoup(response.text, features="lxml")
    chapters = soup.select(".js_compact_book_list>li")
    cnt = len([*chapters])
    title = soup.select_one("h1.info_title_wrap").text
    img_src = soup.select_one(".header_thumbnail_wrap img.thumbnail ").attrs["src"]

    return [
        int(re.search(r"\d+", url)[0]),
        title,
        img_src.replace("//", "https://"),
        cnt,
    ]

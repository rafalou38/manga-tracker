import requests
from pyquery import PyQuery as pq
from tinydb import TinyDB, Query
from time import sleep
from bs4 import BeautifulSoup
import random
import re


def fetchPerf(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("There was an error fetching a perf project:", response.text)
        return

    soup = BeautifulSoup(response.text, features="lxml")

    # cntLabel = soup.select_one("span.p-4:nth-child(2)")
    chapters = soup.select(".grid ul a")
    latest = 0
    for c in chapters:
        n = int(re.search(r"chapitre-?(\d+)", c.attrs["href"])[1])
        latest = max(latest, n)

    # cnt = re.search(r"\d+", cntLabel.text)[0]
    title = soup.find("h1").text
    img = "https://perf-scan.fr" + soup.select_one("img.w-full").attrs["src"]

    slug = re.search(r"[a-z\-\d]+(?=\/?$)", url)[0]

    # chapters = soup.select("[role=\"tabpanel\"] a")

    return [slug, title, img, latest]

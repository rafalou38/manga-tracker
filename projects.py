from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")
assert SHEET_ID

import pandas as pd
import requests
import math
import re


@dataclass
class Project:
    raw_url: str
    trad_url: str
    role: int

    type: str
    """ novel or comic"""


def reloadProjects():
    print("Rechargement des projets")

    r = requests.get(
        f"https://docs.google.com/spreadsheet/ccc?key={SHEET_ID}&output=csv"
    )
    with open("sheet.csv", "wb") as f:
        f.write(r.content)
    df = pd.read_csv("sheet.csv", header=2, usecols=[1, 2, 3, 4, 5, 6, 7])
    # print(df)

    projects: list[Project] = []
    for index, row in df.iterrows():
        # project = {"raw": row.iloc[2], "trad": row.iloc[4], "role": round(row.iloc[5])}

        raw = str(row.iloc[2])
        trad = str(row.iloc[4])
        role = str(row.iloc[5])
        type = str(row.iloc[6])
        if raw == "nan":
            raw = ""
        if trad == "nan":
            trad = ""

        if type != "novel":
            type = "comic"

        if role == "nan" or not re.match(r"^[\d\.]+$", role):
            role = ""
        else:
            role = int(float(role))

        p = Project(raw, trad, role, type)
        # print(p)
        projects.append(p)

    return projects

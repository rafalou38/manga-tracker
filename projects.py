from dotenv import load_dotenv
import os

load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")
assert SHEET_ID

import pandas as pd
import requests


def reloadProjects():
    global projects
    print("Rechargement des projets")

    r = requests.get(
        f"https://docs.google.com/spreadsheet/ccc?key={SHEET_ID}&output=csv"
    )
    with open("sheet.csv", "wb") as f:
        f.write(r.content)
    df = pd.read_csv("sheet.csv", header=2, usecols=[1, 2, 3])
    print(df)
    return df.iloc[:, 2].to_numpy()

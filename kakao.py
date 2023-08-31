import requests
import re


def fetchKakaoProject(url):
    id = re.search(r"\d+", url)[0]
    id = int(id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Accept": "application/graphql+json, application/json",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://page.kakao.com/content/" + str(id),
        "content-type": "application/json",
        "Origin": "https://page.kakao.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    # Get cnt
    json_data = {
        "query": "query contentHomeProductList($after: String, $before: String, $first: Int, $last: Int, $seriesId: Long!, $boughtOnly: Boolean, $sortType: String) {\n  contentHomeProductList(\n    seriesId: $seriesId\n    after: $after\n    before: $before\n    first: $first\n    last: $last\n    boughtOnly: $boughtOnly\n    sortType: $sortType\n  ) {\n    totalCount\n  }\n}",
        "operationName": "contentHomeProductList",
        "variables": {
            "seriesId": id,
            "boughtOnly": False,
            "sortType": "desc",
        },
    }
    response = requests.post(
        "https://page.kakao.com/graphql", headers=headers, json=json_data
    )
    json = response.json()
    cnt = json["data"]["contentHomeProductList"]["totalCount"]

    # Get info
    json_data = {
        "query": """query contentHomeOverview($seriesId: Long!) {
            contentHomeOverview(seriesId: $seriesId) {
                content {
                ...SeriesFragment
                }
            }
            }


            fragment SeriesFragment on Series {
            seriesId
            title
            thumbnail
            }
            """,
        "operationName": "contentHomeOverview",
        "variables": {
            "seriesId": id,
        },
    }
    response = requests.post(
        "https://page.kakao.com/graphql", headers=headers, json=json_data
    )

    json = response.json()
    id = json["data"]["contentHomeOverview"]["content"]["seriesId"]
    title = json["data"]["contentHomeOverview"]["content"]["title"]
    img_src = json["data"]["contentHomeOverview"]["content"]["thumbnail"]

    return [id, title, img_src, cnt]

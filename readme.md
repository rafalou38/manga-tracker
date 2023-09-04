# Manga tracker
THis is a simple python script that fetches a list of manga urls from a google sheet across 3 websites:
-  kakao
-  nave
-  kuaikanmanhua
-  ridibooks

It check for new chapters for every once in a while on each of them.
The new chapter are directly pushed to a discord webhook.

## Config
Create and fill in a `.env` file.
```ini
WEBHOOK_URL=...
SHEET_ID=...
```
import requests
import os

def get_zoho_access_token():
    client_id = os.environ["ZOHO_CLIENT_ID"]
    client_secret = os.environ["ZOHO_CLIENT_SECRET"]
    refresh_token = os.environ["ZOHO_REFRESH_TOKEN"]

    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, params=params)
    data = response.json()
    return data["access_token"]
import os
import logging
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO)

SPOTIFY_USERNAME: Optional[str] = os.getenv("SPOTIFY_USERNAME")
SPOTIFY_PASSWORD: Optional[str] = os.getenv("SPOTIFY_PASSWORD")
GOOGLE_CHROME_BIN: Optional[str] = os.getenv("GOOGLE_CHROME_BIN")
CHROMEDRIVER_PATH: str = os.getenv("CHROMEDRIVER_PATH", "./chromedriver")


logging.info("Starting up Chromium Browser...")
chrome_options = Options()
if GOOGLE_CHROME_BIN:
    chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)

driver.get("https://developer.spotify.com/console/post-playlists/")


# -------------------------- SELECT SCOPES ----------------------------
logging.info("Clicking on Get Token Button...")
get_token_button: WebElement = driver.find_element_by_xpath(
    "//button[text()='Get Token']"
).click()
time.sleep(1)
logging.info("Selecting scopes...")
scopes: List[WebElement] = driver.find_elements_by_class_name("control-indicator")
playlist_modify_public_scope: WebElement = scopes[0].click()
playlist_modify_public_scope = scopes[1].click()
logging.info("Clicking on Request Token Button...")
driver.find_element_by_id("oauthRequestToken").click()
time.sleep(1)
# -------------------------- SELECT SCOPES ----------------------------

# -------------------------- SPOTIFY SIGN IN ---------------------------
logging.info("Signing into Spotify...")
username_field: WebElement = driver.find_element_by_id("login-username")
username_field.send_keys(SPOTIFY_USERNAME)
password_field: WebElement = driver.find_element_by_id("login-password")
password_field.send_keys(SPOTIFY_PASSWORD)
login_button: WebElement = driver.find_element_by_id("login-button").click()
time.sleep(2)
# -------------------------- SPOTIFY SIGN IN ---------------------------

# --------------------- RETRIEVE GENERATED TOKEN -----------------------
logging.info("Getting Shiny New Token...")
oauth_input: WebElement = driver.find_element_by_id("oauth-input")
token: str = oauth_input.get_attribute("value")
logging.info(f"Token Is: {token}")
# --------------------- RETRIEVE GENERATED TOKEN -----------------------

headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
# Get Discover Weekly Playlist Data
dw_playlist_result: requests.Response = requests.get(
    "https://api.spotify.com/v1/search?q=Discover Weekly&type=playlist&limit=1",
    headers=headers,
)
dw_playlist_id: str = dw_playlist_result.json()["playlists"]["items"][0]["id"]

# get all the uris for each track from the Discover Weekly Playlist
dw_uri_response: requests.Response = requests.get(
    f"https://api.spotify.com/v1/playlists/{dw_playlist_id}/tracks?fields=items(track(uri))",
    headers=headers,
)
uri_data: List[Dict[str, Dict[str, str]]] = dw_uri_response.json()["items"]
uri_items: List[str] = []
for uri in uri_data:
    uri_items.append(uri["track"]["uri"])
uris: str = ",".join(uri_items)

start_date: datetime = datetime.now(timezone("US/Eastern"))  # EST timezone
end_date: datetime = start_date + timedelta(days=7)
# Playlist Name in the format of mm/dd-mm/dd with no digit padding (Ex: 1/1-1/7)
name: str = f"{start_date.strftime('%-m/%-d')}-{end_date.strftime('%-m/%-d')}"
# Date string in the form of Month dd - Month dd, YYYY (Ex: Jan 1 - Jan 7, 2020)
date_string: str = f"{start_date.strftime('%b %-d')} - {end_date.strftime('%b %-d, %Y')}"
body: str = f'{{"name": "{name} Weekly Playlist", "description": "Discover Weekly Playlist for {date_string}", "public": false}}'
# creates new private playlist
new_playlist_reponse: requests.Response = requests.post(
    f"https://api.spotify.com/v1/users/{SPOTIFY_USERNAME}/playlists",
    data=body,
    headers=headers,
)
result_data = new_playlist_reponse.json()

# add all tracks from Discover Weekly to New Playlist
new_playlist_id: str = new_playlist_reponse.json()["id"]
requests.post(
    f"https://api.spotify.com/v1/playlists/{new_playlist_id}/tracks?uris={uris}",
    headers=headers,
)

# close the browser session
driver.quit()

playlist_name: str = result_data["name"]
playlist_url: str = result_data["external_urls"]["spotify"]
logging.info(f'"{playlist_name}" available at "{playlist_url}"')

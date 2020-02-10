import os
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

SPOTIFY_USERNAME: Optional[str] = os.getenv("SPOTIFY_USERNAME")
SPOTIFY_PASSWORD: Optional[str] = os.getenv("SPOTIFY_PASSWORD")
GOOGLE_CHROME_BIN: Optional[str] = os.getenv("GOOGLE_CHROME_BIN")
CHROMEDRIVER_PATH: str = os.getenv("CHROMEDRIVER_PATH", "./chromedriver")


print("Starting up Chromium Browser...")
chrome_options = Options()
if GOOGLE_CHROME_BIN:
    chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
try:
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
except Exception as e:
    print(e)
    raise e

driver.get("https://developer.spotify.com/console/post-playlists/")


# -------------------------- SELECT SCOPES ----------------------------
print("Clicking on Get Token Button...")
get_token_button: WebElement = driver.find_element_by_xpath(
    "//button[text()='Get Token']"
).click()
time.sleep(1)
print("Selecting scopes...")
scopes: List[WebElement] = driver.find_elements_by_class_name("control-indicator")
playlist_modify_public_scope: WebElement = scopes[0].click()
playlist_modify_public_scope = scopes[1].click()
driver.find_element_by_id("oauthRequestToken").click()
time.sleep(1)
# -------------------------- SELECT SCOPES ----------------------------

# -------------------------- SPOTIFY SIGN IN ---------------------------
print("Signing into Spotify...")
username_field: WebElement = driver.find_element_by_id("login-username")
username_field.send_keys(SPOTIFY_USERNAME)
password_field: WebElement = driver.find_element_by_id("login-password")
password_field.send_keys(SPOTIFY_PASSWORD)
login_button: WebElement = driver.find_element_by_id("login-button").click()
time.sleep(2)
# -------------------------- SPOTIFY SIGN IN ---------------------------

# --------------------- RETRIEVE GENERATED TOKEN -----------------------
print("Getting Shiny New Token...")
oauth_input: WebElement = driver.find_element_by_id("oauth-input")
token: str = oauth_input.get_attribute("value")
print(f"Token Is: {token}")
# --------------------- RETRIEVE GENERATED TOKEN -----------------------

discover_weekly_playlist_id: str = "37i9dQZEVXcJN8VxgViEXj"

# get all the uris for each track from the Discover Weekly Playlist
discover_weekly_uri_response: requests.Response = requests.get(
    f"https://api.spotify.com/v1/playlists/{discover_weekly_playlist_id}/tracks?fields=items(track(uri))",
    headers={"Authorization": f"Bearer {token}"},
)
uri_data: List[Dict[str, Dict[str, str]]] = discover_weekly_uri_response.json()["items"]
uri_items: List[str] = []
for uri in uri_data:
    uri_items.append(uri["track"]["uri"])
uris: str = ",".join(uri_items)

start_date: datetime = datetime.now(timezone("US/Eastern"))  # EST timezone
end_date: datetime = start_date + timedelta(days=7)
name: str = f"{start_date.strftime('%-m/%-d')}-{end_date.strftime('%-m/%-d')}"
date_string: str = f"{start_date.strftime('%b %-d')} - {end_date.strftime('%b %-d, %Y')}"
body: str = f'{{"name": "{name} Weekly Playlist", "description": "Discover Weekly Playlist for {date_string}", "public": false}}'
# creates new playlist
result: requests.Response = requests.post(
    f"https://api.spotify.com/v1/users/{SPOTIFY_USERNAME}/playlists",
    data=body,
    headers={"Authorization": f"Bearer {token}"},
)
result_data = result.json()

# add all tracks from Discover Weekly to New Playlist
new_playlist_id: str = result.json()["id"]
result = requests.post(
    f"https://api.spotify.com/v1/playlists/{new_playlist_id}/tracks?uris={uris}",
    headers={"Authorization": f"Bearer {token}"},
)

playlist_name = result_data["name"]
playlist_url = result_data["external_urls"]["spotify"]
print(f'"{playlist_name}" available at "{playlist_url}"')

![Spotify Scheduler Banner](./assets/spotify-scheduler-banner.png)

# Spotify Weekly Playlist Scheduler

- Spotify has a Discover Weekly Playlist which has new songs every week. I use it all the time for discovering new music and I also save a lot of these songs to my library to listen to after the week is over.
- My problem was that I either didn't get around to listening to the full playlist within the week or I incorrectly remembered saving songs to my library. Then, after the week was over I lost those songs forever and missed the chance of finding my new favorite song.
- This script (when setup with a scheduler) will automatically create a copy of the Discover Weekly playlist every week so that you don't need to worry about losing your music after the week is done.

# Getting Started (Locally)

1. Clone this repository, e.g.
   ```sh
   git clone https://github.com/VishalRamesh50/spotify-weekly-scheduler.git
   ```
2. Copy `.vscode.example` to `.vscode` to get linting settings (optional)
   ```sh
   cp -r .vscode.example .vscode
   ```
3. Copy `.env.example` to `.env`
   ```sh
   cp .env.example .env
   ```
4. Replace the `SPOTIFY_USERNAME` and `SPOTIFY_PASSWORD` in the `.env` file for the desired user.
5. Install dependencies
   ```sh
   pip3 install -r requirements.txt
   poetry install
   ```
6. Run the program!
   ```sh
   poetry run python main.py
   ```

# Important Steps for Deploying (To Heroku)

1. Add the following buildpacks

   - heroku/python
   - https://github.com/heroku/heroku-buildpack-chromedriver
   - https://github.com/heroku/heroku-buildpack-google-chrome

2. Add these config/environment variables
   - `CHROMEDRIVER_PATH`=/app/.chromedriver/bin/chromedriver
   - `GOOGLE_CHROME_BIN`=/app/.apt/usr/bin/google-chrome
   - `SPOTIFY_USERNAME`=your_spotify_username
   - `SPOTIFY_PASSWORD`=your_spotify_password

Note: This application _does not_ store or send your username and password _anywhere_. However, they are necessary in order to give this application access to read/create your private Spotify playlists. You can learn more about Spotify Authorization Flow [here](https://developer.spotify.com/documentation/general/guides/authorization-guide/). You can learn more about Spotify Authorization Scopes [here](https://developer.spotify.com/documentation/general/guides/scopes/).

3. Add a scheduling extension of your choice and let it run this shell script every Monday:
   ```sh
   poetry install --no-dev && poetry run python main.py
   ```
   What I Use: [Advanced Scheduler](https://elements.heroku.com/addons/advanced-scheduler)

# Getting Started

1. Copy `.vscode.example` to `.vscode` to get linting settings.
   ```sh
   cp .vscode.example .vscode
   ```
2. Copy `.env.example` to `.env`
   ```sh
   cp .env.example .env
   ```
3. Replace the `SPOTIFY_USERNAME` and `SPOTIFY_PASSWORD` in the `.env` file to the desired user.
4. Install dependencies
   ```sh
   pip3 install -r requirements.txt
   poetry install
   ```
5. Run the program!
   ```sh
   poetry run python main.py
   ```

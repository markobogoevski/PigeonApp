# Pigeon Joke Square

Small local Python web app with animated pigeons. Each refresh creates 8-12 pigeons, assigns fixed jokes to all non-love pigeons, and randomly chooses one hidden pair that kisses when clicked.

## Run locally

```bash
python app.py
```

Open `http://localhost:8000`.

## Run with Docker

```bash
docker build -t pigeon-jokes .
docker run --rm -p 8010:8000 -v "$PWD:/app" pigeon-jokes
```

Open `http://localhost:8010`. The bind mount lets the container use your local files. `dev_server.py` restarts the Python server for Python changes, while the page auto-refreshes for HTML/CSS/JS/SVG changes.

## Test

```bash
python -m unittest
```

## Build a Windows installer

The distributable Windows installer is built on Windows. It bundles Python, the local web server, and all static assets, so the receiver does not need Python, Docker, or manual dependency setup.

```powershell
python -m pip install pyinstaller
pyinstaller PigeonJokes.spec --noconfirm --clean
choco install innosetup -y --no-progress
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" "packaging\windows\PigeonJokes.iss"
```

The installer is written to:

```text
installer/PigeonJokesSetup.exe
```

Running the installer launches the app after install. The installed app starts a local server, opens the browser automatically, and shows a small control window with Open App and Quit buttons.

The GitHub Actions workflow at `.github/workflows/windows-installer.yml` can also build `PigeonJokesSetup.exe` on a Windows runner.

## Image Credits

- `static/assets/pigeon-real.png`: Original domestic pigeon photo by Yasunori Yamamoto / iNaturalist, via Wikimedia Commons, licensed under CC BY 4.0: https://commons.wikimedia.org/wiki/File:Columba_livia_domestica_66335414.png
- `static/assets/pigeon-cutout.png`: Local transparent-background cutout derived from the credited source image.

## Audio

- `static/assets/medieval-pigeon-loop.wav`: Local generated 24-second medieval-style loop. Browsers start it after the first user interaction because audible autoplay is blocked by default.
- `static/assets/goofy-pigeon-click.wav`: Local generated click sound for joke pigeons.
- `static/assets/pigeon-kiss-pop.wav`: Local generated kiss sound for the hidden love pair.

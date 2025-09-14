# Neumorphic Music Player

A sleek, modern desktop music player featuring a neumorphic design. Built using HTML, CSS, and JavaScript for the frontend, with a Python Flask backend to scan your local music library, fetch metadata, and serve the web interface.

## Screenshots

<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/89763381-368c-4b28-9aea-41346a501a63" />





## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Metadata:** Mutagen (local tags), The AudioDB API (web enhancement)

## Features

- **Automatic Library Scan:** Scans your system’s default `Music` folder for audio files (`.mp3`, `.m4a`, `.wav`, `.ogg`).
- **Instant Startup & Background Fetching:** Starts immediately by quickly scanning your library. Album art and enhanced metadata are then fetched from The AudioDB API in the background without blocking the UI.
- **Local Album Art Fallback:** If the API doesn't find art, it will try to match songs with images in your local `assets/album art` folder.
- **Full Player Controls:** Play, pause, next, previous, shuffle, and repeat (all/one) modes.
- **Dynamic Playlist:**
    - Real-time search to filter your library by title, artist, or album.
    - Sort your music by title, artist, album, or duration.
- **Modern UI:**
    - Clean, responsive neumorphic style.
    - Light and Dark theme toggle.
    - Volume slider and mute support.

## Getting Started

Follow these instructions to run the player locally.

### Prerequisites

- Python 3.6+
- `pip`
- `git`

### Installation & Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Jonesterw/Neumophic-player.git
    cd Neumophic-player
    ```
2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
3. **Configure API Key (Highly Recommended):**
    - To enable automatic fetching of album art and improved metadata, you need a free API key from The AudioDB.
    - Open the `generate_playlist.py` file.
    - Find the line `THEAUDIODB_API_KEY = "1"` and replace `"1"` with your actual API key.

### Running the Application

1. **Run the server script:**
    ```sh
    python generate_playlist.py
    ```
    - The script will prompt you to confirm your music folder’s location, scan your music, generate the playlist, and start the local web server.
    - You can specify any folder path, or use the default.
    - Keep the terminal window open while using the player.

2. **Open the player:**
    - In your web browser, navigate to:  
      http://127.0.0.1:5000

Your music player should now be running!

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.


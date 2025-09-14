# Neumorphic Music Player

A sleek, modern desktop music player featuring a neumorphic design. Built using HTML, CSS, and JavaScript for the frontend, with a Python Flask backend to scan your local music library, fetch metadata, and serve the web interface.

## Screenshots

<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/e0e513f8-b7f1-4094-b144-56bd10e9c46f" />
<img width="960" height="540" alt="image" src="https://github.com/user-attachments/assets/0a851c00-bb89-440e-ad4f-de1ba0181f07" />



## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Metadata:** Mutagen (local tags), The AudioDB API (web enhancement)

## Features

- **Automatic Library Scan:** Scans your system’s default `Music` folder for audio files (`.mp3`, `.m4a`, `.wav`, `.ogg`).
- **Metadata Enhancement:** Enriches your library with artist, album, and high-quality album art from The AudioDB API.
- **Local Album Art:** Falls back to image files in the `assets/album art` folder if no API art is found.
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
3. **(Optional) Configure API Key:**
    - For the best metadata results, obtain a free API key from The AudioDB.
    - Open `generate_playlist.py` and set your key in the `THEAUDIODB_API_KEY` variable.

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


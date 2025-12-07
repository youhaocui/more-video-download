## 💻 通用媒體下載器 (Universal Media Downloader) 資訊總結

該總結是基於您提供的 Python 腳本 (`youtube_spotify_downloader.py`) 所需的環境依賴和功能說明。

### ✨ 程式核心特色

* **跨站點下載能力**：利用強大的 **yt-dlp** 後端，支援從 YouTube、Twitch 等數百個網站下載視訊與音訊內容。
* **Spotify 整合**：專門處理 Spotify 連結，利用 **spotdl** 進行下載，並能自動嵌入歌曲的中繼資料。
* **多媒體格式輸出**：支援多種格式，包括：音訊 (**MP3**, **FLAC** (無損), **AAC**) 及視訊 (**MP4**, **MOV**, **WebM**)。
* **彈性品質選擇**：提供多種品質選項，例如視訊的 FHD/HD 和音訊的最高/高品質設定。
* **GUI 介面與多語言**：採用 **CustomTkinter** 構建圖形介面，支援多達 15 種語言，提供直觀的使用體驗。
* **非阻塞式下載**：下載操作在獨立的**執行緒 (Threading)** 中運行，確保程式介面在執行時不會凍結。
* **打包兼容性**：程式碼針對 PyInstaller 打包（如單一執行檔）進行優化，能正確調用內嵌的外部執行檔。

---

### 🛠️ 必備外部工具清單

為了讓您的程式能夠正常運作，您需要準備以下三個核心外部執行檔，並將它們**放置在程式執行檔所在的同一目錄下**。

1.  **yt-dlp**：核心的網站內容抓取工具。
2.  **FFmpeg**：用於視訊/音訊的轉換、合併與編碼。
3.  **spotdl**：專門處理 Spotify 連結和中繼資料。

---

### 🔗 工具下載與設置指引

#### 1. yt-dlp

* **用途**：多網站內容下載。
* **下載連結**：[https://github.com/yt-dlp/yt-dlp/releases](https://github.com/yt-dlp/yt-dlp/releases)
    * **選擇檔案**：下載 `yt-dlp.exe`,放置在程式目錄中。

#### 2. spotdl

* **用途**：處理 Spotify 連結並下載歌曲。
* **下載連結**：[https://github.com/spotDL/spotify-downloader/releases/tag/v4.4.3](https://github.com/spotDL/spotify-downloader/releases/tag/v4.4.3)
    * **選擇檔案**：下載 `spotdl-4.4.3-win32.exe`。
    * **設置步驟**：將下載的檔案**重新命名**為 `spotdl.exe`,放置在程式目錄中。


#### 3. FFmpeg

* **用途**：格式轉換與編碼處理。
* **下載連結**：[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
    * **選擇檔案**：往下拉選擇`ffmpeg-release-essentials.zip`點擊下載並解壓縮,在資料夾內的 `bin` 資料夾中找到 `ffmpeg.exe`。
    * **設置步驟**：將 `ffmpeg.exe` 提取到程式目錄中。
 

#### 打包說明已放置在`packaging_instructions.txt`,可下載的網站已放在`Downloadable_videos.txt`。


 ---
 
## 💻 Universal Media Downloader Information Summary

This summary is based on the environment dependencies and feature descriptions required by your provided Python script (`youtube_spotify_downloader.py`).

### ✨ Core Program Features

* **Cross-site download capability**: Utilizes the powerful **yt-dlp** backend to support downloading video and audio content from hundreds of websites such as YouTube and Twitch.

* **Spotify integration**: Dedicated to handling Spotify links, using **spotdl** for downloading, and automatically embedding song relay data.

* **Multimedia Output:** Supports multiple formats, including audio (MP3, FLAC (lossless), AAC) and video (MP4, MOV, WebM).

* **Flexible Quality Selection:** Offers various quality options, such as FHD/HD for video and high/high quality settings for audio.

* **GUI Interface and Multilingual Support:** Utilizes a custom Tkinter graphical interface, supporting up to 15 languages ​​for an intuitive user experience.

* **Non-blocking Download:** Download operations run in a separate thread, ensuring the program interface does not freeze during execution.

* **Packaging Compatibility**: The code is optimized for PyInstaller packaging (such as a single executable), ensuring correct calls to embedded external executables.

---

### 🛠️ Essential External Tools List

For your program to function correctly, you need the following three core external executables and place them in the same directory as your program's executable.

1. **yt-dlp**: The core website content scraping tool.

2. **FFmpeg**: Used for video/audio conversion, merging, and encoding.

3. **spotdl**: Specifically handles Spotify links and relay data.

---

### 🔗 Tool Download and Setup Guide

#### 1. yt-dlp

* **Purpose**: Download content from multiple websites.

* **Download Link**: [https://github.com/yt-dlp/yt-dlp/releases](https://github.com/yt-dlp/yt-dlp/releases)

* **Select File**: Download `yt-dlp.exe` and place it in the program directory.

#### 2. spotdl

* **Purpose**: Handle Spotify links and download songs.

* **Download Link**: [https://github.com/spotDL/spotify-downloader/releases/tag/v4.4.3](https://github.com/spotDL/spotify-downloader/releases/tag/v4.4.3)

* **File Selection**: Download `spotdl-4.4.3-win32.exe`.

* **Setup Steps**: Rename the downloaded file to `spotdl.exe` and place it in the program directory.

#### 3. FFmpeg

* **Purpose**: Format conversion and encoding processing.

* **Download Link**: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

* **File Selection**: Scroll down and select `ffmpeg-release-essentials.zip`, click download and extract. Locate `ffmpeg.exe` in the `bin` folder within the `ffmpeg.zip` folder.

* **Setup Steps**: Extract `ffmpeg.exe` to the program directory.

#### Packaging instructions are located in `packaging_instructions.txt`, and downloadable websites are located in `Downloadable_videos.txt`.

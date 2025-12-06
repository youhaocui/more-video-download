import customtkinter as ctk
import subprocess
import threading
import sys
import os
import re
import locale 
from tkinter import filedialog 
from tkinter import messagebox

# --- 設定與路徑處理 ---
if getattr(sys, 'frozen', False):
    # 當程式被打包成 .exe 時的路徑
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    # 當程式直接運行 Python 腳本時的路徑
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

def get_default_download_path():
    """嘗試獲取使用者的標準「下載」資料夾路徑"""
    # 嘗試標準的用戶家目錄/Downloads
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(download_path):
        # 備用路徑 (Windows 特有環境變量)
        download_path = os.environ.get('USERPROFILE', os.path.expanduser('~'))
        download_path = os.path.join(download_path, 'Downloads')
    # 如果還是找不到，則使用應用程式所在目錄
    return download_path if os.path.exists(download_path) else APPLICATION_PATH

# 支援的格式和 yt-dlp 參數對應 (KEYS MUST REMAIN THE SAME FOR LOGIC)
# 鍵名現在是內部標識符，顯示名稱在 LANG_DATA 中
FORMAT_OPTIONS = {
    'MP3_AUDIO': ['-x', '--audio-format', 'mp3'],
    'FLAC_LOSSLESS': ['-x', '--audio-format', 'flac'],
    'AAC_AUDIO': ['-x', '--audio-format', 'aac'],
    'MP4_VIDEO': ['--recode-video', 'mp4'], 
    'MOV_VIDEO': ['--recode-video', 'mov'],
}

# 視訊畫質選擇
QUALITY_OPTIONS = {
    'BEST_VIDEO': 'bestvideo+bestaudio/best', 
    'FHD_1080P': 'bestvideo[height<=1080]+bestaudio/best',
    'HD_720P': 'bestvideo[height<=720]+bestaudio/best',
}

# 音頻品質選項 (yt-dlp/ffmpeg -q:a 設置)
AUDIO_QUALITY_OPTIONS = {
    'BEST_AUDIO': '0', # 最高品質 (VBR)
    'HIGH_AUDIO': '2', # 高品質 (VBR)
    'MEDIUM_AUDIO': '5', # 中等品質 (CBR)
}

# --- 國際化 (i18n) 資料：已添加選項翻譯 ---
LANG_DATA = {
    'zh_TW': {
        'lang_display': "zh_TW (繁體中文)", 
        'title': "通用媒體下載器", 
        'url_label': "輸入網址 (支援多網站):", 
        'format_label': "選擇輸出格式:", 
        'quality_video_label': "選擇畫質:", 
        'quality_audio_label': "選擇音質:", 
        'path_label': "輸出路徑:", 
        'browse_button': "瀏覽...", 
        'download_button': "🚀 開始下載與轉換", 
        'ready_status': "準備就緒。支援多網站下載。", 
        'error_no_url': "⚠️ 請輸入網址！", 
        'status_downloading_prepare': "正在準備下載命令...", 
        'status_downloading_spotify': "正在處理 Spotify 連結...", 
        'status_downloading_execute': "正在執行下載和轉換...", 
        'status_download_success_spotify': "✅ Spotify 歌曲下載成功！檔案儲存在:", 
        'status_download_success_general': "✅ 網站內容下載與轉換成功！檔案儲存在:", 
        'status_error_exec': "❌ 執行失敗，錯誤碼:", 
        'status_error_not_found': "❌ 錯誤: 找不到 yt-dlp, ffmpeg, 或 spotdl。請檢查同目錄檔案。", 
        'status_error_unexpected': "❌ 發生未預期的錯誤:", 
        'status_path_set': "已設定新的輸出路徑。", 
        'combobox_lang_label': "選擇語言:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (音頻)', 'FLAC_LOSSLESS': 'FLAC (無損)', 'AAC_AUDIO': 'AAC (音頻)', 'MP4_VIDEO': 'MP4 (視訊)', 'MOV_VIDEO': 'MOV (視訊)'},
            'video_qualities': {'BEST_VIDEO': '最高畫質 (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': '最高音質 (Best/VBR)', 'HIGH_AUDIO': '高品質 (High/VBR)', 'MEDIUM_AUDIO': '中等品質 (Medium/CBR)'}
        }
    },
    'zh_CN': {
        'lang_display': "zh_CN (简体中文)", 
        'title': "通用媒体下载器", 
        'url_label': "输入网址 (支持多网站):", 
        'format_label': "选择输出格式:", 
        'quality_video_label': "选择画质:", 
        'quality_audio_label': "选择音质:", 
        'path_label': "输出路径:", 
        'browse_button': "浏览...", 
        'download_button': "🚀 开始下载与转换", 
        'ready_status': "准备就绪。支持多网站下载。", 
        'error_no_url': "⚠️ 请输入网址！", 
        'status_downloading_prepare': "正在准备下载命令...", 
        'status_downloading_spotify': "正在处理 Spotify 链接...", 
        'status_downloading_execute': "正在执行下载和转换...", 
        'status_download_success_spotify': "✅ Spotify 歌曲下载成功！文件存储在:", 
        'status_download_success_general': "✅ 网站内容下载与转换成功！文件存储在:", 
        'status_error_exec': "❌ 执行失败，错误码:", 
        'status_error_not_found': "❌ 错误: 找不到 yt-dlp, ffmpeg, 或 spotdl。请检查同目录文件。", 
        'status_error_unexpected': "❌ 发生未预期的错误:", 
        'status_path_set': "已设置新的输出路径。", 
        'combobox_lang_label': "选择语言:", 
        # 新增的选项翻译
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (音频)', 'FLAC_LOSSLESS': 'FLAC (无损)', 'AAC_AUDIO': 'AAC (音频)', 'MP4_VIDEO': 'MP4 (视频)', 'MOV_VIDEO': 'MOV (视频)'},
            'video_qualities': {'BEST_VIDEO': '最高画质 (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': '最高音质 (Best/VBR)', 'HIGH_AUDIO': '高品质 (High/VBR)', 'MEDIUM_AUDIO': '中等品质 (Medium/CBR)'}
        }
    },
    'en': {
        'lang_display': "en (English)", 
        'title': "Universal Media Downloader", 
        'url_label': "Enter URL (Supports Multi-site):", 
        'format_label': "Select Output Format:", 
        'quality_video_label': "Select Video Quality:", 
        'quality_audio_label': "Select Audio Quality:", 
        'path_label': "Output Path:", 
        'browse_button': "Browse...", 
        'download_button': "🚀 Start Download & Convert", 
        'ready_status': "Ready. Supports multi-site download.", 
        'error_no_url': "⚠️ Please enter a URL!", 
        'status_downloading_prepare': "Preparing download command...", 
        'status_downloading_spotify': "Processing Spotify link...", 
        'status_downloading_execute': "Executing download and conversion...", 
        'status_download_success_spotify': "✅ Spotify song downloaded successfully! File saved to:", 
        'status_download_success_general': "✅ Content downloaded and converted successfully! File saved to:", 
        'status_error_exec': "❌ Execution failed with code:", 
        'status_error_not_found': "❌ ERROR: yt-dlp, ffmpeg, or spotdl not found. Check files in the same directory.", 
        'status_error_unexpected': "❌ An unexpected error occurred:", 
        'status_path_set': "New output path has been set.", 
        'combobox_lang_label': "Select Language:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Lossless)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Highest Quality (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Best Quality (VBR)', 'HIGH_AUDIO': 'High Quality (VBR)', 'MEDIUM_AUDIO': 'Medium Quality (CBR)'}
        }
    },
    'ja': {
        'lang_display': "ja (日本語)", 
        'title': "ユニバーサルメディアダウンローダー", 
        'url_label': "URLを入力 (複数サイト対応):", 
        'format_label': "出力形式を選択:", 
        'quality_video_label': "画質を選択:", 
        'quality_audio_label': "音質を選択:", 
        'path_label': "出力先パス:", 
        'browse_button': "参照...", 
        'download_button': "🚀 ダウンロード開始と変換", 
        'ready_status': "準備完了。多サイトダウンロード対応。", 
        'error_no_url': "⚠️ URLを入力してください！", 
        'status_downloading_prepare': "ダウンロードコマンドを準備中...", 
        'status_downloading_spotify': "Spotifyリンクを処理中...", 
        'status_downloading_execute': "ダウンロードと変換を実行中...", 
        'status_download_success_spotify': "✅ Spotify楽曲のダウンロードに成功しました！保存先:", 
        'status_download_success_general': "✅ コンテンツのダウンロードと変換に成功しました！保存先:", 
        'status_error_exec': "❌ 実行に失敗しました。エラーコード:", 
        'status_error_not_found': "❌ エラー: yt-dlp, ffmpeg, または spotdlが見つかりません。", 
        'status_error_unexpected': "❌ 予期せぬエラーが発生しました:", 
        'status_path_set': "新しい出力先パスが設定されました。", 
        'combobox_lang_label': "言語選択:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (オーディオ)', 'FLAC_LOSSLESS': 'FLAC (ロスレス)', 'AAC_AUDIO': 'AAC (オーディオ)', 'MP4_VIDEO': 'MP4 (ビデオ)', 'MOV_VIDEO': 'MOV (ビデオ)'},
            'video_qualities': {'BEST_VIDEO': '最高画質 (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': '最高音質 (Best/VBR)', 'HIGH_AUDIO': '高音質 (High/VBR)', 'MEDIUM_AUDIO': '中音質 (Medium/CBR)'}
        }
    },
    'fr': {
        'lang_display': "fr (Français)", 
        'title': "Téléchargeur Média Universel", 
        'url_label': "Entrez l'URL (Multi-sites):", 
        'format_label': "Sélectionner le format:", 
        'quality_video_label': "Sélectionner la qualité vidéo:", 
        'quality_audio_label': "Sélectionner la qualité audio:", 
        'path_label': "Chemin de sortie:", 
        'browse_button': "Parcourir...", 
        'download_button': "🚀 Démarrer le Téléchargement", 
        'ready_status': "Prêt. Support multi-sites.", 
        'error_no_url': "⚠️ Veuillez entrer une URL!", 
        'status_downloading_prepare': "Préparation de la commande...", 
        'status_downloading_spotify': "Traitement du lien Spotify...", 
        'status_downloading_execute': "Exécution du téléchargement...", 
        'status_download_success_spotify': "✅ Chanson Spotify téléchargée avec succès ! Enregistrée dans:", 
        'status_download_success_general': "✅ Contenu téléchargé et converti avec succès ! Enregistré dans:", 
        'status_error_exec': "❌ Échec de l'exécution, code :", 
        'status_error_not_found': "❌ ERREUR : yt-dlp, ffmpeg, ou spotdl introuvable.", 
        'status_error_unexpected': "❌ Une erreur inattendue s'est produite:", 
        'status_path_set': "Nouveau chemin de sortie défini.", 
        'combobox_lang_label': "Sélectionner la langue:",
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Sans perte)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Vidéo)', 'MOV_VIDEO': 'MOV (Vidéo)'},
            'video_qualities': {'BEST_VIDEO': 'Meilleure Qualité (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Meilleure Qualité (VBR)', 'HIGH_AUDIO': 'Haute Qualité (VBR)', 'MEDIUM_AUDIO': 'Qualité Moyenne (CBR)'}
        } 
    },
    'de': {
        'lang_display': "de (Deutsch)", 
        'title': "Universal Media Downloader", 
        'url_label': "URL eingeben (Multi-Site-Unterstützung):", 
        'format_label': "Ausgabeformat wählen:", 
        'quality_video_label': "Videoqualität wählen:", 
        'quality_audio_label': "Audioqualität wählen:", 
        'path_label': "Ausgabepfad:", 
        'browse_button': "Durchsuchen...", 
        'download_button': "🚀 Download starten", 
        'ready_status': "Bereit. Multi-Site-Unterstützung.", 
        'error_no_url': "⚠️ Bitte geben Sie eine URL ein!", 
        'status_downloading_prepare': "Download-Befehl wird vorbereitet...", 
        'status_downloading_spotify': "Spotify-Link wird verarbeitet...", 
        'status_downloading_execute': "Download wird ausgeführt...", 
        'status_download_success_spotify': "✅ Spotify-Song erfolgreich heruntergeladen! Gespeichert unter:", 
        'status_download_success_general': "✅ Inhalt erfolgreich heruntergeladen und konvertiert! Gespeichert unter:", 
        'status_error_exec': "❌ Ausführung fehlgeschlagen, Code:", 
        'status_error_not_found': "❌ FEHLER: yt-dlp, ffmpeg oder spotdl nicht gefunden.", 
        'status_error_unexpected': "❌ Ein unerwarteter Fehler ist aufgetreten:", 
        'status_path_set': "Neuer Ausgabepfad wurde festgelegt.", 
        'combobox_lang_label': "Sprache wählen:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Verlustfrei)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Höchste Qualität (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Beste Qualität (VBR)', 'HIGH_AUDIO': 'Hohe Qualität (VBR)', 'MEDIUM_AUDIO': 'Mittlere Qualität (CBR)'}
        }
    },
    'es': {
        'lang_display': "es (Español)", 
        'title': "Descargador Universal de Medios", 
        'url_label': "Introducir URL (Multi-sitio):", 
        'format_label': "Seleccionar formato de salida:", 
        'quality_video_label': "Seleccionar Calidad de Video:", 
        'quality_audio_label': "Seleccionar Calidad de Audio:", 
        'path_label': "Ruta de salida:", 
        'browse_button': "Explorar...", 
        'download_button': "🚀 Iniciar Descarga y Conversión", 
        'ready_status': "Listo. Soporte multi-sitio.", 
        'error_no_url': "⚠️ ¡Por favor, introduzca una URL!", 
        'status_downloading_prepare': "Preparando comando de descarga...", 
        'status_downloading_spotify': "Procesando enlace de Spotify...", 
        'status_downloading_execute': "Ejecutando descarga...", 
        'status_download_success_spotify': "✅ Canción de Spotify descargada con éxito! Guardada en:", 
        'status_download_success_general': "✅ Contenido descargado y convertido con éxito! Guardada en:", 
        'status_error_exec': "❌ Falló la ejecución, código:", 
        'status_error_not_found': "❌ ERROR: yt-dlp, ffmpeg o spotdl no encontrados.", 
        'status_error_unexpected': "❌ Ocurrió un error inesperado:", 
        'status_path_set': "Nueva ruta de salida establecida.", 
        'combobox_lang_label': "Seleccionar idioma:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Sin pérdida)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Máxima Calidad (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Mejor Calidad (VBR)', 'HIGH_AUDIO': 'Alta Calidad (VBR)', 'MEDIUM_AUDIO': 'Calidad Media (CBR)'}
        }
    },
    'pt': {
        'lang_display': "pt (Português)", 
        'title': "Downloader Universal", 
        'url_label': "Insira o URL (Vários sites suportados):", 
        'format_label': "Selecione o formato de saída:", 
        'quality_video_label': "Selecione a Qualidade de Vídeo:", 
        'quality_audio_label': "Selecione a Qualidade de Áudio:", 
        'path_label': "Caminho de Saída:", 
        'browse_button': "Procurar...", 
        'download_button': "🚀 Iniciar Download e Converter", 
        'ready_status': "Pronto. Suporte multi-site.", 
        'error_no_url': "⚠️ Por favor, insira um URL!", 
        'status_downloading_prepare': "Preparando comando de download...", 
        'status_downloading_spotify': "Processando link do Spotify...", 
        'status_downloading_execute': "Executando download...", 
        'status_download_success_spotify': "✅ Música do Spotify baixada com sucesso! Salva em:", 
        'status_download_success_general': "✅ Conteúdo baixado e convertido com sucesso! Salva em:", 
        'status_error_exec': "❌ Falha na execução, código:", 
        'status_error_not_found': "❌ ERRO: yt-dlp, ffmpeg ou spotdl não encontrados.", 
        'status_error_unexpected': "❌ Ocorreu um erro inesperado:", 
        'status_path_set': "Novo caminho de saída definido.", 
        'combobox_lang_label': "Selecionar idioma:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Áudio)', 'FLAC_LOSSLESS': 'FLAC (Sem perdas)', 'AAC_AUDIO': 'AAC (Áudio)', 'MP4_VIDEO': 'MP4 (Vídeo)', 'MOV_VIDEO': 'MOV (Vídeo)'},
            'video_qualities': {'BEST_VIDEO': 'Qualidade Máxima (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Melhor Qualidade (VBR)', 'HIGH_AUDIO': 'Alta Qualidade (VBR)', 'MEDIUM_AUDIO': 'Qualidade Média (CBR)'}
        }
    },
    'ru': {
        'lang_display': "ru (Русский)", 
        'title': "Универсальный загрузчик", 
        'url_label': "Введите URL (Мульти-сайт):", 
        'format_label': "Выберите формат вывода:", 
        'quality_video_label': "Выберите качество видео:", 
        'quality_audio_label': "Выберите качество аудио:", 
        'path_label': "Путь вывода:", 
        'browse_button': "Обзор...", 
        'download_button': "🚀 Начать загрузку", 
        'ready_status': "Готово. Поддержка нескольких сайтов.", 
        'error_no_url': "⚠️ Пожалуйста, введите URL!", 
        'status_downloading_prepare': "Подготовка команды загрузки...", 
        'status_downloading_spotify': "Обработка ссылки Spotify...", 
        'status_downloading_execute': "Выполнение загрузки...", 
        'status_download_success_spotify': "✅ Песня Spotify успешно загружена! Сохранено в:", 
        'status_download_success_general': "✅ Контент успешно загружен и конвертирован! Сохранено в:", 
        'status_error_exec': "❌ Сбой выполнения, код:", 
        'status_error_not_found': "❌ ОШИБКА: yt-dlp, ffmpeg или spotdl не найдены.", 
        'status_error_unexpected': "❌ Произошла непредвиденная ошибка:", 
        'status_path_set': "Установлен новый путь вывода.", 
        'combobox_lang_label': "Выбрать язык:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Аудио)', 'FLAC_LOSSLESS': 'FLAC (Без потерь)', 'AAC_AUDIO': 'AAC (Аудио)', 'MP4_VIDEO': 'MP4 (Видео)', 'MOV_VIDEO': 'MOV (Видео)'},
            'video_qualities': {'BEST_VIDEO': 'Максимальное Качество (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Лучшее Качество (VBR)', 'HIGH_AUDIO': 'Высокое Качество (VBR)', 'MEDIUM_AUDIO': 'Среднее Качество (CBR)'}
        }
    },
    'ko': {
        'lang_display': "ko (한국어)", 
        'title': "통합 미디어 다운로더", 
        'url_label': "URL 입력 (다중 사이트 지원):", 
        'format_label': "출력 형식 선택:", 
        'quality_video_label': "비디오 화질 선택:", 
        'quality_audio_label': "오디오 음질 선택:", 
        'path_label': "출력 경로:", 
        'browse_button': "찾아보기...", 
        'download_button': "🚀 다운로드 및 변환 시작", 
        'ready_status': "준비 완료. 다중 사이트 지원。", 
        'error_no_url': "⚠️ URL을 입력해주세요!", 
        'status_downloading_prepare': "다운로드 명령 준비 중...", 
        'status_downloading_spotify': "Spotify 링크 처리 중...", 
        'status_downloading_execute': "다운로드 및 변환 실행 중...", 
        'status_download_success_spotify': "✅ Spotify 노래 다운로드 성공! 저장 위치:", 
        'status_download_success_general': "✅ 콘텐츠 다운로드 및 변환 성공! 저장 위치:", 
        'status_error_exec': "❌ 실행 실패, 오류 코드:", 
        'status_error_not_found': "❌ 오류: yt-dlp, ffmpeg, 또는 spotdl을 찾을 수 없습니다。", 
        'status_error_unexpected': "❌ 예기치 않은 오류가 발생했습니다:", 
        'status_path_set': "새 출력 경로가 설정되었습니다。", 
        'combobox_lang_label': "언어 선택:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (오디오)', 'FLAC_LOSSLESS': 'FLAC (무손실)', 'AAC_AUDIO': 'AAC (오디오)', 'MP4_VIDEO': 'MP4 (비디오)', 'MOV_VIDEO': 'MOV (비디오)'},
            'video_qualities': {'BEST_VIDEO': '최고 화질 (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': '최고 음질 (Best/VBR)', 'HIGH_AUDIO': '고음질 (High/VBR)', 'MEDIUM_AUDIO': '중간 음질 (Medium/CBR)'}
        }
    },
    'ar': {
        'lang_display': "ar (العربية)", 
        'title': "مُنزّل الوسائط العام", 
        'url_label': "أدخل الرابط (دعم متعدد المواقع):", 
        'format_label': "حدد تنسيق الإخراج:", 
        'quality_video_label': "اختر جودة الفيديو:", 
        'quality_audio_label': "اختر جودة الصوت:", 
        'path_label': "مسار الإخراج:", 
        'browse_button': "تصفح...", 
        'download_button': "🚀 بدء التحميل والتحويل", 
        'ready_status': "جاهز. دعم متعدد المواقع。", 
        'error_no_url': "⚠️ يرجى إدخال رابط!", 
        'status_downloading_prepare': "تحضير أمر التحميل...", 
        'status_downloading_spotify': "معالجة رابط Spotify...", 
        'status_downloading_execute': "تنفيذ التحميل...", 
        'status_download_success_spotify': "✅ تم تحميل أغنية Spotify بنجاح! تم الحفظ في:", 
        'status_download_success_general': "✅ تم تحميل المحتوى وتحويله بنجاح! تم الحفظ في:", 
        'status_error_exec': "❌ فشل التنفيذ، الرمز:", 
        'status_error_not_found': "❌ خطأ: لم يتم العثور على yt-dlp أو ffmpeg أو spotdl。", 
        'status_error_unexpected': "❌ حدث خطأ غير متوقع:", 
        'status_path_set': "تم تعيين مسار إخراج جديد。", 
        'combobox_lang_label': "اختر اللغة:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (صوت)', 'FLAC_LOSSLESS': 'FLAC (بدون فقدان)', 'AAC_AUDIO': 'AAC (صوت)', 'MP4_VIDEO': 'MP4 (فيديو)', 'MOV_VIDEO': 'MOV (فيديو)'},
            'video_qualities': {'BEST_VIDEO': 'أعلى جودة (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'أفضل جودة (VBR)', 'HIGH_AUDIO': 'جودة عالية (VBR)', 'MEDIUM_AUDIO': 'جودة متوسطة (CBR)'}
        }
    },
    'th': {
        'lang_display': "th (ไทย)", 
        'title': "เครื่องมือดาวน์โหลดสื่อสากล", 
        'url_label': "ป้อน URL (รองรับหลายเว็บไซต์):", 
        'format_label': "เลือกรูปแบบเอาต์พุต:", 
        'quality_video_label': "เลือกคุณภาพวิดีโอ:", 
        'quality_audio_label': "เลือกคุณภาพเสียง:", 
        'path_label': "เส้นทางเอาต์พุต:", 
        'browse_button': "เรียกดู...", 
        'download_button': "🚀 เริ่มดาวน์โหลดและแปลง", 
        'ready_status': "พร้อมแล้ว รองรับหลายเว็บไซต์", 
        'error_no_url': "⚠️ กรุณาป้อน URL!", 
        'status_downloading_prepare': "กำลังเตรียมคำสั่งดาวน์โหลด...", 
        'status_downloading_spotify': "กำลังประมวลผลลิงก์ Spotify...", 
        'status_downloading_execute': "กำลังดำเนินการดาวน์โหลด...", 
        'status_download_success_spotify': "✅ ดาวน์โหลดเพลง Spotify สำเร็จแล้ว! บันทึกที่:", 
        'status_download_success_general': "✅ ดาวน์โหลดและแปลงเนื้อหาสำเร็จแล้ว! บันทึกที่:", 
        'status_error_exec': "❌ การดำเนินการล้มเหลว รหัส:", 
        'status_error_not_found': "❌ ข้อผิดพลาด: ไม่พบ yt-dlp, ffmpeg, หรือ spotdl", 
        'status_error_unexpected': "❌ เกิดข้อผิดพลาดที่ไม่คาดคิด:", 
        'status_path_set': "ได้กำหนดเส้นทางเอาต์พุตใหม่แล้ว", 
        'combobox_lang_label': "เลือกภาษา:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (เสียง)', 'FLAC_LOSSLESS': 'FLAC (ไม่สูญเสีย)', 'AAC_AUDIO': 'AAC (เสียง)', 'MP4_VIDEO': 'MP4 (วิดีโอ)', 'MOV_VIDEO': 'MOV (วิดีโอ)'},
            'video_qualities': {'BEST_VIDEO': 'คุณภาพสูงสุด (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'คุณภาพเสียงดีที่สุด (VBR)', 'HIGH_AUDIO': 'คุณภาพสูง (VBR)', 'MEDIUM_AUDIO': 'คุณภาพปานกลาง (CBR)'}
        }
    },
    'vi': {
        'lang_display': "vi (Tiếng Việt)", 
        'title': "Trình Tải Xuống Đa Phương Tiện", 
        'url_label': "Nhập URL (Hỗ trợ đa trang):", 
        'format_label': "Chọn Định dạng Đầu ra:", 
        'quality_video_label': "Chọn Chất lượng Video:", 
        'quality_audio_label': "Chọn Chất lượng Âm thanh:", 
        'path_label': "Đường dẫn Đầu ra:", 
        'browse_button': "Duyệt...", 
        'download_button': "🚀 Bắt đầu Tải xuống & Chuyển đổi", 
        'ready_status': "Sẵn sàng. Hỗ trợ đa trang。", 
        'error_no_url': "⚠️ Vui lòng nhập URL!", 
        'status_downloading_prepare': "Đang chuẩn bị lệnh tải xuống...", 
        'status_downloading_spotify': "Đang xử lý liên kết Spotify...", 
        'status_downloading_execute': "Đang thực hiện tải xuống...", 
        'status_download_success_spotify': "✅ Tải xuống bài hát Spotify thành công! Đã lưu tại:", 
        'status_download_success_general': "✅ Tải xuống và chuyển đổi nội dung thành công! Đã lưu tại:", 
        'status_error_exec': "❌ Thực thi thất bại, mã lỗi:", 
        'status_error_not_found': "❌ Lỗi: Không tìm thấy yt-dlp, ffmpeg, hoặc spotdl。", 
        'status_error_unexpected': "❌ Đã xảy ra lỗi không mong muốn:", 
        'status_path_set': "Đã đặt đường dẫn đầu ra mới。", 
        'combobox_lang_label': "Chọn Ngôn ngữ:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Âm thanh)', 'FLAC_LOSSLESS': 'FLAC (Không mất mát)', 'AAC_AUDIO': 'AAC (Âm thanh)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Chất lượng Cao nhất (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Chất lượng Tốt nhất (VBR)', 'HIGH_AUDIO': 'Chất lượng Cao (VBR)', 'MEDIUM_AUDIO': 'Chất lượng Trung bình (CBR)'}
        }
    },
    'it': {
        'lang_display': "it (Italiano)", 
        'title': "Downloader Universale", 
        'url_label': "Inserisci URL (Supporto Multi-sito):", 
        'format_label': "Seleziona Formato di Uscita:", 
        'quality_video_label': "Seleziona Qualità Video:", 
        'quality_audio_label': "Seleziona Qualità Audio:", 
        'path_label': "Percorso di Uscita:", 
        'browse_button': "Sfoglia...", 
        'download_button': "🚀 Avvia Download e Conversione", 
        'ready_status': "Pronto. Supporto multi-sito.", 
        'error_no_url': "⚠️ Per favore, inserisci un URL!", 
        'status_downloading_prepare': "Preparazione del comando di download...", 
        'status_downloading_spotify': "Elaborazione del link Spotify...", 
        'status_downloading_execute': "Esecuzione download e conversione...", 
        'status_download_success_spotify': "✅ Canzone Spotify scaricata con successo! Salvata in:", 
        'status_download_success_general': "✅ Contenuto scaricato e convertito con successo! Salvata in:", 
        'status_error_exec': "❌ Esecuzione fallita, codice:", 
        'status_error_not_found': "❌ ERRORE: yt-dlp, ffmpeg o spotdl non trovati.", 
        'status_error_unexpected': "❌ Si è verificato un errore imprevisto:", 
        'status_path_set': "Nuovo percorso di uscita impostato.", 
        'combobox_lang_label': "Seleziona Lingua:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Senza perdita)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Massima Qualità (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Migliore Qualità (VBR)', 'HIGH_AUDIO': 'Alta Qualità (VBR)', 'MEDIUM_AUDIO': 'Qualità Media (CBR)'}
        }
    },
    'tr': {
        'lang_display': "tr (Türkçe)", 
        'title': "Evrensel Medya İndiricisi", 
        'url_label': "URL Girin (Çoklu Site Desteği):", 
        'format_label': "Çıkış Formatını Seçin:", 
        'quality_video_label': "Video Kalitesini Seçin:", 
        'quality_audio_label': "Ses Kalitesini Seçin:", 
        'path_label': "Çıkış Yolu:", 
        'browse_button': "Gözat...", 
        'download_button': "🚀 İndirmeyi Başlat & Dönüştür", 
        'ready_status': "Hazır. Çoklu site desteği.", 
        'error_no_url': "⚠️ Lütfen bir URL girin!", 
        'status_downloading_prepare': "İndirme komutu hazırlanıyor...", 
        'status_downloading_spotify': "Spotify bağlantısı işleniyor...", 
        'status_downloading_execute': "İndirme ve dönüştürme yürütülüyor...", 
        'status_download_success_spotify': "✅ Spotify şarkısı başarıyla indirildi! Kaydedildi:", 
        'status_download_success_general': "✅ İçerik başarıyla indirildi ve dönüştürüldü! Kaydedildi:", 
        'status_error_exec': "❌ Yürütme başarısız, kod:", 
        'status_error_not_found': "❌ HATA: yt-dlp, ffmpeg veya spotdl bulunamadı.", 
        'status_error_unexpected': "❌ Beklenmeyen bir hata oluştu:", 
        'status_path_set': "Yeni çıkış yolu ayarlandı.", 
        'combobox_lang_label': "Dil Seçin:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Ses)', 'FLAC_LOSSLESS': 'FLAC (Kayıpsız)', 'AAC_AUDIO': 'AAC (Ses)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'En Yüksek Kalite (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'En İyi Ses Kalitesi (VBR)', 'HIGH_AUDIO': 'Yüksek Ses Kalitesi (VBR)', 'MEDIUM_AUDIO': 'Orta Ses Kalitesi (CBR)'}
        }
    },
    'pl': {
        'lang_display': "pl (Polski)", 
        'title': "Uniwersalny Downloader Mediów", 
        'url_label': "Wprowadź URL (Obsługa wielu witryn):", 
        'format_label': "Wybierz Format Wyjściowy:", 
        'quality_video_label': "Wybierz Jakość Wideo:", 
        'quality_audio_label': "Wybierz Jakość Audio:", 
        'path_label': "Ścieżka Wyjściowa:", 
        'browse_button': "Przeglądaj...", 
        'download_button': "🚀 Rozpocznij Pobieranie i Konwersję", 
        'ready_status': "Gotowe. Obsługa wielu witryn.", 
        'error_no_url': "⚠️ Proszę wprowadzić URL!", 
        'status_downloading_prepare': "Przygotowywanie polecenia pobierania...", 
        'status_downloading_spotify': "Przetwarzanie linku Spotify...", 
        'status_downloading_execute': "Wykonywanie pobierania i konwersji...", 
        'status_download_success_spotify': "✅ Piosenka Spotify pobrana pomyślnie! Zapisano w:", 
        'status_download_success_general': "✅ Zawartość pobrana i skonwertowana pomyślnie! Zapisano w:", 
        'status_error_exec': "❌ Błąd wykonania, kod:", 
        'status_error_not_found': "❌ BŁĄD: Nie znaleziono yt-dlp, ffmpeg lub spotdl.", 
        'status_error_unexpected': "❌ Wystąpił nieoczekiwany błąd:", 
        'status_path_set': "Ustawiono nową ścieżkę wyjściową。", 
        'combobox_lang_label': "Wybierz Język:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Bezstratny)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Wideo)', 'MOV_VIDEO': 'MOV (Wideo)'},
            'video_qualities': {'BEST_VIDEO': 'Najwyższa Jakość (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Najlepsza Jakość (VBR)', 'HIGH_AUDIO': 'Wysoka Jakość (VBR)', 'MEDIUM_AUDIO': 'Średnia Jakość (CBR)'}
        }
    },
    'nl': {
        'lang_display': "nl (Nederlands)", 
        'title': "Universele Media Downloader", 
        'url_label': "Voer URL in (Ondersteuning voor meerdere sites):", 
        'format_label': "Selecteer Uitvoerformaat:", 
        'quality_video_label': "Selecteer Videokwaliteit:", 
        'quality_audio_label': "Selecteer Audiokwaliteit:", 
        'path_label': "Uitvoerpad:", 
        'browse_button': "Bladeren...", 
        'download_button': "🚀 Start Downloaden & Converteren", 
        'ready_status': "Klaar. Ondersteuning voor meerdere sites.", 
        'error_no_url': "⚠️ Voer een URL in!", 
        'status_downloading_prepare': "Downloadopdracht voorbereiden...", 
        'status_downloading_spotify': "Spotify-link verwerken...", 
        'status_downloading_execute': "Downloaden en converteren uitvoeren...", 
        'status_download_success_spotify': "✅ Spotify-nummer succesvol gedownload! Opgeslagen in:", 
        'status_download_success_general': "✅ Inhoud succesvol gedownload en geconverteerd! Opgeslagen in:", 
        'status_error_exec': "❌ Uitvoering mislukt, code:", 
        'status_error_not_found': "❌ FOUT: yt-dlp, ffmpeg of spotdl niet gevonden.", 
        'status_error_unexpected': "❌ Er is een onverwachte fout opgetreden:", 
        'status_path_set': "Nieuw uitvoerpad is ingesteld.", 
        'combobox_lang_label': "Selecteer Taal:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Audio)', 'FLAC_LOSSLESS': 'FLAC (Lossless)', 'AAC_AUDIO': 'AAC (Audio)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Hoogste Kwaliteit (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Beste Kwaliteit (VBR)', 'HIGH_AUDIO': 'Hoge Kwaliteit (VBR)', 'MEDIUM_AUDIO': 'Middelmatige Kwaliteit (CBR)'}
        }
    },
    'sv': {
        'lang_display': "sv (Svenska)", 
        'title': "Universal Media Nedladdare", 
        'url_label': "Ange URL (Stöd för flera webbplatser):", 
        'format_label': "Välj Utdataformat:", 
        'quality_video_label': "Välj Videokvalitet:", 
        'quality_audio_label': "Välj Ljudkvalitet:", 
        'path_label': "Utdata Sökväg:", 
        'browse_button': "Bläddra...", 
        'download_button': "🚀 Starta Nedladdning & Konvertera", 
        'ready_status': "Klar. Stöd för flera webbplatser.", 
        'error_no_url': "⚠️ Ange en URL!", 
        'status_downloading_prepare': "Förbereder nedladdningskommando...", 
        'status_downloading_spotify': "Bearbetar Spotify-länk...", 
        'status_downloading_execute': "Utför nedladdning och konvertering...", 
        'status_download_success_spotify': "✅ Spotify-låten har laddats ner framgångsrikt! Sparad i:", 
        'status_download_success_general': "✅ Innehållet har laddats ner och konverterats framgångsrikt! Sparad i:", 
        'status_error_exec': "❌ Utförandet misslyckades, kod:", 
        'status_error_not_found': "❌ FEL: yt-dlp, ffmpeg eller spotdl hittades inte。", 
        'status_error_unexpected': "❌ Ett oväntat fel uppstod:", 
        'status_path_set': "Ny utdatasökväg har ställts in。", 
        'combobox_lang_label': "Välj Språk:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Ljud)', 'FLAC_LOSSLESS': 'FLAC (Lossless)', 'AAC_AUDIO': 'AAC (Ljud)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Högsta Kvalitet (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Bästa Kvalitet (VBR)', 'HIGH_AUDIO': 'Hög Kvalitet (VBR)', 'MEDIUM_AUDIO': 'Medel Kvalitet (CBR)'}
        }
    },
    'fi': {
        'lang_display': "fi (Suomi)", 
        'title': "Universaali Medianlataaja", 
        'url_label': "Syötä URL (Usean sivuston tuki):", 
        'format_label': "Valitse Tulostusmuoto:", 
        'quality_video_label': "Valitse Videon Laatu:", 
        'quality_audio_label': "Valitse Äänen Laatu:", 
        'path_label': "Tulostuspolku:", 
        'browse_button': "Selaa...", 
        'download_button': "🚀 Aloita Lataus & Muunna", 
        'ready_status': "Valmis. Usean sivuston tuki.", 
        'error_no_url': "⚠️ Anna URL!", 
        'status_downloading_prepare': "Latauskomentoa valmistellaan...", 
        'status_downloading_spotify': "Spotify-linkkiä käsitellään...", 
        'status_downloading_execute': "Lataus ja muunnos suoritetaan...", 
        'status_download_success_spotify': "✅ Spotify-kappale ladattu onnistuneesti! Tallennettu:", 
        'status_download_success_general': "✅ Sisältö ladattu ja muunnettu onnistuneesti! Tallennettu:", 
        'status_error_exec': "❌ Suoritus epäonnistui, koodi:", 
        'status_error_not_found': "❌ VIRHE: yt-dlp, ffmpeg tai spotdl ei löytynyt。", 
        'status_error_unexpected': "❌ Odottamaton virhe tapahtui:", 
        'status_path_set': "Uusi tulostuspolku asetettu。", 
        'combobox_lang_label': "Valitse Kieli:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Ääni)', 'FLAC_LOSSLESS': 'FLAC (Häviötön)', 'AAC_AUDIO': 'AAC (Ääni)', 'MP4_VIDEO': 'MP4 (Video)', 'MOV_VIDEO': 'MOV (Video)'},
            'video_qualities': {'BEST_VIDEO': 'Paras Laatu (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Paras Äänenlaatu (VBR)', 'HIGH_AUDIO': 'Korkea Äänenlaatu (VBR)', 'MEDIUM_AUDIO': 'Keskitaso Äänenlaatu (CBR)'}
        }
    },
    'el': {
        'lang_display': "el (Ελληνικά)", 
        'title': "Καθολικός Λήπτης Πολυμέσων", 
        'url_label': "Εισαγάγετε URL (Υποστήριξη πολλαπλών ιστοτόπων):", 
        'format_label': "Επιλέξτε Μορφή Εξόδου:", 
        'quality_video_label': "Επιλέξτε Ποιότητα Βίντεο:", 
        'quality_audio_label': "Επιλέξτε Ποιότητα Ήχου:", 
        'path_label': "Διαδρομή Εξόδου:", 
        'browse_button': "Αναζήτηση...", 
        'download_button': "🚀 Έναρξη Λήψης & Μετατροπής", 
        'ready_status': "Έτοιμο. Υποστήριξη πολλαπλών ιστοτόπων。", 
        'error_no_url': "⚠️ Παρακαλώ εισάγετε μια διεύθυνση URL!", 
        'status_downloading_prepare': "Προετοιμασία εντολής λήψης...", 
        'status_downloading_spotify': "Επεξεργασία συνδέσμου Spotify...", 
        'status_downloading_execute': "Εκτέλεση λήψης και μετατροπής...", 
        'status_download_success_spotify': "✅ Το τραγούδι Spotify λήφθηκε επιτυχώς! Αποθηκεύτηκε:", 
        'status_download_success_general': "✅ Το περιεχόμενο λήφθηκε και μετατράπηκε επιτυχώς! Αποθηκεύτηκε:", 
        'status_error_exec': "❌ Αποτυχία εκτέλεσης, κωδικός:", 
        'status_error_not_found': "❌ ΣΦΑΛΜΑ: Το yt-dlp, ffmpeg ή spotdl δεν βρέθηκε。", 
        'status_error_unexpected': "❌ Προέκυψε ένα απρόσμενο σφάλμα:", 
        'status_path_set': "Έχει οριστεί νέα διαδρομή εξόδου。", 
        'combobox_lang_label': "Επιλογή Γλώσσας:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (Ήχος)', 'FLAC_LOSSLESS': 'FLAC (Χωρίς απώλειες)', 'AAC_AUDIO': 'AAC (Ήχος)', 'MP4_VIDEO': 'MP4 (Βίντεο)', 'MOV_VIDEO': 'MOV (Βίντεο)'},
            'video_qualities': {'BEST_VIDEO': 'Καλύτερη Ποιότητα (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'Καλύτερη Ποιότητα Ήχου (VBR)', 'HIGH_AUDIO': 'Υψηλή Ποιότητα Ήχου (VBR)', 'MEDIUM_AUDIO': 'Μέτρια Ποιότητα Ήχου (CBR)'}
        }
    },
    'hi': {
        'lang_display': "hi (हिन्दी)", 
        'title': "सार्वभौमिक मीडिया डाउनलोडर", 
        'url_label': "URL दर्ज करें (बहु-साइट समर्थन):", 
        'format_label': "आउटपुट प्रारूप चुनें:", 
        'quality_video_label': "वीडियो गुणवत्ता चुनें:", 
        'quality_audio_label': "ऑडियो गुणवत्ता चुनें:", 
        'path_label': "आउटपुट पथ:", 
        'browse_button': "ब्राउज़ करें...", 
        'download_button': "🚀 डाउनलोड और कनवर्ट शुरू करें", 
        'ready_status': "तैयार है। बहु-साइट समर्थन।", 
        'error_no_url': "⚠️ कृपया URL दर्ज करें!", 
        'status_downloading_prepare': "डाउनलोड कमांड तैयार हो रहा है...", 
        'status_downloading_spotify': "Spotify लिंक संसाधित हो रहा है...", 
        'status_downloading_execute': "डाउनलोड और कनवर्ट निष्पादित हो रहा है...", 
        'status_download_success_spotify': "✅ Spotify गाना सफलतापूर्वक डाउनलोड हो गया! सहेजा गया:", 
        'status_download_success_general': "✅ सामग्री सफलतापूर्वक डाउनलोड और कनवर्ट हो गई! सहेजा गया:", 
        'status_error_exec': "❌ निष्पादन विफल, कोड:", 
        'status_error_not_found': "❌ त्रुटि: yt-dlp, ffmpeg, या spotdl नहीं मिला।", 
        'status_error_unexpected': "❌ एक अप्रत्याशित त्रुटि हुई:", 
        'status_path_set': "नया आउटपुट पथ सेट किया गया है।", 
        'combobox_lang_label': "भाषा चुनें:", 
        # 新增的選項翻譯
        'options': {
            'formats': {'MP3_AUDIO': 'MP3 (ऑडियो)', 'FLAC_LOSSLESS': 'FLAC (हानिरहित)', 'AAC_AUDIO': 'AAC (ऑडियो)', 'MP4_VIDEO': 'MP4 (वीडियो)', 'MOV_VIDEO': 'MOV (वीडियो)'},
            'video_qualities': {'BEST_VIDEO': 'उच्चतम गुणवत्ता (Best)', 'FHD_1080P': '1080p (FHD)', 'HD_720P': '720p (HD)'},
            'audio_qualities': {'BEST_AUDIO': 'सर्वोत्तम ऑडियो गुणवत्ता (VBR)', 'HIGH_AUDIO': 'उच्च ऑडियो गुणवत्ता (VBR)', 'MEDIUM_AUDIO': 'मध्यम ऑडियो गुणवत्ता (CBR)'}
        }
    },
    # 您可以繼續添加其他語言...
}

# --- 語言偵測和處理邏輯 (優化後版本) ---

def get_system_language():
    """
    偵測系統首選語言，優先返回包含區域的代碼 (e.g., 'zh_TW')。
    """
    try:
        # 1. 獲取系統的預設語言設定 (例如 'zh_TW.UTF-8' 或 'C' 等)
        system_locale = locale.getdefaultlocale()
        
        if system_locale and system_locale[0]:
            # 提取完整的語言代碼 (例如 'zh_TW') 並轉換為小寫，用下劃線連接
            full_lang_code = system_locale[0].split('.')[0].replace('-', '_').lower()
            
            # 2. 檢查完整的區域代碼是否在支援列表中
            if full_lang_code in LANG_DATA:
                return full_lang_code
            
            # 3. 如果完整的區域代碼不在列表中，嘗試使用基礎語言代碼 (例如 'zh')
            base_lang_code = full_lang_code.split('_')[0]
            
            # 特殊處理中文：優先分配到 zh_TW 或 zh_CN
            if base_lang_code == 'zh':
                # 簡體中文區域代碼常見的有 zh_CN, zh_SG
                if full_lang_code in ('zh_cn', 'zh-cn', 'zh_sg', 'zh-sg'): 
                    return 'zh_CN'
                else: 
                    # 繁體中文區域代碼常見的有 zh_TW, zh_HK, zh_MO
                    return 'zh_TW' # 默認使用 zh_TW (繁體中文)

            # 4. 檢查基礎語言代碼是否在支援列表中 (如 'en', 'fr', 'de')
            if base_lang_code in LANG_DATA:
                return base_lang_code

    except Exception as e:
        print(f"Error detecting system locale: {e}")
        
    # 5. 最終預設
    return 'en' 

# --- 網址判斷函式 ---
def is_spotify_url(url):
    """檢查網址是否為 Spotify 連結"""
    spotify_pattern = r'^(https?:\/\/open\.spotify\.com\/(track|album|playlist|artist|show|episode)\/[a-zA-Z0-9]+)'
    return re.match(spotify_pattern, url)

# --- 核心下載功能 ---
def download_content(url, format_key, quality_key, output_path, status_callback, current_lang):
    """在獨立執行緒中執行下載命令 (yt-dlp 或 spotdl)"""
    texts = LANG_DATA.get(current_lang, LANG_DATA['en'])
    is_spotify = is_spotify_url(url)
    status_callback(texts['status_downloading_prepare'], "blue")

    if is_spotify:
        status_callback(texts['status_downloading_spotify'], "blue")
        # spotdl 輸出路徑帶有命名模板，這裡使用相對路徑，讓 spotdl 處理絕對路徑
        spotdl_output_template = os.path.join(output_path, "{artist} - {title}.{ext}")
        command = [
            'spotdl',
            'download',
            '--output', spotdl_output_template,
            url
        ]
    else:
        status_callback(texts['status_downloading_execute'], "blue")
        
        # 根據內部 key 獲取 yt-dlp 參數
        format_settings = FORMAT_OPTIONS.get(format_key, [])
        is_audio_download = 'AUDIO' in format_key or 'LOSSLESS' in format_key
        
        # yt-dlp 輸出路徑和格式設定
        yt_dlp_output_template = os.path.join(output_path, "%(title)s.%(ext)s")
        command = [
            'yt-dlp', 
            '-N', '8', # 8 執行緒加速下載
            '--no-part', # 下載完成後不保留 .part 文件
            '-o', yt_dlp_output_template, 
        ] + format_settings + [url]

        if is_audio_download:
            # 音頻下載：加入音質參數
            quality_value = AUDIO_QUALITY_OPTIONS.get(quality_key, '0')
            command.extend(['--audio-quality', quality_value])
        else:
            # 視訊下載：加入畫質參數
            quality_selector = QUALITY_OPTIONS.get(quality_key, 'bestvideo+bestaudio/best')
            command.extend(['-f', quality_selector])
            
        
    try:
        # 執行命令 (不顯示終端機視窗)
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', timeout=None, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        # 成功訊息包含輸出路徑
        path_msg = f"{output_path}" 
        if is_spotify:
            status_callback(f"{texts['status_download_success_spotify']} {path_msg}", "green")
        else:
            status_callback(f"{texts['status_download_success_general']} {path_msg}", "green")

    except subprocess.CalledProcessError as e:
        error_tool = 'SpotDL' if is_spotify else 'yt-dlp'
        # 限制錯誤訊息長度，避免 GUI 跑版
        stderr_snippet = e.stderr[:500] + ('...' if len(e.stderr) > 500 else '')
        error_message = f"❌ {error_tool} {texts['status_error_exec']} {e.returncode}\n{stderr_snippet}"
        status_callback(error_message, "red")
    except FileNotFoundError:
        status_callback(texts['status_error_not_found'], "red")
    except Exception as e:
        status_callback(f"{texts['status_error_unexpected']} {e}", "red")

# --- 應用程式介面 ---
class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 初始化語言設定 (自動偵測) ---
        detected_lang_code = get_system_language() 
        self.current_lang = detected_lang_code if detected_lang_code in LANG_DATA else 'en'
        
        # 確保中文使用正確的區域代碼
        if self.current_lang == 'zh' and 'zh_TW' in LANG_DATA:
            self.current_lang = 'zh_TW'
        
        # 預設值和路徑
        self.output_dir = get_default_download_path()
        self.current_format_key = 'MP4_VIDEO' # 內部 key
        self.current_quality_key = 'BEST_VIDEO' # 內部 key

        
        # --- GUI 佈局設定 ---
        texts = LANG_DATA[self.current_lang]
        self.title(texts['title'])
        self.geometry("600x560") 
        self.grid_columnconfigure(0, weight=1)
        
        # 獲取下拉選單的值 (使用 'lang_display' 鍵)
        lang_display_values = [data['lang_display'] for data in LANG_DATA.values()]
        initial_lang_display = LANG_DATA[self.current_lang]['lang_display']
        
        # 0. 語言選擇 (Row 0)
        self.lang_frame = ctk.CTkFrame(self)
        self.lang_frame.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")
        self.lang_frame.grid_columnconfigure(0, weight=1)
        
        self.lang_label = ctk.CTkLabel(self.lang_frame, text="") 
        self.lang_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.lang_combobox = ctk.CTkComboBox(
            self.lang_frame, 
            values=lang_display_values, 
            command=self.change_language_callback
        )
        self.lang_combobox.set(initial_lang_display) 
        self.lang_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        

        # 1. 網址輸入框 (Row 1, 2)
        self.url_label = ctk.CTkLabel(self, text="")
        self.url_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        self.url_entry = ctk.CTkEntry(self, width=560)
        self.url_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # 2. 格式選擇 (Row 3, 4)
        self.format_label = ctk.CTkLabel(self, text="")
        self.format_label.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        # 格式的值會在 change_language 中初始化
        self.format_combobox = ctk.CTkComboBox(
            self, 
            values=[], # 初始為空，待 change_language 填充
            command=self.format_changed_callback
        )
        self.format_combobox.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        # 3. 畫質/音質選擇 (Row 5, 6) 
        self.quality_label = ctk.CTkLabel(self, text="") 
        self.quality_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w") 
        # 畫質的值會在 change_language 中初始化
        self.quality_combobox = ctk.CTkComboBox(self, values=[])
        self.quality_combobox.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # 4. 輸出路徑顯示與選擇 (Row 7)
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=7, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        self.path_frame.grid_columnconfigure(1, weight=0)

        self.output_label = ctk.CTkLabel(self.path_frame, text="", anchor="w", justify="left")
        self.output_label.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.browse_button = ctk.CTkButton(self.path_frame, text="", width=80, command=self.select_output_folder)
        self.browse_button.grid(row=0, column=1, sticky="e")

        # 5. 下載按鈕 (Row 8)
        self.download_button = ctk.CTkButton(self, text="", command=self.start_download_thread)
        self.download_button.grid(row=8, column=0, padx=20, pady=20, sticky="ew")
        
        # 6. 狀態列 (Row 9)
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray") 
        self.status_label.grid(row=9, column=0, padx=20, pady=(5, 20), sticky="w")
        
        # 初始化介面文字和選項
        self.change_language(self.current_lang)


    def get_key_from_display(self, display_name, options_dict):
        """根據顯示名稱，反向查找選項的內部 key"""
        for key, value in options_dict.items():
            if value == display_name:
                return key
        # 如果找不到，回傳第一個 key (作為默認值)
        return list(options_dict.keys())[0] if options_dict else None

    def get_display_name_from_key(self, key, options_dict):
        """根據內部 key，獲取選項的顯示名稱"""
        return options_dict.get(key, list(options_dict.values())[0] if options_dict else "")

    def change_language_callback(self, choice_display):
        """處理語言選擇下拉選單的變動"""
        new_lang = None
        # 反向查找語言代碼
        for code, data in LANG_DATA.items():
            if data['lang_display'] == choice_display:
                new_lang = code
                break
        
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.change_language(new_lang)

    def change_language(self, lang_code):
        """根據語言代碼更新介面所有文字和選項"""
        texts = LANG_DATA.get(lang_code, LANG_DATA['en'])
        
        self.title(texts.get('title'))
        
        # 1. 更新標籤和按鈕
        self.lang_label.configure(text=texts['combobox_lang_label'])
        self.url_label.configure(text=texts['url_label'])
        self.format_label.configure(text=texts['format_label'])
        self.browse_button.configure(text=texts['browse_button'])
        self.download_button.configure(text=texts['download_button'])
        
        # 2. 更新格式選項下拉選單
        format_options_dict = texts['options']['formats']
        format_display_values = list(format_options_dict.values())
        self.format_combobox.configure(values=format_display_values)
        
        # 嘗試保持選中的格式 (使用內部 key 查找新的顯示名稱)
        new_display_format = self.get_display_name_from_key(self.current_format_key, format_options_dict)
        self.format_combobox.set(new_display_format)
        
        # 3. 觸發格式回呼，更新畫質/音質標籤和選項
        self.format_changed_callback(new_display_format)

        # 4. 更新輸出路徑顯示和狀態
        self.output_label.configure(text=f"{texts['path_label']} {self.output_dir}")
        self.status_label.configure(text=texts['ready_status'])
        
        # 確保語言下拉選單顯示正確的語言名稱
        self.lang_combobox.set(texts['lang_display'])


    def format_changed_callback(self, choice_display):
        """根據選擇的格式，切換畫質/音質選單的內容和標籤，並更新內部 key"""
        texts = LANG_DATA.get(self.current_lang, LANG_DATA['en'])
        
        # 根據顯示名稱找到對應的內部 format key
        format_options_dict = texts['options']['formats']
        self.current_format_key = self.get_key_from_display(choice_display, format_options_dict)
        
        # 檢查是否為音頻格式
        is_audio = 'AUDIO' in self.current_format_key or 'LOSSLESS' in self.current_format_key

        if is_audio:
            # 切換到音質選項
            self.quality_label.configure(text=texts['quality_audio_label'])
            quality_options_dict = texts['options']['audio_qualities']
            
            # 更新下拉選單
            new_quality_display_values = list(quality_options_dict.values())
            self.quality_combobox.configure(values=new_quality_display_values)
            
            # 嘗試保持選中的音質 (使用內部 key 查找新的顯示名稱)
            if self.current_quality_key not in AUDIO_QUALITY_OPTIONS:
                self.current_quality_key = 'BEST_AUDIO'
            new_display_quality = self.get_display_name_from_key(self.current_quality_key, quality_options_dict)
            self.quality_combobox.set(new_display_quality)

        else:
            # 切換到畫質選項 (視訊)
            self.quality_label.configure(text=texts['quality_video_label'])
            quality_options_dict = texts['options']['video_qualities']

            # 更新下拉選單
            new_quality_display_values = list(quality_options_dict.values())
            self.quality_combobox.configure(values=new_quality_display_values)
            
            # 嘗試保持選中的畫質 (使用內部 key 查找新的顯示名稱)
            if self.current_quality_key not in QUALITY_OPTIONS:
                self.current_quality_key = 'BEST_VIDEO'
            new_display_quality = self.get_display_name_from_key(self.current_quality_key, quality_options_dict)
            self.quality_combobox.set(new_display_quality)


    def select_output_folder(self):
        """開啟資料夾選擇對話框，讓使用者選擇輸出資料夾"""
        texts = LANG_DATA.get(self.current_lang, LANG_DATA['en'])
        folder_selected = filedialog.askdirectory(initialdir=self.output_dir, title=texts['path_label'])
        if folder_selected:
            self.output_dir = folder_selected
            self.output_label.configure(text=f"{texts['path_label']} {self.output_dir}")
            self.update_status(texts['status_path_set'], "blue")

    def update_status(self, message, color="gray"):
        """更新介面上的狀態訊息"""
        # 使用 self.after 確保線程安全地更新 GUI
        self.after(0, self.status_label.configure, {"text": message, "text_color": color})

    def start_download_thread(self):
        """啟動下載線程，並根據網址類型決定使用 yt-dlp 或 spotdl"""
        url = self.url_entry.get().strip().strip('"') 
        texts = LANG_DATA.get(self.current_lang, LANG_DATA['en'])
        
        if not url:
            self.update_status(texts['error_no_url'], "orange")
            return
        
        # 獲取當前下拉選單的顯示名稱，並更新內部的 quality key
        current_quality_display = self.quality_combobox.get()
        is_audio = 'AUDIO' in self.current_format_key or 'LOSSLESS' in self.current_format_key

        if is_audio:
             quality_options_dict = texts['options']['audio_qualities']
             self.current_quality_key = self.get_key_from_display(current_quality_display, quality_options_dict)
        else:
             quality_options_dict = texts['options']['video_qualities']
             self.current_quality_key = self.get_key_from_display(current_quality_display, quality_options_dict)


        self.download_button.configure(state="disabled", text=texts['download_button'])
            
        download_thread = threading.Thread(
            target=download_content, 
            args=(url, self.current_format_key, self.current_quality_key, self.output_dir, self.update_status, self.current_lang)
        )
        download_thread.start()
        self.monitor_thread(download_thread)

    def monitor_thread(self, thread):
        """檢查線程是否結束，並在結束後恢復按鈕"""
        texts = LANG_DATA.get(self.current_lang, LANG_DATA['en'])
        if thread.is_alive():
            self.after(100, lambda: self.monitor_thread(thread))
        else:
            self.download_button.configure(state="normal", text=texts['download_button'])

if __name__ == "__main__":
    # 設定外觀模式和主題
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = DownloaderApp()
    app.mainloop()
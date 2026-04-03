"""
YouTube Transcript Extraction Service
Extracts transcript and title from a YouTube URL.
Primary: youtube-transcript-api v1.2.4+
Fallback: yt-dlp subtitles
"""

import re
import logging
import yt_dlp

logger = logging.getLogger(__name__)

# youtube-transcript-api v1.x — import the class only
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )
except ImportError:
    from youtube_transcript_api import YouTubeTranscriptApi
    NoTranscriptFound = Exception
    TranscriptsDisabled = Exception
    VideoUnavailable = Exception


def extract_video_id(url: str) -> str:
    """
    Extract the 11-character YouTube video ID from any YouTube URL format.
    Raises ValueError if the URL is not a valid YouTube URL.
    """
    patterns = [
        r"(?:youtube\.com/watch\?(?:.*&)?v=)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com/embed/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com/shorts/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com/v/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(
        f"Not a valid YouTube URL: '{url}'. "
        "Please provide a URL like https://www.youtube.com/watch?v=... or https://youtu.be/..."
    )


def get_title_from_ytdlp(video_id: str) -> str:
    """Fetch video title using yt-dlp (no download)."""
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            return info.get("title", f"Video {video_id}")
    except Exception as e:
        logger.warning(f"Could not fetch title via yt-dlp: {e}")
        return f"Video {video_id}"


def get_transcript_from_api(video_id: str) -> str:
    """
    Primary method: uses youtube-transcript-api v1.x API.
    In v1.x: YouTubeTranscriptApi is instantiated, uses .fetch() or .list()
    """
    # v1.x API — instantiate the class
    api = YouTubeTranscriptApi()

    try:
        # Try to list available transcripts and find English
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(["en", "en-US", "en-GB"])
        fetched = transcript.fetch()
    except (NoTranscriptFound, AttributeError):
        # Fallback: fetch directly (auto-generated)
        fetched = api.fetch(video_id)

    # fetched is a FetchedTranscript — iterate to get text
    full_text = " ".join(
        snippet.text.strip() if hasattr(snippet, "text") else snippet["text"].strip()
        for snippet in fetched
    )
    return full_text


def get_transcript_from_ytdlp(video_id: str) -> str:
    """Fallback: download auto-generated subtitles via yt-dlp."""
    import os, tempfile, glob

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        if not vtt_files:
            raise RuntimeError("No subtitle file found via yt-dlp")

        with open(vtt_files[0], "r", encoding="utf-8") as f:
            raw = f.read()

        lines = raw.splitlines()
        text_lines = []
        for line in lines:
            line = line.strip()
            if (
                not line
                or line.startswith("WEBVTT")
                or "-->" in line
                or re.match(r"^\d+$", line)
                or re.match(r"^\d{2}:\d{2}", line)
            ):
                continue
            line = re.sub(r"<[^>]+>", "", line)
            if line:
                text_lines.append(line)

        return " ".join(dict.fromkeys(text_lines))


def extract_youtube_data(url: str) -> dict:
    """
    Main entry point.
    Returns: { video_id, title, transcript, thumbnail_url }
    Raises ValueError for invalid URLs, RuntimeError if transcript unavailable.
    """
    # This will raise ValueError for non-YouTube URLs — caught by app.py as 400
    video_id = extract_video_id(url)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    logger.info(f"Processing video ID: {video_id}")

    # Fetch title
    title = get_title_from_ytdlp(video_id)
    logger.info(f"Video title: {title}")

    # Try primary transcript method
    transcript = None
    try:
        transcript = get_transcript_from_api(video_id)
        logger.info(f"Transcript fetched via youtube-transcript-api ({len(transcript)} chars)")
    except (TranscriptsDisabled, VideoUnavailable, Exception) as e:
        logger.warning(f"Primary transcript failed: {e}. Trying yt-dlp fallback...")
        try:
            transcript = get_transcript_from_ytdlp(video_id)
            logger.info(f"Transcript fetched via yt-dlp ({len(transcript)} chars)")
        except Exception as e2:
            logger.error(f"Both transcript methods failed: {e2}")
            raise RuntimeError(
                f"Could not extract transcript for video '{video_id}'. "
                "The video may not have English captions or subtitles."
            )

    if not transcript or len(transcript.strip()) < 50:
        raise RuntimeError("Transcript is too short or empty to process.")

    return {
        "video_id": video_id,
        "title": title,
        "transcript": transcript,
        "thumbnail_url": thumbnail_url,
    }

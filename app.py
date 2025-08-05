import logging
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (NoTranscriptFound, TranscriptsDisabled,
                                    YouTubeTranscriptApi)

# Configure logging to see output in Railway's logs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="YouTube Transcript Service",
    description="An API to fetch the transcript of a YouTube video.",
    version="2.0.0-workaround",
)


def get_video_id(url: str) -> str | None:
    """Extracts the YouTube video ID from various URL formats."""
    # This function is correct and needs no changes.
    if not url:
        return None
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                query = parse_qs(parsed_url.query)
                return query.get('v', [None])[0]
            if parsed_url.path.startswith(('/embed/', '/v/')):
                return parsed_url.path.split('/')[2]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
    except Exception as e:
        logging.error(f"Error parsing URL '{url}': {e}")
    return None


@app.get("/transcript")
async def get_youtube_transcript(video_url: str):
    """
    Fetches the transcript for a given YouTube video URL.
    NOTE: This version uses a deprecated function as a workaround for a platform issue.
    """
    if not video_url:
        raise HTTPException(
            status_code=400, detail="The 'video_url' query parameter is required.")

    video_id = get_video_id(video_url)
    if not video_id:
        raise HTTPException(
            status_code=400, detail="Could not extract a valid YouTube video ID from the URL.")

    logging.info(f"Processing request for video ID: {video_id} (using deprecated get_transcript)")

    try:
        # === THIS IS THE CRITICAL CHANGE ===
        # We are calling the old .get_transcript() method instead of .list_transcripts()
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # If we get here, it worked. Return the result directly.
        return {"video_id": video_id, "transcript": transcript}

    except TranscriptsDisabled:
        logging.warning(f"Transcripts are disabled for video ID: {video_id}")
        raise HTTPException(
            status_code=403, detail="Transcripts are disabled for this video.")
    except NoTranscriptFound as e:
        logging.warning(f"No transcript found for video ID {video_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"No transcript found for this video: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for video ID {video_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"An internal server error occurred: {str(e)}")


@app.get("/")
async def read_root():
    """A welcome message for the service root."""
    return {"message": "YouTube Transcript API Service (Workaround Active)"}

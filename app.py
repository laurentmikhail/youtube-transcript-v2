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
    version="1.0.0",
)


def get_video_id(url: str) -> str | None:
    """Extracts the YouTube video ID from various URL formats."""
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
    It will prioritize English, Spanish, French, or German transcripts,
    but will fall back to any other available transcript if necessary.
    """
    if not video_url:
        raise HTTPException(
            status_code=400, detail="The 'video_url' query parameter is required.")

    video_id = get_video_id(video_url)
    if not video_id:
        raise HTTPException(
            status_code=400, detail="Could not extract a valid YouTube video ID from the URL.")

    logging.info(f"Processing request for video ID: {video_id}")

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        language_priority = ['en', 'es', 'fr', 'de']
        transcript = None

        for lang in language_priority:
            try:
                transcript = transcript_list.find_transcript([lang])
                logging.info(f"Found prioritized transcript in '{lang}' for video ID: {video_id}")
                break
            except NoTranscriptFound:
                continue
        
        if not transcript:
            logging.warning(
                f"No prioritized transcript found for video ID: {video_id}. "
                "Falling back to the first available transcript."
            )
            first_available = next(iter(transcript_list), None)
            if first_available:
                transcript = first_available

        if not transcript:
            raise NoTranscriptFound("No transcripts were found for this video.")

        fetched_transcript = transcript.fetch()
        logging.info(f"Successfully fetched transcript for video ID: {video_id}")
        
        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "transcript": fetched_transcript
        }

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
    return {"message": "Welcome to the YouTube Transcript API Service. "
                     "Use the /docs endpoint to see API documentation."}

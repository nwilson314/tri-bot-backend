import os
import tempfile

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel
from pydub import AudioSegment
import yt_dlp
from openai import OpenAI

from chatbot.settings import settings

client = OpenAI()
router = APIRouter(
    prefix="/video"
)

ydl_opts = {
    'format': 'm4a/bestaudio/best',  # The best audio version in m4a format
    'outtmpl': 'video/%(id)s.%(ext)s',  # The output name should be the id followed by the extension
    # 'postprocessors': [{  # Extract audio using ffmpeg
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'm4a',
    # }],
}


class VideoTranscribeBody(BaseModel):
    path: str



def split_audio(audio_path, chunk_length_ms=60000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunks.append(audio[i:i + chunk_length_ms])
    return chunks



@router.post("/download_transcribe/")
async def download_transcribe_video(
    body: VideoTranscribeBody
):
    if settings.environment != "dev":
        raise HTTPException(status_code=500, detail="Transcription is only available in development mode")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(body.path, download=False)
        error_code = ydl.download([body.path])

    audio_path = f"video/{info['id']}.{info['ext']}"
    text_file_path = f"data/{info['title']}.txt"

    if not os.path.exists(f"data/{info['title']}.txt"):
        logger.debug(f"No data found for url {body.path} at {text_file_path}. Downloading and transcribing...")
        try:
            audio_chunks = split_audio(audio_path)
        except Exception as e:
            logger.error(f"Error while splitting audio: {e}")
            raise HTTPException(status_code=500, detail="Error while splitting audio")
        

        transcriptions = []
        for i, chunk in enumerate(audio_chunks):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio_file:
                logger.debug("Exporting audio chunk to temporary file...")
                chunk.export(temp_audio_file.name, format="mp3")
                temp_audio_file.seek(0)
                with open(temp_audio_file.name, mode='rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    transcriptions.append(transcription.text)
                os.remove(temp_audio_file.name)

        full_transcription = "\n".join(transcriptions)
        with open(text_file_path, "w") as f:
            f.write(full_transcription)

        return {
            "text": full_transcription
        }
    else:
        logger.debug(f"Data found for url {body.path} at {text_file_path}. Returning data...")
        f = open(f"data/{info['title']}.txt", "r")
        return {
            "text": f.read()
        }


@router.post("/transcribe")
async def transcribe_video(
    body: VideoTranscribeBody
):
    audio_file = open(body.path, mode='rb')
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return {
        "text": transcription.text
    }
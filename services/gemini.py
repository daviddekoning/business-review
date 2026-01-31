"""Gemini API service for PDF and audio processing."""

import os
from pathlib import Path

from google import genai


def get_client() -> genai.Client:
    """Get Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract text content from a PDF file using Gemini."""
    client = get_client()
    file_path = Path(file_path)

    # Upload file to Gemini
    uploaded_file = client.files.upload(file=file_path)

    # Request text extraction
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            uploaded_file,
            "Extract all the text content from this PDF document. "
            "Return only the extracted text, preserving paragraphs and structure. "
            "Do not add any commentary or formatting.",
        ],
    )

    return response.text


def transcribe_audio(file_path: str | Path) -> str:
    """Transcribe audio file using Gemini."""
    client = get_client()
    file_path = Path(file_path)

    # Upload file to Gemini
    uploaded_file = client.files.upload(file=file_path)

    # Request transcription
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            uploaded_file,
            "Transcribe this audio file. Return only the transcription text. "
            "Include speaker labels if multiple speakers are detected (e.g., Speaker 1:, Speaker 2:). "
            "Do not add any commentary.",
        ],
    )

    return response.text

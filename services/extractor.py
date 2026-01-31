"""Content extraction service using Trafilatura."""

import trafilatura


def extract_from_url(url: str) -> str:
    """
    Download and extract main text content from a URL.

    Args:
        url: The URL to extract content from.

    Returns:
        Extracted text or empty string if extraction failed.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded)
            return result or ""
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
    return ""

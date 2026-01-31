"""Tests for the extractor service."""

from unittest.mock import patch, MagicMock
from services import extractor


def test_extract_from_url_success():
    """Test successful extraction from a URL."""
    with patch("trafilatura.fetch_url") as mock_fetch:
        with patch("trafilatura.extract") as mock_extract:
            # Setup mocks
            mock_fetch.return_value = "<html><body><p>Test content</p></body></html>"
            mock_extract.return_value = "Test content"

            # Execute
            result = extractor.extract_from_url("http://example.com")

            # Assert
            assert result == "Test content"
            mock_fetch.assert_called_once_with("http://example.com")
            mock_extract.assert_called_once_with(
                "<html><body><p>Test content</p></body></html>"
            )


def test_extract_from_url_fetch_failed():
    """Test extraction when fetch fails (returns None)."""
    with patch("trafilatura.fetch_url") as mock_fetch:
        mock_fetch.return_value = None

        result = extractor.extract_from_url("http://example.com")

        assert result == ""
        mock_fetch.assert_called_once()


def test_extract_from_url_extract_failed():
    """Test extraction when extract returns None."""
    with patch("trafilatura.fetch_url") as mock_fetch:
        with patch("trafilatura.extract") as mock_extract:
            mock_fetch.return_value = "<html></html>"
            mock_extract.return_value = None

            result = extractor.extract_from_url("http://example.com")

            assert result == ""


def test_extract_from_url_exception():
    """Test extraction when an exception occurs."""
    with patch("trafilatura.fetch_url") as mock_fetch:
        mock_fetch.side_effect = Exception("Network error")

        result = extractor.extract_from_url("http://example.com")

        assert result == ""

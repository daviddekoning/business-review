# Business Analysis Webapp

A web application for structured business analysis, supporting frameworks like Porter's Five Forces and PESTEL. It leverages Google Gemini for AI-assisted insights and allows generating reports.

## Features

- **Business Management**: Track multiple businesses and their strategic details.
- **Research Tracking**: Add research items (PDFs, URLs, text) and highlight quotes.
- **Analysis Frameworks**:
  - Porter's Five Forces
  - PESTEL Analysis
- **AI Integration**: Uses Google Gemini to extract text from files and transcripts.
- **Reporting**: Markdown editor for summaries and PDF export.

## Installation

This project uses `uv` for dependency management.

1.  **Install uv**:
    If you haven't installed `uv` yet, follow the instructions on their [website](https://github.com/astral-sh/uv).
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Sync dependencies**:
    ```bash
    uv sync
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory to configure your environment variables:

    ```env
    GEMINI_API_KEY=your_api_key_here
    SECRET_KEY=your_secret_key
    ```

    - **GEMINI_API_KEY**: Required to use AI features (extracting text from PDFs/URLs, transcribing audio). Get an API key from [Google AI Studio](https://aistudio.google.com/).
    - **SECRET_KEY**: secure session storage.
        - *Development*: Optional (defaults to `dev-secret-key`).
        - *Production*: **Required**. Use a strong random string.

## Usage

To run the application, use `uv run`:

```bash
uv run app.py
```

The application will start at `http://127.0.0.1:5001`.

## Testing

To run the tests:

```bash
uv run pytest
```

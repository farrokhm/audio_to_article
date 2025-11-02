# Audio to Article

This project provides a command-line interface (CLI) to convert audio files into well-structured written articles. The process involves audio transcription, content generation, and final export to both DOCX and PDF formats.

## Project Goal

The primary goal of this project is to automate the conversion of spoken content from audio files into polished, ready-to-publish articles. This is achieved by integrating speech-to-text technology with advanced generative AI models.

## Project Structure

The project is organized as follows:

```
├── .gitignore
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
├── data
│   ├── articles
│   ├── audio_files
│   └── transcripts
├── notebooks
│   └── audio_to_article_via_api.ipynb
├── src
│   └── audio_to_article
│       ├── __init__.py
│       └── main.py
└── tests
    ├── __init__.py
    └── test_main.py
```

- **`data/`**: Contains the input audio files, generated transcripts, and final articles.
- **`notebooks/`**: Jupyter notebooks for experimentation and API exploration.
- **`src/`**: The main source code for the project.
- **`tests/`**: Unit tests for the project.

## Setup

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd audio_to_article
    ```

2.  **Install Poetry:**
    This project uses [Poetry](https://python-poetry.org/) for dependency management. If you don't have Poetry installed, follow the instructions on their official website.

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Create a `.env` file:**
    You need to provide your Google API key in a `.env` file at the root of the project.
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

## Usage

To run the audio-to-article conversion process, execute the following command:

```bash
poetry run python src/audio_to_article/main.py
```

This will:
1.  Transcribe the audio file located at `data/audio_files/AI_Foundation_Model_Selection.mp3`.
2.  Generate a draft article using a generative AI model.
3.  Improve the generated article.
4.  Save the final article as both a `.docx` and `.pdf` file in the `data/articles` directory.

## Testing

To run the test suite, use the following command:

```bash
poetry run pytest
```
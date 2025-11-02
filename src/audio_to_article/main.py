import os
from docx import Document
from dotenv import load_dotenv
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file to text using the Whisper model."""
    import whisper
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    return result["text"]


def ensure_directories(base_path: str, subdirs=None) -> None:
    """Ensure required subdirectories exist under base_path."""
    if subdirs is None:
        subdirs = ("audio_files", "transcripts", "articles")
    for sub in subdirs:
        os.makedirs(os.path.join(base_path, sub), exist_ok=True)


def draft_article(
    transcript: str, foundation_model: str, client, temperature: float = 0.5
) -> str | None:
    """Generate an article draft from a transcript using Google GenAI."""
    try:
        article_draft = client.models.generate_content(
            model=foundation_model,
            config=types.GenerateContentConfig(temperature=temperature),
            contents=f"""Draft an informative, well-structured article with three to five paragraphs based on the following transcript: {transcript}""",
        )
        return article_draft.text
    except Exception as e:
        print(f"An error occurred during article generation: {e}")
        return None


def improve_article(article_text: str, client) -> str:
    """Improve an article's grammar, clarity, and readability."""
    improved_article = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""Improve the following article for grammar, clarity, and readability without shortening it.
        Keep the original title and all section headings exactly as they appear.
        Return only the improved article text — no introductions, explanations, or additional commentary:\n\n{article_text}""",
    )
    return improved_article.text


def export_to_docx(text: str, filename: str):
    """Write plain text into a .docx file."""
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)


def export_to_pdf(text: str, filename: str):
    """Export text to a PDF using ReportLab Platypus Paragraphs."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    formatted_text = text.replace("\n", "<br/>")
    p = Paragraph(formatted_text, styles["Normal"])
    doc.build([p])


def main():
    """Main function to run the audio to article pipeline."""
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    data_path = os.path.join(project_root, "data")
    ensure_directories(data_path)

    file_name = "AI_Foundation_Model_Selection.mp3"
    audio_file_path = os.path.join(data_path, "audio_files", file_name)
    file_name_without_extension, _ = os.path.splitext(file_name)
    transcript_path = os.path.join(
        data_path, "transcripts", file_name_without_extension + "_transcript.txt"
    )

    if os.path.isfile(transcript_path):
        print("The transcript is already extracted and saved.")
        with open(transcript_path, "r", encoding="utf-8") as file:
            transcript = file.read()
        print("The transcript is loaded and ready.")
    else:
        print(f"Transcribing {audio_file_path}...")
        transcript = transcribe_audio(audio_file_path)
        with open(transcript_path, "w", encoding="utf-8") as file:
            file.write(transcript)
        print(f"Transcription is extracted and saved to {transcript_path}")

    print("\n--- Transcript ---")
    print(transcript)

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found. Make sure it is set in your .env file.")
    client = genai.Client(api_key=google_api_key)

    print("\nDrafting article...")
    article_draft_text = draft_article(
        transcript=transcript,
        foundation_model="gemini-2.5-flash",
        temperature=0.4,
        client=client,
    )
    print(article_draft_text)

    print("\nImproving article...")
    improved_article_text = improve_article(article_draft_text, client)
    print(improved_article_text)

    save_directory = os.path.join(data_path, "articles")
    article_base_name = file_name_without_extension + "_article"
    save_article_path = os.path.join(save_directory, article_base_name)

    export_to_docx(improved_article_text, save_article_path + ".docx")
    print(f"Article saved to {save_article_path}.docx")

    export_to_pdf(improved_article_text, save_article_path + ".pdf")
    print(f"Article saved to {save_article_path}.pdf")


if __name__ == "__main__":
    main()
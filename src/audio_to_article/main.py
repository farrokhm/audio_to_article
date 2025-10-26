# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: personal-projects-py3.13
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 🎙️ Audio to Article Notebook
# This notebook lets you:
# 1. Upload an audio file,
# 2. Transcribe speech to text (using Whisper),
# 3. Draft an article from the transcript (via API),
# 4. Improve the article quality (summarization),
# 5. Export the article to **DOCX** and **PDF**,
# 6. Download the exported files directly inside the notebook.

# %% [markdown]
# ### Install Required Libraries

# %%
# # %pip install git+https://github.com/openai/whisper.git torch python-docx reportlab google-genai ipywidgets

# %% [markdown]
# ## 📥 Import Libraries

# %%
import os

import whisper
from docx import Document
from dotenv import load_dotenv
from google import genai
from google.genai import types
from IPython.display import HTML, display
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

# %% [markdown]
# ## 🎧 Step 1: Transcribe Audio


# %%
def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file to text using the Whisper model.

    Args:
        audio_path: Path to the input audio file.

    Returns:
        The transcription as a single string.
    """
    model = whisper.load_model("small")  # choose: tiny, base, small, medium, large
    result = model.transcribe(audio_path)
    return result["text"]


def ensure_directories(base_path: str, subdirs=None) -> None:
    """Ensure required subdirectories exist under base_path."""
    if subdirs is None:
        subdirs = ("audio_files", "transcripts", "articles")
    for sub in subdirs:
        os.makedirs(os.path.join(base_path, sub), exist_ok=True)

project_path = (
    "D:\\Education_Profession\\Projects\\Personal_Projects\\audio_to_article\\"
)

# create required folders if missing
data_path = project_path + "data\\"
ensure_directories(data_path)

file_name = "AI_Foundation_Model_Selection.mp3"
audio_file_path = project_path + "data\\audio_files\\" + file_name

file_name_without_extension, file_extension = os.path.splitext(file_name)
transcript_path = (
    project_path + "data\\transcripts\\" + file_name_without_extension + "_transcript.txt"
)
if os.path.isfile(transcript_path):
    print("The transcript is already extracted and saved.")
    # load the transcript (optional)
    with open(transcript_path, "r", encoding="utf-8") as file:
        transcript = file.read()
    print("The transcript is loaded and ready.")
else:
    transcript = transcribe_audio(audio_file_path)
    # save the transcript (optional)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(transcript)
    print(f"Transcription is extracted and saved to {transcript_path}")

# %% [markdown]
# ### Review the Trascription

# %%
# verifying the draft

# This CSS uses VS Code's theme variables for colors,
# with fallback values for other environments like standard Jupyter.
html_code = f"""
<div style="
    max-height: 300px;
    overflow-y: scroll;
    border: 1px solid var(--vscode-contrastBorder, #e0e0e0);
    padding: 10px;
    color: var(--vscode-editor-foreground, #000000);
    background-color: var(--vscode-editor-background, #ffffff);
">
    {transcript}
</div>
"""

display(HTML(html_code))

# %% [markdown]
# ## ✍️ Step 2: Draft Article

# %%
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found. Make sure it is set in your .env file.")
client = genai.Client(api_key=google_api_key)


def draft_article(transcript: str, foundation_model: str, temperature: float = 0.5):
    """Generate an article draft from a transcript using Google GenAI.

    Args:
        transcript: The transcript text to base the article on.
        foundation_model: Model identifier to use for generation (e.g. "gemini-2.5-flash").
        temperature: Sampling temperature for generation (0.0 - 1.0).

    Returns:
        Generated article text on success, or None on error.
    """
    try:
        article_draft = client.models.generate_content(
            model=foundation_model,
            config=types.GenerateContentConfig(temperature=temperature),
            contents=f"""Draft an informative, well-structured article with three to five paragraphs based on the following transcript: {transcript}""",
        )
        article_draft_text = article_draft.text
        return article_draft_text

    except Exception as e:
        # The function will now handle errors gracefully instead of crashing.
        print(f"An error occurred during article generation: {e}")
        return None


# %%
article_draft_text = draft_article(
    transcript=transcript, foundation_model="gemini-2.5-flash", temperature=0.4
)

# %% [markdown]
# ### Review the article

# %%
html_code = f"""
<div style="
    max-height: 300px;
    overflow-y: scroll;
    border: 1px solid var(--vscode-contrastBorder, #e0e0e0);
    padding: 10px;
    color: var(--vscode-editor-foreground, #000000);
    background-color: var(--vscode-editor-background, #ffffff);
">
    {article_draft_text}
</div>
"""

display(HTML(html_code))

# %% [markdown]
# ## 📝 Step 3: Improve Article

# %%
improved_article = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"Improve the following article for grammar, clarity, and readability without shortening it. \
        Keep the original title and all section headings exactly as they appear. \
        Return only the improved article text — no introductions, explanations, or additional commentary:\n\n{article_draft_text}",
)

# %% [markdown]
# ### Review the improved article

# %%
improved_article_text = improved_article.text
html_code = f"""
<div style="
    max-height: 300px;
    overflow-y: scroll;
    border: 1px solid var(--vscode-contrastBorder, #e0e0e0);
    padding: 10px;
    color: var(--vscode-editor-foreground, #000000);
    background-color: var(--vscode-editor-background, #ffffff);
">
    {improved_article_text}
</div>
"""

display(HTML(html_code))


# %% [markdown]
# ## 💾 Step 4: Export Functions


# %%
def export_to_docx(text: str, filename: str):
    """Write plain text into a .docx file.

    Args:
        text: Text content to write into the document.
        filename: Destination .docx file path.
    """
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)


def export_to_pdf(text: str, filename: str):
    """Export text to a PDF using ReportLab Platypus Paragraphs.

    Produces a simple single-flow PDF that wraps text correctly.

    Args:
        text: Text content to export.
        filename: Destination .pdf file path.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    formatted_text = text.replace("\n", "<br/>")
    p = Paragraph(formatted_text, styles["Normal"])
    doc.build([p])


save_directory = project_path + "data\\articles\\"
file_name = file_name_without_extension + "_article"
save_article_path = os.path.join(save_directory, file_name)

# %%
# Export the article as a MS Word file
export_to_docx(improved_article_text, save_article_path + ".docx")
print(f"The Article is saved correctly to: {save_article_path} as a MS Word file.")

# %%
export_to_pdf(improved_article_text, save_article_path + ".pdf")
print(f"The article is saved correctly to: {save_article_path} as a PDF file.")

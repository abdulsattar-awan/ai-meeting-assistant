# AI Meeting Assistant

Turns a meeting recording into clean, structured meeting notes in a Word file, using **Google Gemini** (audio understanding) and Python.

Works with meetings in English, Urdu or a mix of both. Urdu speech is written in Roman Urdu.

## What it does

```
Recording (audio) → Transcript with timestamps → Summary + Key points + Action items → Word file (.docx)
```

The Word file contains:
- **Summary** of the meeting
- **Key points** as bullet points
- **Action items** table: Task, Owner, Deadline
- **Full transcript** with timestamps

## Features

- Gemini listens to the audio directly, so no separate transcription tool is needed
- Structured notes through Gemini **JSON mode**
- Never invents names or dates: if the meeting did not mention an owner or deadline, it writes "Not mentioned"
- Captures every task discussed, even without an owner or deadline (tested over repeated runs for consistency)
- Retry logic for busy AI servers (503 errors)
- Each run saves a new file with date and time in the name, so older notes are never overwritten

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=your_key_here
```

Put your recording in the folder as `meeting1.mp4` and run:

```bash
python transcribe.py
```

## Privacy

Recordings (`.mp4`, `.m4a`, `.mp3`) and generated notes (`.docx`) are excluded from this repository through `.gitignore`. Always get consent from everyone before recording a meeting.

## Tech

Python, Google Gemini (google-genai), python-docx

## Next steps

- Email the notes automatically through the Gmail API
- Choose the recording file when running the script
- Simple web interface for uploading recordings
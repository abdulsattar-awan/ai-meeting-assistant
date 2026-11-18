import os
import time
from datetime import date, datetime
from docx import Document

from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_gemini(contents, json_mode=False):
    config = None
    if json_mode:
        config = types.GenerateContentConfig(response_mime_type="application/json")
    for attempt in range(1, 6):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Koshish {attempt}: server masroof hai, 20 second ruk kar dobara...")
            time.sleep(20)
    print("5 koshishon ke baad bhi jawab nahi mila.")
    exit()

# 1. Audio file Gemini par upload karo
print("Uploading...")
audio = client.files.upload(
    file="meeting1.mp4",
    config={"mime_type": "audio/mp4"}
)

# 2. Jab tak file tayyar na ho, intezar karo
while audio.state.name != "ACTIVE":
    print("State:", audio.state.name)
    if audio.state.name == "FAILED":
        print("File process nahi ho saki.")
        exit()
    time.sleep(3)
    audio = client.files.get(name=audio.name)

# 3. Transcript maango
transcript = ask_gemini([
    audio,
    "Is meeting recording ka poora transcript likho. "
    "Agar baat Urdu mein hai to Roman Urdu mein likho, sirf English huroof mein. "
    "Har hissay ke shuru mein time stamp likho, jaise 00:00 - 00:08. "
    "Shuru mein koi taaruf ya jumla na likho, seedha transcript do. "
    "Markdown istemal na karo: koi #, *, ** ya --- nahi."
])

print("\n--- TRANSCRIPT ---")
print(transcript)

# 4. Summary aur action items JSON mein maango
notes_text = ask_gemini(
    "Neeche aik meeting ka transcript hai. Is se Roman Urdu (sirf English huroof) mein notes banao. "
    "Jawab sirf is JSON shakal mein do:\n"
    '{"summary": "3-4 lines ka khulasa", '
    '"key_points": ["point 1", "point 2"], '
    '"action_items": [{"task": "kaam", "owner": "kaun karega", "deadline": "kab tak"}]}\n'
    "Har woh kaam jo meeting mein karne ke liye kaha gaya, action_items mein zaroor shamil karo, chahe owner ya deadline na ho.\n"
    "Agar transcript mein naam ya tareekh nahi, to 'Not mentioned' likho. Apni taraf se kuch na banao.\n\n"
    f"TRANSCRIPT:\n{transcript}",
    json_mode=True
)

notes = json.loads(notes_text)

print("\n--- SUMMARY ---")
print(notes["summary"])
print("\n--- ACTION ITEMS ---")
for item in notes["action_items"]:
    print(f"- {item['task']} | {item['owner']} | {item['deadline']}")

# 5. Word file banao
doc = Document()
doc.add_heading("Meeting Notes", level=1)
doc.add_paragraph(f"Date: {date.today()}")

doc.add_heading("Summary", level=2)
doc.add_paragraph(notes["summary"])

doc.add_heading("Key Points", level=2)
for point in notes["key_points"]:
    doc.add_paragraph(point, style="List Bullet")

doc.add_heading("Action Items", level=2)
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"
header = table.rows[0].cells
for i, title in enumerate(["Task", "Owner", "Deadline"]):
    header[i].text = ""
    header[i].paragraphs[0].add_run(title).bold = True
for item in notes["action_items"]:
    row = table.add_row().cells
    row[0].text = item["task"]
    row[1].text = item["owner"]
    row[2].text = item["deadline"]

doc.add_heading("Full Transcript", level=2)
doc.add_paragraph(transcript)

filename = f"meeting_notes_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.docx"
doc.save(filename)
print(f"\nWord file save ho gayi: {filename}")
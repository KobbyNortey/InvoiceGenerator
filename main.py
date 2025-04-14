import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from docxtpl import DocxTemplate
from docx2pdf import convert
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# === CONFIG ===
TEMPLATE_PATH =" " #Absolute Path to Invoice Word Template (.docx)
OUTPUT_FOLDER = "invoices"
LAST_PROCESSED_FILE = "last_timestamp.txt" # replace with absolute Path to file that stores the last processed timestamp
RATE_PER_HOUR = 500 #Replace with your rate per hour
GOOGLE_SHEET_NAME = "Form Responses 1" #Default name; replace with the name of your Google Sheet if different
TIMEZONE = "Africa/Accra"
GOOGLE_CREDENTIALS_FILE = "credentials.json" # replace with absolute path to credentials file


# === GOOGLE SHEETS ===
def get_latest_booking(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(" ") #Replace with the ID of your Google Sheet
    worksheet = sheet.worksheet(sheet_name)
    rows = worksheet.get_all_records()

    latest = rows[-1]
    return { # Replace with the actual column names in your Google Sheet
        "CLIENT_NAME": latest["Booker's Name"],
        "EVENT_NAME": latest["Event Name"],
        "PHONE": latest["Phone Number"],
        "EMAIL": latest["Email Address"],
        "DURATION": float(latest["Duration"]),
        "TIMESTAMP": latest["Timestamp"],
        "EVENT_START": latest["Event Date"]

    }

# === TIMESTAMP TRACKING ===
def get_last_processed_timestamp():
    if os.path.exists(LAST_PROCESSED_FILE):
        with open(LAST_PROCESSED_FILE, "r") as f:
            return f.read().strip()
    return ""

def update_last_processed_timestamp(ts):
    with open(LAST_PROCESSED_FILE, "w") as f:
        f.write(ts)

# === INVOICE ===
def generate_invoice_number(folder):
    existing = [f for f in os.listdir(folder) if f.endswith(".docx")]
    return len(existing) + 1

def fill_template(template_path, output_path, context):
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)

# === GOOGLE CALENDAR ===
def add_event_to_google_calendar(credentials_file, summary, start_time, duration_hours, location=None, description=None):
    scopes = ["https://www.googleapis.com/auth/calendar"]
    credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    service = build("calendar", "v3", credentials=credentials)

    end_time = start_time + timedelta(hours=duration_hours)

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": TIMEZONE,
        },
    }

    event = service.events().insert(calendarId="XXX@group.calendar.google.com", body=event).execute() #Replace with your Google Calendar ID
    print(f"Google Calendar event created: {event.get('htmlLink')}")

# === MAIN ===
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

entry = get_latest_booking(GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_NAME)
last_ts = get_last_processed_timestamp()

if entry["TIMESTAMP"] == last_ts:
    print("No new booking found. Invoice generation skipped.")
else:
    invoice_no = generate_invoice_number(OUTPUT_FOLDER)
    total = int(entry["DURATION"] * RATE_PER_HOUR)

    invoice_context = {
        "INVOICE_NO": invoice_no,
        "CLIENT_NAME": entry["CLIENT_NAME"],
        "EVENT_NAME": entry["EVENT_NAME"],
        "SERVICE_DESC": f"DJ set for {entry['DURATION']} hours",
        "RATE": RATE_PER_HOUR,
        "TOTAL": total,
        "PHONE": entry["PHONE"],
        "EMAIL": entry["EMAIL"]
    }

    safe_name = "".join(c if c.isalnum() else "_" for c in entry["CLIENT_NAME"])
    output_filename = f"invoice_{invoice_no}_{safe_name}.docx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    fill_template(TEMPLATE_PATH, output_path, invoice_context)

    # Convert to PDF
    pdf_output_path = output_path.replace(".docx", ".pdf")
    convert(output_path, pdf_output_path)
    print(f"PDF saved: {pdf_output_path}")

    # Add to Google Calendar
    event_title = f"DJ for {entry['EVENT_NAME']} - {entry['CLIENT_NAME']}"
    event_start_time = datetime.strptime(entry["EVENT_START"], "%m/%d/%Y %H:%M:%S")

    add_event_to_google_calendar(
        GOOGLE_CREDENTIALS_FILE,
        summary=event_title,
        start_time=event_start_time,
        duration_hours=entry["DURATION"],
        location=None,
        description=f"Booking for {entry['CLIENT_NAME']} ({entry['EMAIL']})"
    )

    update_last_processed_timestamp(entry["TIMESTAMP"])
    print(f"Invoice generated: {output_path}")

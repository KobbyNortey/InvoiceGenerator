
# DJ Booking Automation Script

A Python script that automates the workflow for DJ bookings via Google Forms. It generates customized invoices in Word and PDF format and automatically schedules the event in Google Calendar.

---

## Features

- Reads booking data from Google Sheets (submitted via Google Form)
- Generates personalized invoices in `.docx` and `.pdf`
- Adds booking to a specified Google Calendar
- Skips duplicates using a timestamp log
- Automatable via cron (runs every 5 minutes)

---

## Project Structure

```
pythonProject1/
├── main.py                  # Main script
├── credentials.json         # Google service account credentials (DO NOT SHARE)
├── requirements.txt         # List of required Python packages
├── Invoice_Template.docx  # Word template for invoices
├── invoices/                # Output folder for generated invoices
├── last_timestamp.txt       # Tracks last processed form submission
```

---

## Setup Instructions


### 1. Google Cloud Setup

1. Go to Google Cloud Console
2. Enable:
    - Google Sheets API
    - Google Calendar API
3. Create a Service Account
4. Download the `.json` credentials and rename it to `credentials.json`
5. Share your target Google Sheet and Calendar with the service account email

---

### 2. Google Form Setup

Ensure your Google Form (linked to your Google Sheet) includes the following columns:

- `Timestamp`
- `Booker's Name`
- `Event Name`
- `Phone Number`
- `Email Address`
- `Duration`
- `Event Date` (Format: `MM/DD/YYYY HH:MM:SS`)

---

### 3. Configure Paths (if needed)

Update the following variables in `main.py` to reflect your environment:

```python
TEMPLATE_PATH = "/absolute/path/to/Invoice_Template.docx"
OUTPUT_FOLDER = "/absolute/path/to/invoices"
GOOGLE_CREDENTIALS_FILE = "/absolute/path/to/credentials.json"
```

---

### 4. Run the Script

```bash
python main.py
```

Or schedule it every 5 minutes using cron:

```bash
crontab -e
```

Then add:
```cron
*/5 * * * * /path/to/.venv/bin/python /path/to/main.py >> /path/to/log_file 2>&1
```

---

## Customizing the Invoice

Edit the `Invoice_Template.docx` file using Microsoft Word. Use `{{PLACEHOLDER}}` syntax for:

- `{{INVOICE_NO}}`
- `{{DATE}}`
- `{{CLIENT_NAME}}`
- `{{EVENT_NAME}}`
- `{{RATE}}`
- `{{TOTAL}}`

These will be automatically filled using `docxtpl`.

---

## Security

- Do not commit `credentials.json` to version control
- Add it to `.gitignore`
- Revoke and regenerate credentials if accidentally exposed

---

## Future Improvements

- Automatic email delivery of invoices
- Web dashboard for viewing bookings

---

## Acknowledgments

Developed by Shawn Owusu-Nortey  
Built with Python and Google Cloud Platform

---

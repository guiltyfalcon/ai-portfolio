# Google Sheets Integration for Email Capture

## Quick Setup (5 minutes)

### Option 1: Google Apps Script (Easiest - No API Keys)

1. **Create a new Google Sheet:**
   - Go to sheets.google.com
   - Create new sheet named "BetBrain Waitlist"
   - Add headers in row 1: `Timestamp`, `Email`, `Source`, `IP`

2. **Add Apps Script webhook:**
   - In the sheet, go to **Extensions → Apps Script**
   - Paste this code:

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  
  sheet.appendRow([
    new Date(),
    data.email,
    data.source || 'landing-page',
    data.ip || 'unknown'
  ]);
  
  return ContentService
    .createTextOutput(JSON.stringify({success: true}))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({status: 'active'}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

3. **Deploy as webhook:**
   - Click **Deploy → New deployment**
   - Select type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click **Deploy**
   - Copy the Web app URL

4. **Update webhook.py:**
   - Replace `GOOGLE_SHEETS_WEBHOOK_URL` with your URL
   - Or set env var: `GOOGLE_SHEETS_WEBHOOK_URL=https://script.google.com/...`

### Option 2: Service Account (More Control)

1. **Create Google Cloud Project:**
   - Go to console.cloud.google.com
   - Create new project
   - Enable Google Sheets API

2. **Create Service Account:**
   - IAM & Admin → Service Accounts
   - Create service account
   - Download JSON key file

3. **Share Sheet with Service Account:**
   - Copy service account email (ends with @.iam.gserviceaccount.com)
   - Share your Google Sheet with that email (Editor access)

4. **Install gspread:**
   ```bash
   pip install gspread
   ```

5. **Update webhook.py:**
   - Uncomment the gspread code
   - Add path to your service account JSON key

---

## Testing

```bash
# Test the webhook locally
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

Check the JSON file:
```bash
cat /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/email-capture/waitlist_emails.json
```

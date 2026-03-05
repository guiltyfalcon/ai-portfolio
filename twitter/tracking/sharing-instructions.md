# BetBrain AI - Public Sharing Instructions

## Overview
This guide walks you through publishing your BetBrain pick tracking spreadsheet for public viewing, creating a shareable short URL, and embedding it on your website or landing page.

---

## Part 1: Google Sheets Public Sharing Settings

### Step 1: Open Your Spreadsheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Open your BetBrain Pick Tracker spreadsheet

### Step 2: Access Share Settings
1. Click the **"Share"** button in the top-right corner (green button with person icon)
2. OR go to **File → Share → Share with others**

### Step 3: Configure General Access
1. Under **"General access"**, click the dropdown (default: "Restricted")
2. Select **"Anyone with the link"**

### Step 4: Set Permission Level
1. In the role dropdown next to "Anyone with the link", select **"Viewer"**
2. ⚠️ **IMPORTANT:** Do NOT select "Editor" or "Commenter" - this is public-facing

### Step 5: Disable Editing Options
1. Click the **gear icon (⚙️)** next to the share button
2. **UNCHECK** the following:
   - ☐ Editors can change permissions and share
   - ☐ Viewers can see the option to download, print, and copy
   - ☐ Viewers can comment
3. Click **Save**

### Step 6: Copy the Link
1. Click **"Copy link"** button
2. The link will look like:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123xyz789/edit?usp=sharing
   ```

### Step 7: Verify Public Access
1. Open an **Incognito/Private browser window**
2. Paste the link
3. Confirm you can view but NOT edit the spreadsheet
4. If you can edit, return to Step 4

---

## Part 2: Creating a Short URL (bit.ly)

### Option A: bit.ly (Recommended)

#### Step 1: Create Account
1. Go to [bit.ly](https://bit.ly)
2. Click **"Sign Up"** (free account recommended for analytics)
3. Complete registration

#### Step 2: Create Short Link
1. Click **"Create new"** or **"+"** button
2. Paste your Google Sheets long URL into the destination field
3. Click **"Customize"** (optional but recommended)
4. Set custom back-half:
   ```
   betbrain-tracker
   betbrain-picks
   betbrain-live
   ```
5. Click **"Create"**

#### Step 3: Your Short URL
```
https://bit.ly/betbrain-tracker
```

#### Step 4: Test the Link
1. Click your new short link
2. Verify it redirects to the Google Sheet
3. Test on mobile device

### Option B: Alternative URL Shorteners

| Service | URL | Notes |
|---------|-----|-------|
| TinyURL | https://tinyurl.com | No account needed |
| Rebrandly | https://rebrandly.com | Custom domain options |
| Short.io | https://short.io | Good for teams |
| Ow.ly | https://ow.ly | Hootsuite integration |

---

## Part 3: Embed Code for Website/Landing Page

### Method 1: Google Sheets Native Embed (IFrame)

#### Step 1: Get Embed Code from Google Sheets
1. In your spreadsheet, go to **File → Share → Publish to web**
2. In the dialog, click **"Embed"** tab (not "Link")
3. Select which sheet to publish (usually "Dashboard" or "Picks Log")
4. Choose interaction level:
   - ☑ Interactive (allows sorting/filtering)
   - ☐ Static (image-like, no interaction)
5. Click **"Publish"**
6. Confirm by clicking **"OK"**
7. Copy the iframe code provided

#### Step 2: Example Embed Code
```html
<iframe src="https://docs.google.com/spreadsheets/d/1ABC123xyz789/pubhtml?widget=true&headers=false" 
        width="100%" 
        height="600" 
        frameborder="0" 
        scrolling="no">
</iframe>
```

#### Step 3: Customize Dimensions
- **Width:** Use `100%` for responsive design or fixed pixels (e.g., `800`)
- **Height:** Adjust based on content (600-800px recommended for dashboard)

### Method 2: Responsive Embed with Container

```html
<div style="position: relative; padding-bottom: 75%; height: 0; overflow: hidden; max-width: 100%;">
  <iframe src="https://docs.google.com/spreadsheets/d/1ABC123xyz789/pubhtml?widget=true&headers=false" 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
          frameborder="0" 
          scrolling="no">
  </iframe>
</div>
```

### Method 3: Direct Link Button (Alternative to Embed)

```html
<a href="https://bit.ly/betbrain-tracker" 
   target="_blank" 
   rel="noopener noreferrer"
   style="background-color: #0F9D58; color: white; padding: 12px 24px; 
          text-decoration: none; border-radius: 4px; font-weight: bold; 
          display: inline-block; margin: 20px 0;">
  📊 View Live Pick Tracker
</a>
```

### Method 4: Styled Card with Embed

```html
<div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; 
            margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h3 style="margin-top: 0; color: #333;">🏆 BetBrain AI - Live Performance</h3>
  <p style="color: #666; margin-bottom: 15px;">
    Track our AI's real-time betting performance with full transparency.
  </p>
  <iframe src="https://docs.google.com/spreadsheets/d/1ABC123xyz789/pubhtml?widget=true&headers=false" 
          width="100%" 
          height="500" 
          frameborder="0" 
          scrolling="no"
          style="border: 1px solid #eee; border-radius: 4px;">
  </iframe>
  <p style="text-align: center; margin-top: 15px; color: #999; font-size: 12px;">
    Updated in real-time • <a href="https://bit.ly/betbrain-tracker" target="_blank">Open full tracker</a>
  </p>
</div>
```

---

## Part 4: Platform-Specific Integration

### WordPress

#### Using Gutenberg Block Editor
1. Add a **"Custom HTML"** block
2. Paste your embed code
3. Preview and publish

#### Using Elementor
1. Add an **"HTML"** widget
2. Paste embed code
3. Adjust widget width as needed

#### Using Classic Editor
1. Switch to **"Text"** tab (not Visual)
2. Paste embed code
3. Switch back to Visual to verify

### Webflow
1. Add an **"Embed"** element
2. Paste iframe code
3. Adjust dimensions in element settings

### Squarespace
1. Add a **"Code"** block
2. Paste embed code
3. Set block to full-width if needed

### Wix
1. Add an **"HTML iframe"** element
2. Paste embed code
3. Resize the element box

### Custom HTML Site
1. Paste embed code where you want it to appear
2. Ensure responsive CSS is applied
3. Test on mobile devices

### Landing Page Builders

**Carrd:**
- Use "Embed" element
- Paste iframe code

**ConvertKit:**
- Use "Custom HTML" block
- Note: Some restrictions may apply

**Leadpages:**
- Use "HTML" widget
- Full support for iframes

---

## Part 5: Social Media Sharing

### Twitter/X
```
📊 BetBrain AI Pick Tracker - LIVE

Transparent, real-time tracking of all our AI's betting picks.

✅ Win/Loss record
✅ ROI %
✅ Sport breakdown
✅ Current streak

👉 https://bit.ly/betbrain-tracker

#SportsBetting #AI #BetBrain
```

### Instagram (Link in Bio)
```
🔗 LINK IN BIO: Live Pick Tracker

Track every BetBrain AI pick in real-time with full transparency.

• Total picks & win rate
• ROI by sport
• Profit/loss tracking
• AI confidence scores

No BS. Just results. 📈
```

### Discord
```
**📊 BetBrain Live Tracker**

Check out our real-time pick tracking spreadsheet!

<https://bit.ly/betbrain-tracker>

Updated after every game. Full transparency on all AI picks.
```

### Telegram
```
📊 *BetBrain AI - Live Pick Tracker*

Transparent tracking of all our AI betting picks:

• Win/Loss record
• ROI percentage  
• Sport-by-sport breakdown
• Current streak

🔗 https://bit.ly/betbrain-tracker

_Updated in real-time_
```

---

## Part 6: Best Practices

### ✅ DO:
- Set permissions to "Viewer" only
- Test public access in incognito mode
- Use a custom short URL for branding
- Add UTM parameters for tracking:
  ```
  https://bit.ly/betbrain-tracker?utm_source=twitter&utm_medium=social
  ```
- Update the spreadsheet regularly
- Pin the link in social media profiles
- Add a "Last Updated" timestamp to your dashboard

### ❌ DON'T:
- Allow editing or commenting access
- Share the original edit link
- Use the raw Google Sheets URL (too long)
- Forget to test on mobile
- Embed without responsive styling
- Share before verifying privacy settings

---

## Part 7: Analytics & Tracking

### Google Sheets Built-in Analytics
1. Go to **File → Version history → See version history**
2. Track view counts indirectly through edit frequency

### bit.ly Analytics
1. Log into bit.ly dashboard
2. Click on your link
3. View:
   - Total clicks
   - Clicks by date
   - Geographic data
   - Referrer sources
   - Device types

### Add UTM Parameters
```
https://bit.ly/betbrain-tracker?utm_source=twitter&utm_medium=social&utm_campaign=tracker_launch
```

### Google Analytics (if embedding on your site)
Track iframe interactions with event tracking:
```javascript
// Track when users scroll to tracker
gtag('event', 'view', {
  'event_category': 'Tracker',
  'event_label': 'BetBrain Spreadsheet'
});
```

---

## Part 8: Maintenance & Updates

### Weekly Checklist
- [ ] Verify link still works
- [ ] Check sharing settings haven't changed
- [ ] Update any outdated picks
- [ ] Review analytics for traffic sources
- [ ] Test on mobile device

### Monthly Checklist
- [ ] Archive old picks (optional)
- [ ] Review and update formulas if needed
- [ ] Check bit.ly link performance
- [ ] Update embed code if Google changes format
- [ ] Backup spreadsheet (File → Download → .xlsx)

### Quarterly Checklist
- [ ] Full audit of sharing permissions
- [ ] Review analytics and optimize promotion
- [ ] Update short URL if rebranding
- [ ] Test all embedded locations
- [ ] Create fresh backup copy

---

## Part 9: Troubleshooting

| Issue | Solution |
|-------|----------|
| "Access Denied" error | Re-check sharing settings, ensure "Anyone with link" is selected |
| Embed not showing | Verify "Publish to web" was completed (different from Share) |
| Link not shortening | Try alternative shortener or check bit.ly account status |
| Mobile display issues | Use responsive embed code with percentage widths |
| Slow loading | Consider publishing only Dashboard sheet, not full workbook |
| Can't publish to web | Check Google Workspace admin settings (if using work account) |
| Embed shows login screen | Ensure you published via File → Publish to web, not just shared |

---

## Part 10: Quick Reference

### Your Links (Fill In After Setup)

| Type | URL | Purpose |
|------|-----|---------|
| **Original Sheet** | `https://docs.google.com/spreadsheets/d/XXXXXXXXXXX/edit` | Your edit access |
| **Public View Link** | `https://docs.google.com/spreadsheets/d/XXXXXXXXXXX/view?usp=sharing` | Direct public access |
| **Short URL** | `https://bit.ly/betbrain-tracker` | Social media sharing |
| **Embed Code** | See Method 1 above | Website integration |

### Quick Commands

**Revoke Public Access:**
1. File → Share
2. Click "Anyone with the link"
3. Change to "Restricted"

**Update Published Version:**
- Changes publish automatically (no action needed)

**Change Published Sheet:**
1. File → Share → Publish to web
2. Select different sheet from dropdown
3. Click "Republish"

---

## Security Checklist

Before going public, verify:

- [ ] No personal information in spreadsheet
- [ ] No private notes visible in shared view
- [ ] Permission set to "Viewer" (not Editor/Commenter)
- [ ] Download/copy/print disabled (optional but recommended)
- [ ] Comments disabled
- [ ] Tested in incognito window
- [ ] No sensitive formulas exposed
- [ ] Backup created before publishing

---

## Support Resources

- **Google Sheets Help:** https://support.google.com/docs
- **bit.ly Help:** https://support.bit.ly.com
- **Embed Troubleshooting:** https://developers.google.com/chart/interactive/docs/basic_load_libs

---

*Last Updated: 2026-03-05*
*Version: 1.0*

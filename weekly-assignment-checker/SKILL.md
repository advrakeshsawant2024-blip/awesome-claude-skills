---
name: weekly-assignment-checker
description: Sets up a macOS automation that searches Gmail every Saturday at 9 AM for new assignments and creates high-priority reminders in a "Drafting and Correspondence" list with 3-day due dates and 2-day-before alerts.
---

# Weekly Assignment Checker

This skill creates and installs a macOS automation that monitors Gmail for assignment-related emails and automatically creates structured reminders so nothing falls through the cracks.

## When to Use This Skill

- Setting up automated assignment tracking from email
- Keeping a "Drafting and Correspondence" reminders list populated without manual effort
- Creating a recurring Saturday-morning digest of new assignments
- Ensuring follow-up reminders exist for every incoming assignment email

## What This Skill Does

1. **Creates the Node.js script** (`~/weekly-assignment-checker.js`) that:
   - Authenticates with Gmail via OAuth2
   - Searches the last 7 days of email for assignment keywords
   - Parses sender, subject, and snippet from each matching email
   - Creates a macOS Reminder via AppleScript in the "Drafting and Correspondence" list with:
     - Due date 3 days from today
     - High priority
     - Sender and email details in notes
     - Alert 2 days before the due date

2. **Creates the LaunchAgent plist** (`~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist`) that:
   - Schedules the script every Saturday at 9:00 AM
   - Routes stdout and stderr to log files under `~/Library/Logs/`

3. **Walks the user through loading and verifying** the LaunchAgent

## Instructions

When the user invokes this skill:

### Step 1 — Check prerequisites

Run the following and report results:

```bash
node --version 2>/dev/null || echo "Node.js not found"
```

If Node.js is missing, tell the user:
```
Node.js is required. Install it with:
  brew install node
Then re-run this skill.
```

If Node.js is present, continue.

### Step 2 — Create the script file

Write `~/weekly-assignment-checker.js` with the contents below. Use `~` expansion via `$HOME`.

```javascript
#!/usr/bin/env node
/**
 * Weekly Assignment Checker
 * Searches Gmail for assignment-related emails and creates macOS Reminders.
 * Runs via LaunchAgent every Saturday at 9 AM.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

const LOG_FILE = path.join(process.env.HOME, 'Library', 'Logs', 'weekly-assignment-checker.log');
const TOKEN_FILE = path.join(process.env.HOME, '.weekly-assignment-checker-token.json');
const CREDENTIALS_FILE = path.join(process.env.HOME, '.weekly-assignment-checker-credentials.json');

const ASSIGNMENT_KEYWORDS = [
  'assignment', 'task', 'action item', 'deliverable', 'due date',
  'deadline', 'please complete', 'please review', 'follow up',
  'action required', 'your input', 'please respond'
];

const REMINDER_LIST = 'Drafting and Correspondence';
const DUE_DAYS = 3;
const ALERT_DAYS_BEFORE = 2;

function log(message) {
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_FILE, line);
  process.stdout.write(line);
}

function getDateString(daysFromNow) {
  const d = new Date();
  d.setDate(d.getDate() + daysFromNow);
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

function escapeForAppleScript(str) {
  return (str || '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function createReminder({ title, notes }) {
  const dueDate = getDateString(DUE_DAYS);
  const alertDate = getDateString(DUE_DAYS - ALERT_DAYS_BEFORE);

  const script = `
    tell application "Reminders"
      tell list "${REMINDER_LIST}"
        set newReminder to make new reminder with properties {¬
          name:"${escapeForAppleScript(title)}",¬
          body:"${escapeForAppleScript(notes)}",¬
          due date:date "${dueDate}",¬
          priority:1}
        set remind me date of newReminder to date "${alertDate}"
      end tell
    end tell
  `;

  try {
    execSync(`osascript -e '${script.replace(/'/g, "'\\''")}'`);
    log(`Created reminder: ${title}`);
  } catch (err) {
    log(`Failed to create reminder "${title}": ${err.message}`);
  }
}

function httpsGet(url, headers) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`JSON parse error: ${data}`)); }
      });
    });
    req.on('error', reject);
  });
}

function refreshAccessToken(credentials, token) {
  return new Promise((resolve, reject) => {
    const body = new URLSearchParams({
      client_id: credentials.installed.client_id,
      client_secret: credentials.installed.client_secret,
      refresh_token: token.refresh_token,
      grant_type: 'refresh_token',
    }).toString();

    const options = {
      hostname: 'oauth2.googleapis.com',
      path: '/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.error) reject(new Error(result.error_description || result.error));
          else resolve(result.access_token);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function searchGmail(accessToken) {
  const sevenDaysAgo = Math.floor((Date.now() - 7 * 24 * 60 * 60 * 1000) / 1000);
  const query = encodeURIComponent(
    `(${ASSIGNMENT_KEYWORDS.map(k => `"${k}"`).join(' OR ')}) after:${sevenDaysAgo}`
  );
  const url = `https://gmail.googleapis.com/gmail/v1/users/me/messages?q=${query}&maxResults=20`;

  const headers = { Authorization: `Bearer ${accessToken}` };
  const listResult = await httpsGet(url, headers);

  if (!listResult.messages || listResult.messages.length === 0) {
    log('No assignment-related emails found in the last 7 days.');
    return [];
  }

  const emails = [];
  for (const msg of listResult.messages) {
    const detail = await httpsGet(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject`,
      headers
    );

    const headers_ = detail.payload?.headers || [];
    const subject = headers_.find(h => h.name === 'Subject')?.value || '(no subject)';
    const from = headers_.find(h => h.name === 'From')?.value || '(unknown sender)';
    const snippet = detail.snippet || '';

    emails.push({ subject, from, snippet, id: msg.id });
  }

  return emails;
}

async function main() {
  log('Weekly Assignment Checker starting...');

  if (!fs.existsSync(CREDENTIALS_FILE)) {
    log(`ERROR: Credentials file not found at ${CREDENTIALS_FILE}`);
    log('Please follow the setup instructions to configure Gmail OAuth2 credentials.');
    process.exit(1);
  }

  if (!fs.existsSync(TOKEN_FILE)) {
    log(`ERROR: Token file not found at ${TOKEN_FILE}`);
    log('Please run the OAuth2 authorization flow first. See setup instructions.');
    process.exit(1);
  }

  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_FILE, 'utf8'));
  const token = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));

  let accessToken;
  try {
    accessToken = await refreshAccessToken(credentials, token);
    log('Access token refreshed successfully.');
  } catch (err) {
    log(`ERROR refreshing access token: ${err.message}`);
    process.exit(1);
  }

  let emails;
  try {
    emails = await searchGmail(accessToken);
  } catch (err) {
    log(`ERROR searching Gmail: ${err.message}`);
    process.exit(1);
  }

  log(`Found ${emails.length} assignment-related email(s).`);

  for (const email of emails) {
    createReminder({
      title: `Assignment: ${email.subject}`,
      notes: `From: ${email.from}\n\nPreview: ${email.snippet}`,
    });
  }

  log('Weekly Assignment Checker finished.');
}

main().catch((err) => {
  log(`Unhandled error: ${err.message}`);
  process.exit(1);
});
```

### Step 3 — Create the LaunchAgent plist

Write `~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist`. Create the directory if it doesn't exist.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.user.weekly-assignment-checker</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/bin/node</string>
      <string>/Users/REPLACE_WITH_USERNAME/weekly-assignment-checker.js</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
      <key>Weekday</key>
      <integer>6</integer>
      <key>Hour</key>
      <integer>9</integer>
      <key>Minute</key>
      <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/REPLACE_WITH_USERNAME/Library/Logs/weekly-assignment-checker.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/REPLACE_WITH_USERNAME/Library/Logs/weekly-assignment-checker-error.log</string>

    <key>RunAtLoad</key>
    <false/>
  </dict>
</plist>
```

**Important**: Before writing the plist, detect the actual username and Node.js path:

```bash
echo $USER
which node
```

Replace `REPLACE_WITH_USERNAME` with the real username and `/usr/local/bin/node` with the real Node.js path in the plist.

### Step 4 — Make script executable

```bash
chmod +x ~/weekly-assignment-checker.js
```

### Step 5 — Set up Gmail OAuth2 credentials

Explain to the user that the script requires Gmail API access and walk them through:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project (or use an existing one)
2. Enable the **Gmail API** for the project
3. Create **OAuth 2.0 credentials** (Desktop app type)
4. Download the JSON credentials file and save it to `~/.weekly-assignment-checker-credentials.json`
5. Run the one-time authorization flow:

```bash
node -e "
const { execSync } = require('child_process');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const CREDENTIALS_FILE = path.join(process.env.HOME, '.weekly-assignment-checker-credentials.json');
const TOKEN_FILE = path.join(process.env.HOME, '.weekly-assignment-checker-token.json');
const SCOPES = 'https://www.googleapis.com/auth/gmail.readonly';

const creds = JSON.parse(fs.readFileSync(CREDENTIALS_FILE, 'utf8')).installed;
const redirectUri = 'http://localhost:3000/oauth2callback';

const authUrl = 'https://accounts.google.com/o/oauth2/v2/auth?' +
  new URLSearchParams({
    client_id: creds.client_id,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: SCOPES,
    access_type: 'offline',
    prompt: 'consent',
  });

console.log('Open this URL in your browser:\\n' + authUrl);

const server = http.createServer((req, res) => {
  const code = new url.URL(req.url, 'http://localhost:3000').searchParams.get('code');
  if (!code) { res.end('No code found'); return; }
  res.end('Authorization successful! You can close this tab.');
  server.close();

  const body = new URLSearchParams({
    code, client_id: creds.client_id, client_secret: creds.client_secret,
    redirect_uri: redirectUri, grant_type: 'authorization_code',
  }).toString();

  const reqOpts = {
    hostname: 'oauth2.googleapis.com', path: '/token', method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) },
  };
  const tokenReq = https.request(reqOpts, (tokenRes) => {
    let data = '';
    tokenRes.on('data', c => data += c);
    tokenRes.on('end', () => {
      fs.writeFileSync(TOKEN_FILE, data);
      console.log('Token saved to ' + TOKEN_FILE);
    });
  });
  tokenReq.write(body);
  tokenReq.end();
}).listen(3000);
"
```

### Step 6 — Load the LaunchAgent

```bash
mkdir -p ~/Library/LaunchAgents
launchctl load ~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist
```

Verify it loaded:
```bash
launchctl list | grep weekly-assignment-checker
```

### Step 7 — Test the script manually (optional)

```bash
node ~/weekly-assignment-checker.js
tail -20 ~/Library/Logs/weekly-assignment-checker.log
```

### Step 8 — Confirm the "Drafting and Correspondence" list exists

If the Reminders list doesn't exist yet, the script will error. Tell the user to open **Reminders.app** and create a list named exactly:

```
Drafting and Correspondence
```

### Step 9 — Report completion

Summarize what was created:

```
Setup complete!

Files created:
  ~/weekly-assignment-checker.js          — main script
  ~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist — scheduler

Next steps:
  1. Complete Gmail OAuth2 setup (credentials + token)
  2. Ensure "Drafting and Correspondence" list exists in Reminders.app
  3. The script will run automatically every Saturday at 9:00 AM

To run it now:
  node ~/weekly-assignment-checker.js

To check logs:
  tail -f ~/Library/Logs/weekly-assignment-checker.log
```

## Troubleshooting Guide

Provide this if the user reports issues:

| Symptom | Cause | Fix |
|---|---|---|
| Script doesn't run Saturday | Mac was asleep/off | Enable "Wake for network access" in Energy Saver |
| `node: command not found` | Wrong Node path in plist | Run `which node` and update plist ProgramArguments |
| `ERROR: Credentials file not found` | OAuth credentials missing | Complete Step 5 above |
| `ERROR refreshing access token` | Token expired or revoked | Re-run the OAuth flow in Step 5 |
| Reminders not created | List name mismatch | Verify Reminders list is named exactly "Drafting and Correspondence" |
| `Permission denied` | Script not executable | Run `chmod +x ~/weekly-assignment-checker.js` |

To unload the scheduler:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist
```

To reload it:
```bash
launchctl load ~/Library/LaunchAgents/com.user.weekly-assignment-checker.plist
```

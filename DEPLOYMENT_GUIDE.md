# 24/7 Deployment Guide - UAE Investor Research Agent

This guide shows you how to run the investor research agent continuously in the cloud.

---

## 🎯 Deployment Options

### Option 1: GitHub Actions (FREE - Recommended)
Run automatically on a schedule, no server needed.

### Option 2: AWS Lambda (Pay-per-use)
Serverless, scales automatically, only pay when running.

### Option 3: Railway/Render (Always-on)
Simple deployment, runs continuously.

### Option 4: Local Cron Job (Free)
Run on your own computer on a schedule.

---

## ⭐ OPTION 1: GitHub Actions (Easiest + Free)

### Step 1: Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create uae-investor-agent --public
git push -u origin main
```

### Step 2: Add API Key as Secret
1. Go to your repo on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your API key
6. Click "Add secret"

### Step 3: Create Workflow File
Create `.github/workflows/investor-research.yml`:

```yaml
name: UAE Investor Research

on:
  schedule:
    # Runs every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch: # Manual trigger

jobs:
  research:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install anthropic
    
    - name: Run investor research
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        python uae_investor_agent.py
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: investor-data
        path: uae_investors_research.csv
    
    - name: Commit and push if changed
      run: |
        git config --global user.name 'GitHub Action'
        git config --global user.email 'action@github.com'
        git add -A
        git diff --quiet && git diff --staged --quiet || (git commit -m "Update investor data" && git push)
```

### Step 4: Add Google Sheets Integration
Install GitHub Action for Google Sheets:

```yaml
    - name: Update Google Sheets
      uses: jroehl/gsheet.action@v2.0.0
      with:
        spreadsheetId: ${{ secrets.SPREADSHEET_ID }}
        commands: |
          [
            {
              "command": "updateData",
              "args": {
                "data": "${{ steps.read-csv.outputs.data }}",
                "minCol": 1,
                "minRow": 1
              }
            }
          ]
      env:
        GSHEET_CLIENT_EMAIL: ${{ secrets.GSHEET_CLIENT_EMAIL }}
        GSHEET_PRIVATE_KEY: ${{ secrets.GSHEET_PRIVATE_KEY }}
```

**Benefits:**
- ✅ Completely free
- ✅ Runs on schedule automatically
- ✅ Can push directly to Google Sheets
- ✅ Version control for all data
- ✅ No server management

---

## 🚀 OPTION 2: AWS Lambda (Serverless)

### Step 1: Create Lambda Function
Create `lambda_handler.py`:

```python
import json
import boto3
import os
from uae_investor_agent import UAEInvestorResearchAgent

def lambda_handler(event, context):
    """
    AWS Lambda handler for investor research.
    Triggered by EventBridge on schedule.
    """
    
    # Initialize agent
    agent = UAEInvestorResearchAgent(
        target_industry=os.getenv('TARGET_INDUSTRY', 'creator economy, SaaS')
    )
    
    # Run research
    investors = agent.run()
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET')
    
    csv_content = generate_csv(investors)
    
    s3.put_object(
        Bucket=bucket,
        Key=f'investor-data/{datetime.now().strftime("%Y-%m-%d")}.csv',
        Body=csv_content,
        ContentType='text/csv'
    )
    
    # Optionally: Send to Google Sheets via API
    # update_google_sheet(investors)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Found {len(investors)} investors',
            'timestamp': datetime.now().isoformat()
        })
    }

def generate_csv(investors):
    """Convert investors list to CSV string"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=investors[0].keys())
    writer.writeheader()
    writer.writerows(investors)
    return output.getvalue()
```

### Step 2: Create Deployment Package
```bash
# Create layer for dependencies
mkdir python
pip install anthropic -t python/
zip -r layer.zip python

# Create function package
zip function.zip lambda_handler.py uae_investor_agent.py
```

### Step 3: Deploy with Terraform
Create `main.tf`:

```hcl
resource "aws_lambda_function" "investor_research" {
  filename      = "function.zip"
  function_name = "uae-investor-research"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 900 # 15 minutes
  
  environment {
    variables = {
      ANTHROPIC_API_KEY = var.anthropic_api_key
      S3_BUCKET         = aws_s3_bucket.results.id
    }
  }
  
  layers = [aws_lambda_layer_version.dependencies.arn]
}

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "investor-research-schedule"
  schedule_expression = "rate(6 hours)"
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "InvestorResearchLambda"
  arn       = aws_lambda_function.investor_research.arn
}
```

### Step 4: Deploy
```bash
terraform init
terraform apply
```

**Benefits:**
- ✅ Serverless (no servers to manage)
- ✅ Pay only when running (~$0.20/month)
- ✅ Scales automatically
- ✅ Integrates with AWS services

---

## 🔄 OPTION 3: Railway/Render (Always-On Web Service)

### Step 1: Add Web Server
Create `app.py`:

```python
from flask import Flask, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from uae_investor_agent import UAEInvestorResearchAgent
import os

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Store latest results
latest_results = []

def run_research():
    """Background job to research investors"""
    global latest_results
    agent = UAEInvestorResearchAgent()
    latest_results = agent.run()
    print(f"Research complete: {len(latest_results)} investors found")

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'last_run': latest_results[0]['date_added'] if latest_results else None,
        'investor_count': len(latest_results)
    })

@app.route('/download')
def download():
    """Download latest CSV"""
    return send_file('uae_investors_research.csv', as_attachment=True)

@app.route('/trigger')
def trigger():
    """Manually trigger research"""
    run_research()
    return jsonify({'status': 'triggered'})

if __name__ == '__main__':
    # Run research every 6 hours
    scheduler.add_job(run_research, 'interval', hours=6)
    scheduler.start()
    
    # Run once on startup
    run_research()
    
    # Start web server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Step 2: Add Requirements
Create `requirements.txt`:
```
anthropic
flask
apscheduler
```

### Step 3: Deploy to Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variable
railway variables set ANTHROPIC_API_KEY=your-key-here

# Deploy
railway up
```

**Benefits:**
- ✅ Simple deployment
- ✅ Always running
- ✅ Web dashboard to monitor
- ✅ Auto-deploy on git push

---

## 💻 OPTION 4: Local Cron Job (Free, No Cloud)

### For Mac/Linux

Create `run_research.sh`:
```bash
#!/bin/bash
cd /path/to/uae-investor-agent
source venv/bin/activate
export ANTHROPIC_API_KEY='your-key-here'
python uae_investor_agent.py
```

Add to crontab:
```bash
# Edit crontab
crontab -e

# Add this line (runs every 6 hours)
0 */6 * * * /path/to/run_research.sh >> /path/to/logs/cron.log 2>&1
```

### For Windows

Create `run_research.bat`:
```batch
@echo off
cd C:\path\to\uae-investor-agent
set ANTHROPIC_API_KEY=your-key-here
python uae_investor_agent.py
```

Use Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 6 hours
4. Action: Start a program → `run_research.bat`

**Benefits:**
- ✅ Completely free
- ✅ Full control
- ✅ No cloud dependencies

**Drawbacks:**
- ❌ Computer must stay on
- ❌ No redundancy

---

## 📊 Google Sheets Auto-Sync

### Method 1: Google Sheets API (Recommended)

Install additional dependency:
```bash
pip install gspread oauth2client
```

Add to your script:
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def update_google_sheet(investors):
    """Push data directly to Google Sheets"""
    
    # Setup credentials
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope)
    
    client = gspread.authorize(creds)
    
    # Open spreadsheet
    sheet = client.open('UAE Investors').sheet1
    
    # Clear existing data
    sheet.clear()
    
    # Write headers
    headers = list(investors[0].keys())
    sheet.append_row(headers)
    
    # Write data
    for investor in investors:
        sheet.append_row(list(investor.values()))
    
    print(f"✓ Updated Google Sheet with {len(investors)} investors")
```

Setup credentials:
1. Go to Google Cloud Console
2. Create service account
3. Download JSON key
4. Share your Google Sheet with the service account email

### Method 2: Zapier/Make Integration

Create webhook endpoint:
```python
@app.route('/webhook/new-investor', methods=['POST'])
def new_investor_webhook():
    """Zapier catches this and adds to Sheets"""
    data = request.json
    # Zapier will receive this and add to Sheets
    return jsonify({'status': 'received'})
```

Then in Zapier:
1. Trigger: Webhook (catches new investor data)
2. Action: Google Sheets → Add Row

---

## 🔔 Notifications & Monitoring

### Slack Notifications

```python
import requests

def send_slack_notification(investor_count):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    message = {
        "text": f"🎯 Found {investor_count} new UAE investors!",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Investor Research Complete*\n{investor_count} investors added to database"
                }
            }
        ]
    }
    
    requests.post(webhook_url, json=message)
```

### Email Alerts

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(investors):
    msg = MIMEText(f"Research complete: {len(investors)} investors found")
    msg['Subject'] = 'UAE Investor Research - Daily Update'
    msg['From'] = 'agent@yourcompany.com'
    msg['To'] = 'you@yourcompany.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email', 'app-password')
        server.send_message(msg)
```

---

## 📈 Recommended Setup for Your Use Case

**For Matchr Fundraising:**

1. **Use GitHub Actions** (Free tier is enough)
2. **Schedule:** Every 12 hours (2x daily)
3. **Auto-sync to Google Sheets**
4. **Slack notifications** when new investors found
5. **Manual trigger** for immediate research

This gives you:
- Fresh investor data twice daily
- Always up-to-date Google Sheet
- Team notifications via Slack
- Zero infrastructure costs
- Full automation

---

## 🎯 Quick Deploy Checklist

- [ ] Choose deployment platform
- [ ] Set up API keys as environment variables
- [ ] Configure schedule (recommended: every 6-12 hours)
- [ ] Set up Google Sheets integration
- [ ] Add notification system (Slack/Email)
- [ ] Test manual trigger
- [ ] Monitor first few runs
- [ ] Set up error alerting

---

**Need help with deployment? Let me know which option you'd like to use and I can provide more specific guidance!**

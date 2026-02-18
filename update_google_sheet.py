#!/usr/bin/env python3
"""
Google Sheets Sync Script
Automatically updates your Google Sheet with investor research data.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json
import os
from datetime import datetime

# Configuration
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'UAE Investors Database')
CSV_FILE = 'uae_investors_research.csv'
WORKSHEET_NAME = 'Investors'

def setup_google_sheets():
    """Authenticate and return Google Sheets client"""
    
    # Get credentials from environment variable
    creds_json = os.getenv('GSHEET_CREDENTIALS')
    
    if not creds_json:
        print("❌ GSHEET_CREDENTIALS environment variable not set")
        print("ℹ️  Create a service account and add the JSON as a GitHub secret")
        return None
    
    # Parse JSON credentials
    creds_dict = json.loads(creds_json)
    
    # Setup scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Authenticate
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    
    return client

def read_csv_data(filename):
    """Read investor data from CSV"""
    
    investors = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            investors.append(row)
    
    return investors

def update_sheet(client, investors):
    """Update Google Sheet with investor data"""
    
    try:
        # Open or create spreadsheet
        try:
            spreadsheet = client.open(SPREADSHEET_NAME)
            print(f"✓ Found spreadsheet: {SPREADSHEET_NAME}")
        except gspread.SpreadsheetNotFound:
            print(f"Creating new spreadsheet: {SPREADSHEET_NAME}")
            spreadsheet = client.create(SPREADSHEET_NAME)
            # Share with your email (optional)
            # spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
        
        # Get or create worksheet
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            print(f"✓ Found worksheet: {WORKSHEET_NAME}")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=20)
            print(f"✓ Created worksheet: {WORKSHEET_NAME}")
        
        # Clear existing data
        worksheet.clear()
        
        # Prepare data
        if not investors:
            print("⚠️  No investors to upload")
            return False
        
        headers = list(investors[0].keys())
        
        # Add metadata row
        metadata = [
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            f"Total Investors: {len(investors)}",
            "Status: Auto-updated by GitHub Actions"
        ]
        
        # Prepare all data
        all_data = [
            metadata,
            [],  # Empty row
            headers
        ]
        
        # Add investor rows
        for investor in investors:
            all_data.append(list(investor.values()))
        
        # Update sheet in batch (much faster)
        worksheet.update(all_data, value_input_option='USER_ENTERED')
        
        # Format header row
        worksheet.format('A3:L3', {
            'backgroundColor': {'red': 0.4, 'green': 0.5, 'blue': 0.9},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })
        
        # Format metadata row
        worksheet.format('A1:C1', {
            'textFormat': {'italic': True},
            'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
        })
        
        # Auto-resize columns
        worksheet.columns_auto_resize(0, len(headers))
        
        # Add data validation for status column (if exists)
        try:
            status_col_idx = headers.index('outreach_status') + 1
            worksheet.add_validation(
                f'{chr(64 + status_col_idx)}4:{chr(64 + status_col_idx)}1000',
                'ONE_OF_LIST',
                ['Not contacted', 'Request sent', 'Accepted', 'Meeting scheduled', 'Passed']
            )
        except ValueError:
            pass  # Status column doesn't exist
        
        # Freeze header rows
        worksheet.freeze(rows=3)
        
        print(f"✅ Successfully updated Google Sheet with {len(investors)} investors")
        print(f"📊 Spreadsheet URL: {spreadsheet.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Google Sheet: {e}")
        return False

def create_dashboard_sheet(client, spreadsheet_name):
    """Create a dashboard worksheet with stats and charts"""
    
    try:
        spreadsheet = client.open(spreadsheet_name)
        
        # Create or get dashboard worksheet
        try:
            dashboard = spreadsheet.worksheet('Dashboard')
        except gspread.WorksheetNotFound:
            dashboard = spreadsheet.add_worksheet(title='Dashboard', rows=30, cols=10)
        
        dashboard.clear()
        
        # Add dashboard content
        dashboard_data = [
            ['🎯 UAE Investor Research Dashboard', '', '', ''],
            [],
            ['Metric', 'Value', '', ''],
            ['Total Investors', f'=COUNTA(Investors!A4:A)', '', ''],
            ['With LinkedIn', f'=COUNTIF(Investors!E:E,"http*")', '', ''],
            ['With Email', f'=COUNTIF(Investors!F:F,"*@*")', '', ''],
            ['Contacted', f'=COUNTIF(Investors!J:J,"*sent")', '', ''],
            ['Meetings Scheduled', f'=COUNTIF(Investors!J:J,"*scheduled")', '', ''],
            [],
            ['Top Locations', '', '', ''],
            ['Location', 'Count', '', ''],
            # These will be populated by formulas
        ]
        
        dashboard.update(dashboard_data)
        
        # Format dashboard
        dashboard.format('A1:D1', {
            'backgroundColor': {'red': 0.4, 'green': 0.5, 'blue': 0.9},
            'textFormat': {'bold': True, 'fontSize': 14, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })
        
        print("✅ Dashboard created successfully")
        
    except Exception as e:
        print(f"⚠️  Could not create dashboard: {e}")

def main():
    """Main execution function"""
    
    print("="*60)
    print("📊 Google Sheets Sync Script")
    print("="*60)
    
    # Check if CSV exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found: {CSV_FILE}")
        exit(1)
    
    # Setup Google Sheets
    client = setup_google_sheets()
    
    if not client:
        print("❌ Failed to authenticate with Google Sheets")
        exit(1)
    
    # Read data
    print(f"\n📖 Reading data from {CSV_FILE}...")
    investors = read_csv_data(CSV_FILE)
    print(f"✓ Loaded {len(investors)} investors")
    
    # Update sheet
    print(f"\n🔄 Updating Google Sheet...")
    success = update_sheet(client, investors)
    
    if success:
        # Create dashboard
        print(f"\n📈 Creating dashboard...")
        create_dashboard_sheet(client, SPREADSHEET_NAME)
        
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE")
        print("="*60)
        exit(0)
    else:
        print("\n❌ SYNC FAILED")
        exit(1)

if __name__ == "__main__":
    main()

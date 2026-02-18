# UAE Investor Research Agent 🤖

Automated AI agent that researches potential investors in the UAE region, finds their LinkedIn profiles, generates personalized outreach messages, and exports everything to Google Sheets.

---

## 🎯 What It Does

1. **Searches** for UAE-based VCs, angel investors, and family offices
2. **Extracts** LinkedIn profiles, emails, investment focus, and portfolio companies
3. **Generates** personalized connection messages for each investor
4. **Exports** everything to CSV format (ready for Google Sheets)

---

## 🚀 Quick Start

### Option 1: Web Interface (Easiest)

1. Open `uae_investor_agent_web.html` in your browser
2. Fill in your company details and pitch
3. Click "Start Research"
4. Export results to CSV and upload to Google Sheets

**Note:** The web version includes demo data. For real research, use Option 2.

---

### Option 2: Python Script (Production)

#### Prerequisites
```bash
pip install anthropic
```

#### Setup
1. Get your Anthropic API key from https://console.anthropic.com/
2. Set it as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-key-here'
   ```

#### Run
```bash
python uae_investor_agent.py
```

The script will:
- Search for investors across multiple queries
- Extract structured data using Claude's web search
- Generate personalized messages
- Save to `uae_investors_research.csv`

---

## 📊 Output Format

The CSV includes these columns:

| Column | Description |
|--------|-------------|
| `full_name` | Investor's full name |
| `title` | Their role (e.g., "Managing Partner") |
| `company` | Fund or company name |
| `location` | City in UAE (Dubai, Abu Dhabi, etc.) |
| `linkedin_url` | LinkedIn profile URL |
| `email` | Email address (if publicly available) |
| `investment_focus` | Sectors and stages they invest in |
| `portfolio_companies` | Notable investments |
| `personalized_message` | AI-generated outreach message |
| `outreach_status` | Track your progress |
| `date_added` | When the record was created |
| `source_url` | Where the info came from |

---

## 🔧 Customization

### Change Target Industry
Edit line 16 in `uae_investor_agent.py`:
```python
agent = UAEInvestorResearchAgent(
    target_industry="your industry here"
)
```

### Modify Search Queries
Edit the `search_queries` list in the `search_investors()` method (line 26):
```python
search_queries = [
    "your custom query 1",
    "your custom query 2",
    "your custom query 3"
]
```

### Customize Message Generation
Edit the prompt in `generate_personalized_message()` method (line 133) to change:
- Your company name
- Your pitch
- Message tone and length

---

## 📥 Importing to Google Sheets

### Method 1: Direct Import
1. Run the Python script → generates CSV
2. Open Google Sheets
3. File → Import → Upload → Select CSV
4. Choose "Replace spreadsheet" or "Insert new sheet"

### Method 2: Auto-Sync (Advanced)
Use Google Sheets IMPORTDATA function:
```
=IMPORTDATA("your-csv-url")
```
Host the CSV on a public URL and it will auto-update.

---

## 💡 Best Practices

### LinkedIn Outreach
- **Personalize further**: Use the AI-generated message as a starting point
- **Mention specifics**: Reference their portfolio companies
- **Keep it brief**: LinkedIn has a 300-character limit for connection requests
- **Follow up**: If they accept, send a longer message

### Email Outreach
- **Verify emails**: Use tools like Hunter.io to verify before sending
- **Subject lines matter**: Keep them clear and relevant
- **Add value first**: Share insights or ask intelligent questions
- **Include deck**: Attach or link to your pitch deck

### Tracking Progress
Use the Google Sheet to track:
- Connection request status (Pending, Accepted, Declined)
- Response status (No reply, Interested, Not interested)
- Meeting scheduled (Yes/No)
- Follow-up dates

---

## 🔍 How It Works

### Architecture

```
┌─────────────────┐
│  User Input     │
│  (Industry,     │
│   Company)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web Search     │◄──── Claude API with
│  (3-5 queries)  │      Web Search Tool
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data           │◄──── Claude API
│  Extraction     │      (JSON parsing)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Message        │◄──── Claude API
│  Generation     │      (personalization)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CSV Export     │
│  (Google Sheets)│
└─────────────────┘
```

### Search Strategy
The agent uses multiple search patterns:
1. **VC firms** → "UAE venture capital firms [industry]"
2. **Geography-specific** → "Dubai investors [focus]"
3. **Stage-specific** → "MENA early-stage [sector]"
4. **Alternative capital** → "UAE family offices startups"

### Personalization Engine
For each investor, the agent:
1. Analyzes their investment focus
2. Identifies relevant portfolio companies
3. Crafts a message that:
   - References their expertise
   - Connects your startup to their thesis
   - Stays under 300 characters
   - Sounds human, not robotic

---

## ⚠️ Limitations

1. **Email availability**: Most investor emails are not publicly listed
2. **Rate limits**: The script includes delays to respect API limits
3. **Data accuracy**: Information is sourced from public web data
4. **LinkedIn profiles**: Some investors may not have public profiles

---

## 🛠️ Troubleshooting

### "No investors found"
- **Solution**: Broaden your search terms
- Try removing specific constraints
- Increase the number of search queries

### API Rate Limit Errors
- **Solution**: Increase sleep times in the script
- Reduce the number of concurrent searches
- Use a higher-tier API plan

### JSON Parsing Errors
- **Solution**: The script includes error handling
- Check the raw response in console output
- Adjust the extraction prompt if needed

### Empty Email/LinkedIn Fields
- **Solution**: This is normal for many investors
- Use LinkedIn Sales Navigator for more data
- Cross-reference with Crunchbase or PitchBook

---

## 📈 Future Enhancements

Potential additions:
- [ ] Direct Google Sheets API integration (no CSV export needed)
- [ ] Email verification integration (Hunter.io, NeverBounce)
- [ ] LinkedIn Sales Navigator scraping
- [ ] Multi-region support (not just UAE)
- [ ] Automated follow-up sequences
- [ ] Sentiment analysis on investor news
- [ ] Portfolio company analysis
- [ ] Investment thesis matching score

---

## 🤝 Support

For issues or questions:
1. Check this documentation first
2. Review the code comments
3. Test with the web demo before production
4. Ensure your API key is valid

---

## 📝 License

MIT License - feel free to modify and use for your fundraising efforts!

---

## 🎯 Example Use Case

**Scenario**: You're raising a seed round for your creator economy platform.

**Steps**:
1. Run the agent targeting "creator economy, SaaS, marketplace"
2. Export 20-30 relevant UAE investors
3. Send personalized LinkedIn requests (5-10 per day)
4. When they accept, send a detailed message + deck
5. Track responses in Google Sheets
6. Schedule calls with interested investors

**Expected Results**:
- 60-70% connection acceptance rate
- 20-30% response rate from accepted connections
- 5-10% meeting conversion rate

That's **2-3 investor meetings** from 30 outreach attempts.

---

**Good luck with your fundraise! 🚀**

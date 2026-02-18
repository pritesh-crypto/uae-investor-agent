# 🚀 QUICK START - 24/7 Deployment

## Option 1: Automated Setup (Easiest)

```bash
./deploy.sh
```

Follow the prompts. Done in 5 minutes!

---

## Option 2: Manual GitHub Setup

### Step 1: Create Repository
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create uae-investor-agent --public --source=. --push
```

### Step 2: Add Secrets
Go to: `Settings → Secrets and variables → Actions`

**Required:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Optional:**
- `GSHEET_CREDENTIALS` - Google service account JSON
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications

### Step 3: Trigger First Run
Go to: `Actions → UAE Investor Research Agent → Run workflow`

---

## What Happens Automatically

✅ **Every 6 hours:**
1. Agent searches for new UAE investors
2. Extracts LinkedIn, emails, investment focus
3. Generates personalized messages
4. Updates CSV in repository
5. Syncs to Google Sheets (if enabled)
6. Sends Slack notification (if enabled)

---

## Monitoring

### Check Status
```bash
gh run list --workflow=investor-research.yml
```

### View Logs
```bash
gh run view --log
```

### Manual Trigger
```bash
gh workflow run investor-research.yml
```

Or click "Run workflow" in GitHub Actions tab

---

## File Locations

**After each run:**
- `uae_investors_research.csv` - Latest results (auto-updated)
- `historical_data/investors_YYYYMMDD_HHMMSS.csv` - Archived runs
- GitHub Actions → Artifacts - Downloadable CSV

---

## Cost Estimates

### GitHub Actions (Free Tier)
- ✅ 2,000 minutes/month FREE
- Each run: ~5 minutes
- Runs per month: 120 (every 6 hours)
- Total: 600 minutes/month
- **Cost: FREE** ✨

### Anthropic API
- ~50 API calls per run
- Cost: ~$0.05 per run
- 120 runs/month: ~$6/month

### Google Sheets API
- ✅ FREE (unlimited)

### Total: ~$6/month

---

## Customization

### Change Frequency
Edit `.github/workflows/investor-research.yml`:
```yaml
schedule:
  - cron: '0 */12 * * *'  # Every 12 hours
  - cron: '0 9 * * *'     # Daily at 9 AM UTC
  - cron: '0 0 * * 1'     # Weekly on Monday
```

### Change Target Industry
Edit `uae_investor_agent.py` line 16:
```python
agent = UAEInvestorResearchAgent(
    target_industry="fintech, blockchain, AI"
)
```

### Change Search Queries
Edit `uae_investor_agent.py` line 26:
```python
search_queries = [
    "UAE angel investors fintech",
    "Dubai seed stage VC firms",
    # Add your queries
]
```

---

## Troubleshooting

### "No investors found"
- Check API key is set correctly
- Broaden search terms
- Check GitHub Actions logs

### "Google Sheets sync failed"
- Verify GSHEET_CREDENTIALS secret
- Check service account has edit access
- Ensure Sheets API is enabled

### "Workflow not running"
- Check cron schedule is valid
- Ensure workflow file is in `.github/workflows/`
- Verify repository has Actions enabled

---

## Advanced: Multiple Regions

Want to research investors in multiple regions?

**Option A: Multiple Workflows**
- Duplicate `investor-research.yml`
- Create `uae_investor_agent.py`, `saudi_investor_agent.py`, etc.
- Each runs on own schedule

**Option B: Single Workflow with Matrix**
```yaml
strategy:
  matrix:
    region: [uae, saudi, egypt, turkey]
```

---

## Security Best Practices

✅ **DO:**
- Use GitHub Secrets for all credentials
- Enable Dependabot for security updates
- Set repository to private if containing sensitive data
- Review workflow runs regularly

❌ **DON'T:**
- Commit API keys to repository
- Share service account credentials
- Make sensitive investor data public

---

## Support

**Issues?** Check:
1. GitHub Actions logs
2. DEPLOYMENT_GUIDE.md for detailed troubleshooting
3. README.md for full documentation

**Questions?** Open an issue on GitHub

---

## Success Checklist

- [ ] Repository created on GitHub
- [ ] Secrets added (ANTHROPIC_API_KEY minimum)
- [ ] First workflow run completed successfully
- [ ] CSV file visible in repository
- [ ] Google Sheets syncing (if enabled)
- [ ] Slack notifications working (if enabled)
- [ ] Schedule confirmed (check next run time)

---

**You're all set! Your agent is running 24/7. 🎉**

Check back in 6 hours for your first batch of investors!

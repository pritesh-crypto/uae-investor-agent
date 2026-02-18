import anthropic
import json
import csv
import time
from datetime import datetime
import os

# Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')  # User should set this
OUTPUT_CSV = 'uae_investors_research.csv'

class UAEInvestorResearchAgent:
    """
    AI Agent to research potential investors in the UAE region.
    Outputs: LinkedIn profiles, personalized messages, and emails to CSV/Google Sheets.
    """
    
    def __init__(self, target_industry="creator economy, social commerce, SaaS"):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.target_industry = target_industry
        self.investors_data = []
        
    def search_investors(self, focus_area="venture capital"):
        """
        Use Claude with web search to find UAE investors.
        """
        print(f"\n🔍 Searching for UAE investors in {focus_area}...")
        
        # Single combined search to avoid rate limits
        search_query = f"UAE Dubai Abu Dhabi venture capital investors angel investors family offices {self.target_industry}"
        
        print(f"  → Searching: {search_query}")
        
        investors = []
        
        try:
            # Call Claude API with web search - ONE REQUEST ONLY
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search"
                    }
                ],
                messages=[{
                    "role": "user",
                    "content": f"""Search for UAE investors, VCs, and angel investors in: {self.target_industry}

Find at least 10-15 specific investors in the UAE (Dubai, Abu Dhabi, Sharjah).

For each investor, extract:
1. Full name (person or firm)
2. Title/role
3. Company/Fund name
4. LinkedIn profile URL (search for it)
5. Email (if publicly available)
6. Investment focus/sectors
7. Notable portfolio companies
8. Location in UAE

Provide detailed results with real names and companies. Format as structured data."""
                }]
            )
            
            # Parse response
            result_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    result_text += block.text
            
            investors.append({
                'query': search_query,
                'results': result_text
            })
            
            print("  ✓ Search completed")
            
        except Exception as e:
            print(f"  ✗ Search failed: {e}")
        
        return investors
    
    def extract_structured_data(self, raw_results):
        """
        Use Claude to parse unstructured search results into structured investor data.
        """
        print("\n📊 Extracting structured data from search results...")
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            messages=[{
                "role": "user",
                "content": f"""Here are the search results about UAE investors:

{json.dumps(raw_results, indent=2)}

Please analyze these results and extract a structured list of individual investors and firms.

For each investor, provide:
- full_name: Person or firm name
- title: Their role/title
- company: Company/Fund name
- linkedin_url: LinkedIn profile URL (if found, otherwise "Not found")
- email: Email address (if found, otherwise "Not found")
- location: City in UAE
- investment_focus: What sectors/stages they focus on
- portfolio_companies: Notable companies they've invested in (if mentioned)
- source_url: Where this info came from

Return ONLY a valid JSON array of objects. No other text.
Example format:
[
  {{
    "full_name": "John Smith",
    "title": "Managing Partner",
    "company": "ABC Ventures",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "email": "john@abcventures.com",
    "location": "Dubai",
    "investment_focus": "Early-stage SaaS, fintech",
    "portfolio_companies": "Company A, Company B",
    "source_url": "https://example.com"
  }}
]"""
            }]
        )
        
        # Extract JSON
        result_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                result_text += block.text
        
        # Clean and parse JSON
        try:
            # Remove markdown code blocks if present
            clean_json = result_text.strip()
            if clean_json.startswith('```'):
                clean_json = clean_json.split('```')[1]
                if clean_json.startswith('json'):
                    clean_json = clean_json[4:]
            clean_json = clean_json.strip()
            
            investors = json.loads(clean_json)
            print(f"  ✓ Extracted {len(investors)} investors")
            return investors
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parsing error: {e}")
            print(f"  Raw response: {result_text[:500]}")
            return []
    
    def generate_personalized_message(self, investor):
        """
        Generate a personalized outreach message for each investor.
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Write a highly personalized LinkedIn connection request message for this investor:

Name: {investor['full_name']}
Company: {investor['company']}
Title: {investor['title']}
Investment Focus: {investor['investment_focus']}
Portfolio: {investor.get('portfolio_companies', 'N/A')}

Context: I'm building Matchr - a swipe-first creator-brand matching platform that's reimagining creator commerce. We're making it effortless for brands (especially SMBs) to discover and partner with creators at the perfect timing, powered by real audience intelligence.

The message should be:
- Under 300 characters (LinkedIn limit)
- Reference their investment focus or portfolio naturally
- Not salesy, just genuine connection
- Professional but warm

Return ONLY the message text, nothing else."""
            }]
        )
        
        message = ""
        for block in response.content:
            if hasattr(block, 'text'):
                message += block.text
        
        return message.strip()
    
    def enrich_investor_data(self, investors):
        """
        Add personalized messages to each investor record.
        """
        print("\n✍️  Generating personalized messages...")
        
        enriched = []
        for i, investor in enumerate(investors, 1):
            print(f"  → {i}/{len(investors)}: {investor['full_name']}")
            
            try:
                personalized_msg = self.generate_personalized_message(investor)
                investor['personalized_message'] = personalized_msg
            except Exception as e:
                print(f"    ⚠️  Could not generate message: {e}")
                # Create a basic template message
                investor['personalized_message'] = f"Hi {investor['full_name'].split()[0]}, interested in discussing opportunities in {self.target_industry}. Would love to connect."
            
            investor['outreach_status'] = 'Not contacted'
            investor['date_added'] = datetime.now().strftime('%Y-%m-%d')
            
            enriched.append(investor)
            
            # Longer delay to avoid rate limits
            if i < len(investors):
                time.sleep(3)  # 3 seconds between requests
        
        return enriched
    
    def save_to_csv(self, investors):
        """
        Save investor data to CSV file (Google Sheets compatible).
        """
        print(f"\n💾 Saving to {OUTPUT_CSV}...")
        
        fieldnames = [
            'full_name', 'title', 'company', 'location',
            'linkedin_url', 'email', 'investment_focus',
            'portfolio_companies', 'personalized_message',
            'outreach_status', 'date_added', 'source_url'
        ]
        
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(investors)
        
        print(f"  ✓ Saved {len(investors)} investors to {OUTPUT_CSV}")
        print(f"\n📋 You can now upload this CSV to Google Sheets!")
        
    def run(self):
        """
        Execute the full research pipeline.
        """
        print("="*60)
        print("🤖 UAE INVESTOR RESEARCH AGENT")
        print("="*60)
        print(f"Target Industry: {self.target_industry}")
        print(f"Output File: {OUTPUT_CSV}")
        print("="*60)
        
        # Step 1: Search for investors
        raw_results = self.search_investors()
        
        # Step 2: Extract structured data
        investors = self.extract_structured_data(raw_results)
        
        if not investors:
            print("\n❌ No investors found. Try adjusting search parameters.")
            return
        
        # Step 3: Generate personalized messages
        enriched_investors = self.enrich_investor_data(investors)
        
        # Step 4: Save to CSV
        self.save_to_csv(enriched_investors)
        
        # Summary
        print("\n" + "="*60)
        print("✅ RESEARCH COMPLETE")
        print("="*60)
        print(f"Total Investors Found: {len(enriched_investors)}")
        print(f"With LinkedIn: {sum(1 for inv in enriched_investors if inv['linkedin_url'] != 'Not found')}")
        print(f"With Email: {sum(1 for inv in enriched_investors if inv['email'] != 'Not found')}")
        print("="*60)
        
        return enriched_investors


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = UAEInvestorResearchAgent(
        target_industry="creator economy, social commerce, marketplace platforms"
    )
    
    # Run research
    investors = agent.run()
    
    # Display sample results
    if investors:
        print("\n📊 SAMPLE RESULTS (First 3):")
        print("="*60)
        for inv in investors[:3]:
            print(f"\n👤 {inv['full_name']} - {inv['title']}")
            print(f"   Company: {inv['company']}")
            print(f"   Location: {inv['location']}")
            print(f"   LinkedIn: {inv['linkedin_url']}")
            print(f"   Email: {inv['email']}")
            print(f"   Focus: {inv['investment_focus']}")
            print(f"   Message Preview: {inv['personalized_message'][:150]}...")

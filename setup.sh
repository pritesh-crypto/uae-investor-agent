#!/bin/bash

# UAE Investor Research Agent - Quick Setup Script
# Run this to get started in seconds

echo "=========================================="
echo "🤖 UAE Investor Research Agent Setup"
echo "=========================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install anthropic --quiet
echo "✓ Dependencies installed"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not found in environment variables"
    echo ""
    echo "To get your API key:"
    echo "1. Go to https://console.anthropic.com/"
    echo "2. Sign up or log in"
    echo "3. Navigate to API Keys"
    echo "4. Create a new key"
    echo ""
    read -p "Enter your Anthropic API key: " api_key
    export ANTHROPIC_API_KEY=$api_key
    
    # Save to shell profile
    echo "" >> ~/.bashrc
    echo "# Anthropic API Key" >> ~/.bashrc
    echo "export ANTHROPIC_API_KEY='$api_key'" >> ~/.bashrc
    
    echo "✓ API key saved to ~/.bashrc"
else
    echo "✓ ANTHROPIC_API_KEY found"
fi
echo ""

# Configuration
echo "🎯 Configuration"
echo "----------------------------------------"
read -p "Company name (default: Matchr): " company_name
company_name=${company_name:-Matchr}

read -p "Industry (default: creator economy, SaaS): " industry
industry=${industry:-"creator economy, SaaS"}

read -p "Number of investors to find (default: 10): " count
count=${count:-10}
echo ""

# Create custom config file
cat > config.json <<EOF
{
  "company_name": "$company_name",
  "industry": "$industry",
  "target_count": $count,
  "pitch": "Edit this with your one-liner pitch"
}
EOF

echo "✓ Configuration saved to config.json"
echo ""

# Run options
echo "=========================================="
echo "🚀 Ready to Start!"
echo "=========================================="
echo ""
echo "Choose how to run:"
echo ""
echo "Option 1: Web Interface (Demo Mode)"
echo "  → Open uae_investor_agent_web.html in your browser"
echo ""
echo "Option 2: Python Script (Production Mode)"
echo "  → Run: python3 uae_investor_agent.py"
echo ""
echo "Option 3: Run now with current settings"
echo ""
read -p "Run production script now? (y/n): " run_now

if [ "$run_now" = "y" ] || [ "$run_now" = "Y" ]; then
    echo ""
    echo "🔍 Starting investor research..."
    echo ""
    python3 uae_investor_agent.py
    
    if [ -f "uae_investors_research.csv" ]; then
        echo ""
        echo "=========================================="
        echo "✅ SUCCESS!"
        echo "=========================================="
        echo ""
        echo "Results saved to: uae_investors_research.csv"
        echo ""
        echo "Next steps:"
        echo "1. Open the CSV file"
        echo "2. Upload to Google Sheets"
        echo "3. Start reaching out to investors!"
        echo ""
        echo "📋 Quick Stats:"
        lines=$(wc -l < uae_investors_research.csv)
        echo "   Total investors found: $((lines - 1))"
        echo ""
    fi
else
    echo ""
    echo "📚 Read README.md for full instructions"
    echo ""
fi

echo "=========================================="
echo "Need help? Check out README.md"
echo "=========================================="

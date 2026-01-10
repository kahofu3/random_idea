#!/bin/bash

# Script to check Gemini API quota and usage information

echo "========================================="
echo "Gemini API Quota Checker"
echo "========================================="
echo ""

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY is not set"
    echo "Please run: source ~/.zshrc"
    exit 1
fi

echo "✅ API Key is set (showing first 20 chars): ${GEMINI_API_KEY:0:20}..."
echo ""

echo "📋 Available Models:"
curl -s "https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY" | \
    python3 -c "import sys, json; data = json.load(sys.stdin); \
    models = data.get('models', []); \
    [print(f\"  • {m['displayName']} ({m['name']})\") for m in models if 'gemini' in m['name'].lower()]" 2>/dev/null

echo ""
echo "========================================="
echo "To Increase Quota:"
echo "========================================="
echo ""
echo "1. Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas"
echo ""
echo "2. Enable Billing (if not already enabled):"
echo "   https://console.cloud.google.com/billing"
echo ""
echo "3. Request quota increase:"
echo "   - Select the quota you want to increase"
echo "   - Click 'Edit Quotas'"
echo "   - Fill in the form and submit"
echo ""
echo "4. Check usage and billing:"
echo "   https://aistudio.google.com/app/apikey"
echo ""


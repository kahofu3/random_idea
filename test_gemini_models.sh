#!/bin/bash

# Script to test different Gemini models to find one that isn't quota-exhausted

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY is not set"
    exit 1
fi

API_KEY="$GEMINI_API_KEY"

echo "Testing different Gemini models for available quota..."
echo ""

# List of models to try (from lightest to heaviest, as lighter models often have higher quotas)
models=(
    "gemini-2.0-flash-lite"
    "gemini-2.5-flash-lite"
    "gemini-2.0-flash"
    "gemini-2.5-flash"
    "gemini-2.5-pro"
)

for model in "${models[@]}"; do
    echo -n "Testing ${model}... "
    
    response=$(curl -s -X POST \
        "https://generativelanguage.googleapis.com/v1/models/${model}:generateContent?key=${API_KEY}" \
        -H "Content-Type: application/json" \
        -d '{
            "contents": [{
                "parts": [{"text": "Say hello in one word"}]
            }]
        }' 2>&1)
    
    if echo "$response" | grep -q "totalTokens\|text"; then
        echo "✅ WORKS - This model has quota available!"
        echo "   Use it with: gemini -m ${model} 'your question'"
        echo ""
        exit 0
    elif echo "$response" | grep -q "quota\|QUOTA\|exhausted\|PERMISSION_DENIED"; then
        echo "❌ Quota exhausted"
    elif echo "$response" | grep -q "400\|403"; then
        echo "⚠️  Not available"
    else
        echo "❓ Unknown response"
    fi
done

echo ""
echo "All models appear to be quota-exhausted. Try again after quota reset (midnight Pacific Time)."


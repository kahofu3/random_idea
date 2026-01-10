#!/bin/bash

# Script to set up Gemini API key for the Gemini CLI

echo "========================================="
echo "Gemini CLI API Key Setup"
echo "========================================="
echo ""
echo "1. Copy your API key from the browser window that just opened"
echo "   (or visit: https://aistudio.google.com/app/apikey)"
echo ""
read -p "2. Paste your API key here: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "Error: API key cannot be empty!"
    exit 1
fi

echo ""
echo "Setting up API key..."

# Set as environment variable in shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
fi

if [ -n "$SHELL_PROFILE" ]; then
    # Remove old API key if exists
    sed -i '' '/GEMINI_API_KEY/d' "$SHELL_PROFILE" 2>/dev/null || sed -i '/GEMINI_API_KEY/d' "$SHELL_PROFILE" 2>/dev/null
    
    # Add new API key
    echo "" >> "$SHELL_PROFILE"
    echo "# Gemini API Key" >> "$SHELL_PROFILE"
    echo "export GEMINI_API_KEY=\"$API_KEY\"" >> "$SHELL_PROFILE"
    
    echo "✓ API key added to $SHELL_PROFILE"
    echo ""
    echo "To use it in this terminal session, run:"
    echo "  export GEMINI_API_KEY=\"$API_KEY\""
    echo ""
    echo "Or restart your terminal to load it automatically."
else
    echo "Could not find shell profile file. Setting for current session only:"
    echo "  export GEMINI_API_KEY=\"$API_KEY\""
fi

# Also try to set it for the Gemini CLI if it supports config
if command -v gemini &> /dev/null; then
    echo ""
    echo "✓ Gemini CLI is installed"
    echo "You can now use it with: gemini [your query]"
fi

echo ""
echo "Setup complete! 🎉"


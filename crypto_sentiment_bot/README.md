# 🤖 Crypto News Sentiment Analyzer Bot

A Telegram bot that analyzes cryptocurrency news sentiment in real-time to help you understand market mood and potential price movements.

## 🌟 Features

- **Real-time News Monitoring**: Tracks major crypto news sources (CoinDesk, CoinTelegraph, etc.)
- **Sentiment Analysis**: Uses VADER and TextBlob with crypto-specific vocabulary
- **Impact Assessment**: Identifies high-impact news that could move markets
- **Telegram Alerts**: Get notified of important news via Telegram
- **Market Summary**: Overall market sentiment analysis
- **Source Credibility**: Weights news by source reliability

## 📊 What It Tracks

### News Sources
- **CoinDesk** (Weight: 0.9) - Leading crypto news
- **CoinTelegraph** (Weight: 0.8) - Major crypto publication  
- **Decrypt** (Weight: 0.7) - Crypto & Web3 news
- **Bitcoinist** (Weight: 0.6) - Bitcoin-focused news
- **Bloomberg Crypto** (Weight: 1.0) - Highest credibility
- **Reuters** (Weight: 0.95) - Traditional finance coverage

### Key Events Monitored
- **Regulatory News**: SEC actions, government policies
- **Institutional Adoption**: Tesla, MicroStrategy, ETFs
- **Technical Events**: Hacks, upgrades, network issues
- **Market Movements**: Whale activity, liquidations

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### 2. Installation

```bash
# Clone the repository
cd crypto_sentiment_bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Create a Telegram bot:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy your bot token

2. Set up environment:
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your bot token
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
# Run the main bot
python main.py

# Or test the analyzer first
python test_analyzer.py
```

## 📱 Bot Commands

- `/start` - Initialize bot and see welcome message
- `/news` - Get latest analyzed news (last 6 hours)
- `/summary` - Get 24-hour market sentiment summary
- `/alerts on/off` - Toggle automatic high-impact alerts
- `/status` - Check bot status and sources
- `/help` - Detailed help and explanations

## 🧪 Testing the Analyzer

Run the test script to see how sentiment analysis works:

```bash
python test_analyzer.py
```

This shows real examples like:
- "BlackRock Files for Bitcoin ETF" → Very Positive 🚀
- "FTX Exchange Files for Bankruptcy" → Very Negative 💥
- "Bitcoin Whale Moves 50,000 BTC" → Negative 📉

## 📈 Understanding the Analysis

### Sentiment Levels
- 🚀 **Very Positive** (>0.5): Strong bullish signals
- 📈 **Positive** (0.1-0.5): Moderate good news
- ➡️ **Neutral** (-0.1-0.1): Mixed signals
- 📉 **Negative** (-0.5--0.1): Moderate bad news
- 💥 **Very Negative** (<-0.5): Strong bearish signals

### Impact Levels
- **HIGH**: Major market-moving news (SEC, bans, major adoption)
- **MEDIUM-HIGH**: Significant but not critical
- **MEDIUM**: Notable news with limited impact
- **LOW**: Minor news, unlikely to affect prices

### Crypto-Specific Terms
The analyzer understands crypto slang:
- Positive: moon, bullish, pump, hodl, adoption
- Negative: dump, crash, scam, hack, rekt, FUD

## 🔧 Advanced Configuration

### Custom News Sources
Edit `src/news_sources.py` to add sources:

```python
"new_source": {
    "name": "Source Name",
    "rss": "https://example.com/rss",
    "weight": 0.7  # 0-1 credibility score
}
```

### Adjust Sentiment Weights
Modify crypto terms in `src/sentiment_analyzer.py`:

```python
self.crypto_lexicon = {
    'moon': 3.0,  # Very positive
    'dump': -3.0  # Very negative
}
```

## ⚠️ Important Disclaimers

1. **Not Financial Advice**: This tool provides information only
2. **No Guarantees**: Sentiment doesn't always predict price movement
3. **Verify News**: Always check multiple sources
4. **Market Risk**: Crypto markets are highly volatile

## 🛠️ Troubleshooting

### Bot not responding?
- Check your bot token is correct
- Ensure you've started the bot with `/start`
- Check logs for errors

### No news showing?
- RSS feeds might be temporarily down
- Try again in a few minutes
- Check internet connection

### Incorrect sentiment?
- Sentiment analysis isn't perfect
- Complex headlines may confuse the analyzer
- Source context matters

## 📊 Example Output

```
📰 Headline: SEC Approves Bitcoin Spot ETF Applications
📡 Source: CoinDesk
🎯 Sentiment: Very Positive 🚀
⚡ Impact: HIGH
📊 Score: 0.825
🔑 Keywords: +approves, +adoption
```

## 🔮 Future Enhancements

- [ ] Price correlation tracking
- [ ] Multi-language support
- [ ] Historical sentiment database
- [ ] Machine learning improvements
- [ ] More news sources
- [ ] Custom alert thresholds

## 📝 License

MIT License - Use at your own risk

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Remember**: This is an educational tool. Always do your own research before making investment decisions!
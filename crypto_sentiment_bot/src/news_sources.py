"""
Crypto News Sources Configuration
Real sources that we'll monitor for sentiment analysis
"""

NEWS_SOURCES = {
    # Major Crypto News Sites
    "coindesk": {
        "name": "CoinDesk",
        "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "api": None,
        "weight": 0.9  # High credibility
    },
    "cointelegraph": {
        "name": "CoinTelegraph", 
        "rss": "https://cointelegraph.com/rss",
        "api": None,
        "weight": 0.8
    },
    "decrypt": {
        "name": "Decrypt",
        "rss": "https://decrypt.co/feed",
        "api": None,
        "weight": 0.7
    },
    "bitcoinist": {
        "name": "Bitcoinist",
        "rss": "https://bitcoinist.com/feed/",
        "api": None,
        "weight": 0.6
    },
    
    # General Finance with Crypto Coverage
    "bloomberg_crypto": {
        "name": "Bloomberg Crypto",
        "rss": None,
        "api": "https://www.bloomberg.com/crypto",  # Would need scraping
        "weight": 1.0  # Highest credibility
    },
    "reuters": {
        "name": "Reuters Crypto",
        "search_terms": ["bitcoin", "cryptocurrency", "ethereum", "crypto"],
        "weight": 0.95
    }
}

# Keywords that indicate major market-moving news
MAJOR_KEYWORDS = {
    "positive": [
        "adoption", "accepts", "approves", "bullish", "surge", "rally",
        "partnership", "integration", "institutional", "mainstream",
        "breakthrough", "upgrade", "halving", "ATH", "all-time high"
    ],
    "negative": [
        "ban", "crash", "hack", "scam", "fraud", "investigation",
        "lawsuit", "bankruptcy", "default", "crackdown", "regulatory",
        "bear", "plunge", "dump", "exploit", "vulnerability"
    ]
}

# Specific events we track
TRACKED_EVENTS = {
    "regulatory": {
        "keywords": ["SEC", "regulation", "legal", "government", "policy"],
        "impact": "high"
    },
    "institutional": {
        "keywords": ["Tesla", "MicroStrategy", "bank", "fund", "ETF"],
        "impact": "high"
    },
    "technical": {
        "keywords": ["hack", "security", "breach", "vulnerability"],
        "impact": "medium"
    },
    "market": {
        "keywords": ["whale", "liquidation", "volume", "breakout"],
        "impact": "medium"
    }
}

# Example of what news we'll analyze
EXAMPLE_NEWS = [
    {
        "headline": "Tesla Announces $1.5 Billion Bitcoin Purchase",
        "source": "CoinDesk",
        "expected_sentiment": "Very Positive",
        "expected_impact": "High - Institutional adoption"
    },
    {
        "headline": "China Bans Cryptocurrency Mining Operations",
        "source": "Reuters",
        "expected_sentiment": "Very Negative", 
        "expected_impact": "High - Major market disruption"
    },
    {
        "headline": "Ethereum Successfully Completes Merge Upgrade",
        "source": "CoinTelegraph",
        "expected_sentiment": "Positive",
        "expected_impact": "Medium - Technical improvement"
    },
    {
        "headline": "Unknown Whale Moves 10,000 BTC to Exchange",
        "source": "Bitcoinist",
        "expected_sentiment": "Negative",
        "expected_impact": "Low-Medium - Potential sell pressure"
    }
]
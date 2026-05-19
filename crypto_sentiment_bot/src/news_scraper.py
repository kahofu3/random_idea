"""
News Scraper for Crypto News Sources
Fetches real-time news from RSS feeds and APIs
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from typing import List, Dict
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.news_cache = []
        self.last_fetch = {}
        
    def fetch_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Fetch news from RSS feed"""
        try:
            logger.info(f"Fetching RSS feed from {source_name}")
            feed = feedparser.parse(feed_url)
            
            articles = []
            for entry in feed.entries[:10]:  # Get latest 10 articles
                article = {
                    'headline': entry.title,
                    'url': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],  # First 200 chars
                    'source': source_name,
                    'fetched_at': datetime.now().isoformat()
                }
                articles.append(article)
                
            logger.info(f"Fetched {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching {source_name}: {str(e)}")
            return []
    
    def fetch_all_news(self, sources: Dict) -> List[Dict]:
        """Fetch news from all configured sources"""
        all_articles = []
        
        for source_id, source_info in sources.items():
            if source_info.get('rss'):
                # Rate limiting
                time.sleep(1)
                
                articles = self.fetch_rss_feed(
                    source_info['rss'], 
                    source_info['name']
                )
                
                # Add source weight to each article
                for article in articles:
                    article['source_weight'] = source_info['weight']
                    article['source_id'] = source_id
                
                all_articles.extend(articles)
        
        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x['published'], reverse=True)
        
        return all_articles
    
    def filter_recent_news(self, articles: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter articles from the last N hours"""
        recent_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for article in articles:
            try:
                # Parse published date
                pub_date = feedparser._parse_date(article['published'])
                if pub_date:
                    article_time = datetime(*pub_date[:6])
                    if article_time > cutoff_time:
                        recent_articles.append(article)
            except:
                # If can't parse date, include it anyway
                recent_articles.append(article)
        
        return recent_articles
    
    def search_for_keywords(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles containing specific keywords"""
        filtered = []
        
        for article in articles:
            headline_lower = article['headline'].lower()
            summary_lower = article.get('summary', '').lower()
            
            for keyword in keywords:
                if keyword.lower() in headline_lower or keyword.lower() in summary_lower:
                    filtered.append(article)
                    break
        
        return filtered
    
    def get_trending_topics(self, articles: List[Dict]) -> Dict[str, int]:
        """Extract trending topics from articles"""
        topic_count = {}
        
        # Common crypto terms to track
        topics = ['bitcoin', 'btc', 'ethereum', 'eth', 'defi', 'nft', 
                 'regulation', 'sec', 'hack', 'pump', 'dump', 'bull', 'bear']
        
        for article in articles:
            text = (article['headline'] + ' ' + article.get('summary', '')).lower()
            for topic in topics:
                if topic in text:
                    topic_count[topic] = topic_count.get(topic, 0) + 1
        
        # Sort by count
        return dict(sorted(topic_count.items(), key=lambda x: x[1], reverse=True))
    
    def format_for_telegram(self, article: Dict, sentiment: Dict = None) -> str:
        """Format article for Telegram message"""
        msg = f"📰 *{article['headline']}*\n"
        msg += f"📡 Source: {article['source']}\n"
        
        if sentiment:
            msg += f"🎯 Sentiment: {sentiment['sentiment_label']}\n"
            msg += f"⚡ Impact: {sentiment['impact_level']}\n"
            msg += f"📊 Score: {sentiment['combined_score']:.3f}\n"
            
            if sentiment['keywords']:
                msg += f"🔑 Keywords: {', '.join(sentiment['keywords'])}\n"
        
        msg += f"\n🔗 [Read More]({article['url']})"
        
        return msg


# Example usage and testing
if __name__ == "__main__":
    from news_sources import NEWS_SOURCES
    
    scraper = CryptoNewsScraper()
    
    print("🌐 FETCHING REAL-TIME CRYPTO NEWS...\n")
    
    # Fetch news from all sources
    articles = scraper.fetch_all_news(NEWS_SOURCES)
    
    print(f"📊 Total articles fetched: {len(articles)}\n")
    
    # Get recent news only (last 24 hours)
    recent_articles = scraper.filter_recent_news(articles, hours=24)
    print(f"🕐 Articles from last 24 hours: {len(recent_articles)}\n")
    
    # Show trending topics
    trending = scraper.get_trending_topics(articles)
    print("🔥 TRENDING TOPICS:")
    for topic, count in list(trending.items())[:5]:
        print(f"  • {topic}: {count} mentions")
    
    # Display first 5 articles
    print("\n📰 LATEST HEADLINES:")
    print("="*60)
    
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['headline']}")
        print(f"   Source: {article['source']} | Weight: {article['source_weight']}")
        print(f"   Published: {article['published']}")
        print(f"   URL: {article['url'][:50]}...")
        
    # Example: Search for specific news
    print("\n🔍 SEARCHING FOR 'SEC' OR 'REGULATION' NEWS:")
    print("="*60)
    
    regulatory_news = scraper.search_for_keywords(articles, ['sec', 'regulation', 'legal'])
    for article in regulatory_news[:3]:
        print(f"\n• {article['headline']}")
        print(f"  Source: {article['source']}")
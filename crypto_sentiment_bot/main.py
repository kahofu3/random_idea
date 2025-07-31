"""
Crypto Sentiment Analysis Telegram Bot
Main application that combines news scraping, sentiment analysis, and Telegram alerts
"""

import os
import asyncio
import logging
from datetime import datetime
import json
from typing import List, Dict
import schedule
import time
import threading

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Import our modules
import sys
sys.path.append('src')
from news_scraper import CryptoNewsScraper
from sentiment_analyzer import CryptoSentimentAnalyzer
from news_sources import NEWS_SOURCES, TRACKED_EVENTS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CryptoSentimentBot:
    def __init__(self, telegram_token: str, chat_id: str = None):
        self.token = telegram_token
        self.chat_id = chat_id
        self.scraper = CryptoNewsScraper()
        self.analyzer = CryptoSentimentAnalyzer()
        self.app = Application.builder().token(telegram_token).build()
        
        # Store analyzed news to avoid duplicates
        self.analyzed_urls = set()
        self.last_summary = None
        
        # Setup handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup telegram command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("news", self.get_latest_news))
        self.app.add_handler(CommandHandler("summary", self.get_market_summary))
        self.app.add_handler(CommandHandler("alerts", self.toggle_alerts))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 *Crypto Sentiment Analysis Bot*

I analyze crypto news sentiment to help you understand market mood!

*Commands:*
/news - Get latest analyzed news
/summary - Get market sentiment summary  
/alerts on/off - Toggle automatic alerts
/status - Check bot status
/help - Show detailed help

*What I track:*
• Major crypto news sites (CoinDesk, CoinTelegraph, etc.)
• Regulatory news (SEC, government actions)
• Institutional moves (Tesla, MicroStrategy, etc.)
• Technical events (hacks, upgrades)

⚠️ *Disclaimer:* This is for information only, not financial advice!
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
        
        # Store chat ID for alerts
        if not self.chat_id:
            self.chat_id = update.effective_chat.id
            logger.info(f"Set chat_id to {self.chat_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed help"""
        help_text = """
📚 *Detailed Help*

*How Sentiment Analysis Works:*
• I analyze headlines using AI (VADER + TextBlob)
• Custom crypto vocabulary (moon, dump, HODL, etc.)
• Source credibility weighting
• Impact level assessment

*Sentiment Levels:*
🚀 Very Positive: Strong bullish signals
📈 Positive: Moderate good news
➡️ Neutral: Mixed or unclear signals
📉 Negative: Moderate bad news
💥 Very Negative: Strong bearish signals

*Impact Levels:*
• HIGH: Major market-moving news
• MEDIUM: Notable but limited impact
• LOW: Minor news, likely no effect

*Tips:*
• High-impact + strong sentiment = stronger signal
• Multiple sources reporting = more reliable
• Always verify with multiple sources
• Sentiment ≠ guaranteed price movement
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def get_latest_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fetch and analyze latest news"""
        await update.message.reply_text("🔄 Fetching latest crypto news...")
        
        try:
            # Fetch news
            articles = self.scraper.fetch_all_news(NEWS_SOURCES)
            recent_articles = self.scraper.filter_recent_news(articles, hours=6)
            
            if not recent_articles:
                await update.message.reply_text("No recent news found in the last 6 hours.")
                return
            
            # Analyze top 5 articles
            messages = []
            for article in recent_articles[:5]:
                if article['url'] not in self.analyzed_urls:
                    # Analyze sentiment
                    sentiment = self.analyzer.analyze_headline(
                        article['headline'], 
                        article['source_weight']
                    )
                    
                    # Format message
                    msg = self.scraper.format_for_telegram(article, sentiment)
                    messages.append(msg)
                    
                    # Mark as analyzed
                    self.analyzed_urls.add(article['url'])
            
            # Send messages
            if messages:
                for msg in messages:
                    await update.message.reply_text(msg, parse_mode='Markdown', 
                                                  disable_web_page_preview=True)
            else:
                await update.message.reply_text("All recent news has already been analyzed.")
                
        except Exception as e:
            logger.error(f"Error in get_latest_news: {str(e)}")
            await update.message.reply_text(f"❌ Error fetching news: {str(e)}")
    
    async def get_market_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get overall market sentiment summary"""
        await update.message.reply_text("📊 Analyzing market sentiment...")
        
        try:
            # Fetch all recent news
            articles = self.scraper.fetch_all_news(NEWS_SOURCES)
            recent_articles = self.scraper.filter_recent_news(articles, hours=24)
            
            if not recent_articles:
                await update.message.reply_text("No news found in the last 24 hours.")
                return
            
            # Analyze all headlines
            analyses = []
            for article in recent_articles:
                sentiment = self.analyzer.analyze_headline(
                    article['headline'],
                    article['source_weight']
                )
                sentiment['source'] = article['source']
                analyses.append(sentiment)
            
            # Get summary
            summary = self.analyzer.get_market_sentiment_summary(analyses)
            
            # Get trending topics
            trending = self.scraper.get_trending_topics(recent_articles)
            
            # Format summary message
            msg = f"""
📊 *24h Market Sentiment Summary*

🎯 Overall: {summary['overall_sentiment']}
📈 Score: {summary['average_score']:.3f}
📰 Articles Analyzed: {summary['total_articles']}
⚡ High-Impact News: {summary['high_impact_count']}

*Sentiment Distribution:*
🚀 Very Positive: {summary['sentiment_distribution']['very_positive']}
📈 Positive: {summary['sentiment_distribution']['positive']}
➡️ Neutral: {summary['sentiment_distribution']['neutral']}
📉 Negative: {summary['sentiment_distribution']['negative']}
💥 Very Negative: {summary['sentiment_distribution']['very_negative']}

*Trending Topics:*
"""
            for topic, count in list(trending.items())[:5]:
                msg += f"• {topic}: {count} mentions\n"
            
            msg += f"\n💡 *Analysis:*\n{summary['recommendation']}"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            
            # Store for later reference
            self.last_summary = summary
            
        except Exception as e:
            logger.error(f"Error in get_market_summary: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check bot status"""
        status_msg = f"""
🤖 *Bot Status*

✅ Bot is running
📰 News sources configured: {len(NEWS_SOURCES)}
🔍 Analyzed articles: {len(self.analyzed_urls)}
⏰ Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Active News Sources:*
"""
        for source_id, source in NEWS_SOURCES.items():
            status_msg += f"• {source['name']} (weight: {source['weight']})\n"
            
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def toggle_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle automatic alerts"""
        if not context.args:
            await update.message.reply_text("Usage: /alerts on or /alerts off")
            return
            
        if context.args[0].lower() == 'on':
            context.job_queue.run_repeating(
                self.check_high_impact_news,
                interval=1800,  # 30 minutes
                first=10,
                name='news_alerts'
            )
            await update.message.reply_text("✅ Alerts enabled! Will check every 30 minutes.")
        elif context.args[0].lower() == 'off':
            jobs = context.job_queue.get_jobs_by_name('news_alerts')
            for job in jobs:
                job.schedule_removal()
            await update.message.reply_text("❌ Alerts disabled.")
    
    async def check_high_impact_news(self, context: ContextTypes.DEFAULT_TYPE):
        """Check for high-impact news and send alerts"""
        try:
            # Fetch latest news
            articles = self.scraper.fetch_all_news(NEWS_SOURCES)
            recent_articles = self.scraper.filter_recent_news(articles, hours=1)
            
            high_impact_alerts = []
            
            for article in recent_articles:
                if article['url'] not in self.analyzed_urls:
                    # Analyze sentiment
                    sentiment = self.analyzer.analyze_headline(
                        article['headline'],
                        article['source_weight']
                    )
                    
                    # Check if high impact
                    if sentiment['impact_level'] in ['HIGH', 'MEDIUM-HIGH']:
                        msg = "🚨 *HIGH IMPACT NEWS ALERT*\n\n"
                        msg += self.scraper.format_for_telegram(article, sentiment)
                        high_impact_alerts.append(msg)
                    
                    self.analyzed_urls.add(article['url'])
            
            # Send alerts
            if high_impact_alerts and self.chat_id:
                for alert in high_impact_alerts:
                    await context.bot.send_message(
                        chat_id=self.chat_id,
                        text=alert,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    
        except Exception as e:
            logger.error(f"Error in check_high_impact_news: {str(e)}")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Crypto Sentiment Bot...")
        self.app.run_polling()


# Example configuration
if __name__ == "__main__":
    # You need to set these environment variables or replace with your values
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', None)  # Optional, will be set on /start
    
    if TELEGRAM_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️  Please set your Telegram bot token!")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your token and replace 'YOUR_BOT_TOKEN_HERE'")
        exit(1)
    
    # Create and run bot
    bot = CryptoSentimentBot(TELEGRAM_TOKEN, CHAT_ID)
    bot.run()
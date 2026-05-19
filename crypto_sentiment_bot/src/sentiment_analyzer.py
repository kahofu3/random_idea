"""
Sentiment Analyzer for Crypto News
Uses VADER and TextBlob for sentiment analysis
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re
from datetime import datetime
from typing import Dict, List, Tuple
import json

class CryptoSentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        
        # Add crypto-specific terms to VADER lexicon
        self.crypto_lexicon = {
            # Positive terms
            'moon': 3.0, 'mooning': 3.0, 'bullish': 2.5, 'pump': 2.0,
            'hodl': 1.5, 'adoption': 2.0, 'institutional': 2.0,
            'halving': 1.5, 'defi': 1.0, 'breakout': 2.0,
            
            # Negative terms  
            'dump': -3.0, 'crash': -3.0, 'scam': -3.0, 'hack': -3.0,
            'bearish': -2.5, 'plunge': -2.5, 'fraud': -3.0,
            'bubble': -2.0, 'fud': -1.5, 'rekt': -2.5
        }
        
        # Update VADER with crypto terms
        self.vader.lexicon.update(self.crypto_lexicon)
        
    def analyze_headline(self, headline: str, source_weight: float = 1.0) -> Dict:
        """
        Analyze a single headline for sentiment
        Returns detailed sentiment scores and interpretation
        """
        # Clean headline
        clean_headline = self._preprocess_text(headline)
        
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(clean_headline)
        
        # TextBlob sentiment
        blob = TextBlob(clean_headline)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # Combined score (weighted average)
        combined_score = (vader_scores['compound'] * 0.7 + textblob_polarity * 0.3) * source_weight
        
        # Determine impact level
        impact = self._determine_impact(headline, combined_score)
        
        # Get sentiment label
        sentiment_label = self._get_sentiment_label(combined_score)
        
        # Check for specific keywords
        keywords_found = self._extract_keywords(headline)
        
        return {
            'headline': headline,
            'processed_text': clean_headline,
            'timestamp': datetime.now().isoformat(),
            'vader_scores': vader_scores,
            'textblob_scores': {
                'polarity': textblob_polarity,
                'subjectivity': textblob_subjectivity
            },
            'combined_score': combined_score,
            'sentiment_label': sentiment_label,
            'impact_level': impact,
            'keywords': keywords_found,
            'confidence': self._calculate_confidence(vader_scores, textblob_polarity)
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and prepare text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Keep important punctuation for sentiment
        text = re.sub(r'[^a-zA-Z0-9\s!?.$%]', '', text)
        
        return text.strip()
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert numerical score to label"""
        if score >= 0.5:
            return "Very Positive 🚀"
        elif score >= 0.1:
            return "Positive 📈"
        elif score >= -0.1:
            return "Neutral ➡️"
        elif score >= -0.5:
            return "Negative 📉"
        else:
            return "Very Negative 💥"
    
    def _determine_impact(self, headline: str, sentiment_score: float) -> str:
        """Determine potential market impact"""
        headline_lower = headline.lower()
        
        # High impact keywords
        high_impact = ['sec', 'ban', 'regulation', 'tesla', 'microstrategy', 
                      'government', 'hack', 'billion', 'etf']
        
        # Check for high impact
        for keyword in high_impact:
            if keyword in headline_lower:
                if abs(sentiment_score) > 0.3:
                    return "HIGH"
        
        # Medium impact based on sentiment strength
        if abs(sentiment_score) > 0.5:
            return "MEDIUM-HIGH"
        elif abs(sentiment_score) > 0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_keywords(self, headline: str) -> List[str]:
        """Extract important keywords from headline"""
        keywords = []
        headline_lower = headline.lower()
        
        # Check positive keywords
        from news_sources import MAJOR_KEYWORDS
        for keyword in MAJOR_KEYWORDS['positive']:
            if keyword in headline_lower:
                keywords.append(f"+{keyword}")
        
        # Check negative keywords
        for keyword in MAJOR_KEYWORDS['negative']:
            if keyword in headline_lower:
                keywords.append(f"-{keyword}")
        
        return keywords
    
    def _calculate_confidence(self, vader_scores: Dict, textblob_polarity: float) -> float:
        """Calculate confidence in the sentiment analysis"""
        # If VADER and TextBlob agree, higher confidence
        vader_sentiment = vader_scores['compound']
        
        if (vader_sentiment > 0 and textblob_polarity > 0) or \
           (vader_sentiment < 0 and textblob_polarity < 0):
            agreement_bonus = 0.2
        else:
            agreement_bonus = -0.1
        
        # Base confidence on VADER's individual scores
        confidence = (abs(vader_scores['pos']) + abs(vader_scores['neg'])) / 2 + agreement_bonus
        
        return min(max(confidence, 0), 1)  # Clamp between 0 and 1
    
    def analyze_batch(self, headlines: List[Tuple[str, str, float]]) -> List[Dict]:
        """Analyze multiple headlines"""
        results = []
        for headline, source, weight in headlines:
            analysis = self.analyze_headline(headline, weight)
            analysis['source'] = source
            results.append(analysis)
        
        return results
    
    def get_market_sentiment_summary(self, analyses: List[Dict]) -> Dict:
        """Get overall market sentiment from multiple analyses"""
        if not analyses:
            return {"error": "No analyses provided"}
        
        total_score = sum(a['combined_score'] for a in analyses)
        avg_score = total_score / len(analyses)
        
        high_impact_news = [a for a in analyses if a['impact_level'] in ['HIGH', 'MEDIUM-HIGH']]
        
        return {
            'overall_sentiment': self._get_sentiment_label(avg_score),
            'average_score': avg_score,
            'total_articles': len(analyses),
            'high_impact_count': len(high_impact_news),
            'sentiment_distribution': {
                'very_positive': len([a for a in analyses if 'Very Positive' in a['sentiment_label']]),
                'positive': len([a for a in analyses if a['sentiment_label'] == 'Positive 📈']),
                'neutral': len([a for a in analyses if 'Neutral' in a['sentiment_label']]),
                'negative': len([a for a in analyses if a['sentiment_label'] == 'Negative 📉']),
                'very_negative': len([a for a in analyses if 'Very Negative' in a['sentiment_label']])
            },
            'recommendation': self._get_recommendation(avg_score, high_impact_news)
        }
    
    def _get_recommendation(self, avg_score: float, high_impact_news: List[Dict]) -> str:
        """Generate a recommendation based on sentiment"""
        if len(high_impact_news) > 0:
            if avg_score > 0.3:
                return "🟢 Strong positive sentiment with high-impact news. Market may be bullish."
            elif avg_score < -0.3:
                return "🔴 Strong negative sentiment with high-impact news. Exercise caution."
            else:
                return "🟡 Mixed signals with high-impact news. Wait for clearer direction."
        else:
            if abs(avg_score) < 0.2:
                return "⚪ Low sentiment signal. No major market moves expected."
            else:
                return "🟡 Moderate sentiment but low-impact news. Monitor closely."


# Example usage
if __name__ == "__main__":
    analyzer = CryptoSentimentAnalyzer()
    
    # Test with example headlines
    from news_sources import EXAMPLE_NEWS
    
    print("🔍 CRYPTO NEWS SENTIMENT ANALYSIS EXAMPLES\n")
    print("="*60)
    
    for news_item in EXAMPLE_NEWS:
        result = analyzer.analyze_headline(news_item['headline'])
        
        print(f"\n📰 Headline: {news_item['headline']}")
        print(f"📡 Source: {news_item['source']}")
        print(f"🎯 Expected: {news_item['expected_sentiment']}")
        print(f"🤖 Analyzed: {result['sentiment_label']}")
        print(f"📊 Score: {result['combined_score']:.3f}")
        print(f"⚡ Impact: {result['impact_level']}")
        print(f"🔑 Keywords: {', '.join(result['keywords']) if result['keywords'] else 'None'}")
        print(f"💪 Confidence: {result['confidence']:.1%}")
        print("-"*60)
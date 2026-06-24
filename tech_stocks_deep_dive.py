"""
Tech Stocks Deep Dive Analysis
Focuses on finding high-conviction technology opportunities
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import the main analyzer
from stock_analysis_2025 import StockAnalyzer

class TechStockAnalyzer(StockAnalyzer):
    def __init__(self):
        super().__init__()
        
        # Expanded tech universe including high-growth and AI-focused companies
        self.stock_universe = {
            # Existing top tech from main analysis
            'GOOGL': 'Alphabet Inc',
            'PLTR': 'Palantir Technologies',
            'ARM': 'Arm Holdings',
            'SMCI': 'Super Micro Computer',
            'META': 'Meta Platforms',
            'AVGO': 'Broadcom Inc',
            
            # Additional AI/ML focused
            'SNOW': 'Snowflake Inc',
            'CRWD': 'CrowdStrike Holdings',
            'DDOG': 'Datadog Inc',
            'NET': 'Cloudflare Inc',
            'MDB': 'MongoDB Inc',
            'PATH': 'UiPath Inc',
            'AI': 'C3.ai Inc',
            
            # Semiconductor & Hardware
            'QCOM': 'Qualcomm Inc',
            'MU': 'Micron Technology',
            'LRCX': 'Lam Research',
            'KLAC': 'KLA Corporation',
            'AMAT': 'Applied Materials',
            'ASML': 'ASML Holding',
            'TSM': 'Taiwan Semiconductor',
            
            # Software & Cloud
            'CRM': 'Salesforce Inc',
            'NOW': 'ServiceNow Inc',
            'ADBE': 'Adobe Inc',
            'TEAM': 'Atlassian Corp',
            'VEEV': 'Veeva Systems',
            'WDAY': 'Workday Inc',
            'ZM': 'Zoom Video',
            'DOCU': 'DocuSign Inc',
            
            # Cybersecurity
            'PANW': 'Palo Alto Networks',
            'FTNT': 'Fortinet Inc',
            'ZS': 'Zscaler Inc',
            'OKTA': 'Okta Inc',
            
            # Gaming & Entertainment Tech
            'RBLX': 'Roblox Corp',
            'U': 'Unity Software',
            'TTWO': 'Take-Two Interactive',
            'EA': 'Electronic Arts',
            
            # Fintech
            'SQ': 'Block Inc',
            'PYPL': 'PayPal Holdings',
            'COIN': 'Coinbase Global',
            'SOFI': 'SoFi Technologies',
            
            # Electric Vehicles & Clean Tech
            'RIVN': 'Rivian Automotive',
            'LCID': 'Lucid Group',
            'NIO': 'NIO Inc',
            'XPEV': 'XPeng Inc'
        }
        
    def analyze_tech_specific_factors(self, info, df):
        """Analyze tech-specific factors for conviction scoring"""
        tech_score = 50  # Base score
        
        # Revenue growth is crucial for tech
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth > 0.30:  # 30%+ growth
            tech_score += 20
        elif revenue_growth > 0.20:  # 20%+ growth
            tech_score += 15
        elif revenue_growth > 0.10:  # 10%+ growth
            tech_score += 10
        elif revenue_growth < 0:  # Negative growth
            tech_score -= 15
            
        # Gross margins - tech should have high margins
        gross_margin = info.get('grossMargins', 0)
        if gross_margin > 0.70:  # 70%+ margins
            tech_score += 15
        elif gross_margin > 0.50:  # 50%+ margins
            tech_score += 10
        elif gross_margin < 0.30:  # Low margins
            tech_score -= 10
            
        # R&D spending (shows innovation)
        operating_margin = info.get('operatingMargins', 0)
        if 0.10 < operating_margin < 0.25:  # Healthy but investing in R&D
            tech_score += 5
            
        # Market position
        market_cap = info.get('marketCap', 0)
        if market_cap > 100e9:  # $100B+ (established leader)
            tech_score += 10
        elif market_cap > 10e9:  # $10B+ (mid-cap growth)
            tech_score += 5
            
        # Check for momentum in last 3 months
        if len(df) >= 60:
            three_month_return = (df['Close'].iloc[-1] / df['Close'].iloc[-60] - 1) * 100
            if three_month_return > 20:
                tech_score += 10
            elif three_month_return > 10:
                tech_score += 5
            elif three_month_return < -20:
                tech_score -= 10
                
        return min(100, max(0, tech_score))
    
    def calculate_ai_momentum_score(self, ticker, info):
        """Special scoring for AI-related companies"""
        ai_keywords = ['artificial intelligence', 'machine learning', 'ai', 'neural', 
                       'deep learning', 'computer vision', 'nlp', 'data science']
        
        ai_score_boost = 0
        
        # Check if company description mentions AI
        business_summary = info.get('longBusinessSummary', '').lower()
        for keyword in ai_keywords:
            if keyword in business_summary:
                ai_score_boost += 5
                break
                
        # Special boost for known AI leaders
        ai_leaders = ['NVDA', 'GOOGL', 'MSFT', 'META', 'PLTR', 'SNOW', 'AI', 
                      'CRWD', 'DDOG', 'NET', 'ARM', 'AVGO']
        if ticker in ai_leaders:
            ai_score_boost += 10
            
        return ai_score_boost
    
    def generate_tech_recommendation(self, conviction_score, signals, targets, tech_factors):
        """Generate tech-specific recommendations"""
        base_rec = super().generate_recommendation(conviction_score, signals, targets)
        
        # Adjust for tech-specific factors
        if tech_factors > 70 and conviction_score > 60:
            base_rec['recommendation'] = "BUY"
            base_rec['action'] = "Strong growth momentum - accumulate"
        elif tech_factors > 60 and signals['rsi_value'] < 40:
            base_rec['recommendation'] = "BUY"
            base_rec['action'] = "Oversold growth stock - buy the dip"
            
        return base_rec

def main():
    """Run focused tech stock analysis"""
    analyzer = TechStockAnalyzer()
    results = []
    
    print("=== Tech Stocks Deep Dive Analysis ===")
    print(f"Analyzing {len(analyzer.stock_universe)} technology stocks...\n")
    
    # First, let's look at our existing tech analysis
    try:
        existing_df = pd.read_csv('us_stock_analysis_2025.csv')
        tech_stocks = existing_df[existing_df['sector'].isin(['Technology', 'Communication Services'])]
        
        print("Current Tech Stock Rankings from Main Analysis:")
        print("=" * 60)
        tech_top = tech_stocks.nlargest(10, 'conviction_score')[['ticker', 'name', 'conviction_score', 'recommendation', 'rsi', 'target_30d', 'current_price']]
        
        for _, stock in tech_top.iterrows():
            pct_gain = ((stock['target_30d'] / stock['current_price']) - 1) * 100
            print(f"{stock['ticker']:6} - {stock['name']:25} Score: {stock['conviction_score']:.0f} | {stock['recommendation']:10} | 30d: {pct_gain:+.1f}%")
        
    except:
        pass
    
    print("\n\nAnalyzing Additional Tech Stocks for High-Conviction Opportunities...")
    print("=" * 60)
    
    high_conviction_techs = []
    
    for ticker in analyzer.stock_universe:
        if ticker in ['GOOGL', 'PLTR', 'ARM', 'SMCI', 'META', 'AVGO']:
            continue  # Skip already analyzed
            
        print(f"Analyzing {ticker}...", end=' ')
        
        stock_data = analyzer.fetch_stock_data(ticker)
        if not stock_data or stock_data['data'].empty:
            print("No data")
            continue
            
        df = stock_data['data']
        info = stock_data['info']
        
        # Calculate all indicators
        indicators = analyzer.calculate_technical_indicators(df)
        signals = analyzer.calculate_signals(df, indicators)
        targets = analyzer.calculate_price_targets(df, indicators)
        fundamentals = analyzer.analyze_fundamentals(info)
        
        # Tech-specific analysis
        tech_score = analyzer.analyze_tech_specific_factors(info, df)
        ai_boost = analyzer.calculate_ai_momentum_score(ticker, info)
        
        # Adjusted conviction score
        base_conviction = analyzer.calculate_conviction_score(signals, fundamentals)
        tech_conviction = (base_conviction * 0.6 + tech_score * 0.4 + ai_boost)
        tech_conviction = min(100, tech_conviction)
        
        recommendation = analyzer.generate_tech_recommendation(tech_conviction, signals, targets, tech_score)
        
        result = {
            'ticker': ticker,
            'name': stock_data['name'],
            'current_price': targets['current_price'],
            'conviction_score': tech_conviction,
            'tech_score': tech_score,
            'ai_boost': ai_boost,
            'recommendation': recommendation['recommendation'],
            'rsi': signals['rsi_value'],
            'target_30d': targets['target_30d'],
            'target_90d': targets['target_90d'],
            'revenue_growth': info.get('revenueGrowth', 0),
            'gross_margin': info.get('grossMargins', 0),
            'market_cap_b': info.get('marketCap', 0) / 1e9
        }
        
        results.append(result)
        print(f"Score: {tech_conviction:.1f} - {recommendation['recommendation']}")
        
        if tech_conviction >= 65:
            high_conviction_techs.append(result)
    
    # Create DataFrame and save
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('conviction_score', ascending=False)
    results_df.to_csv('tech_stocks_analysis_2025.csv', index=False)
    
    # Display high conviction tech stocks
    print("\n\n")
    print("=" * 80)
    print("HIGH-CONVICTION TECH STOCKS (Score >= 65)")
    print("=" * 80)
    
    if high_conviction_techs:
        high_conviction_techs.sort(key=lambda x: x['conviction_score'], reverse=True)
        
        for stock in high_conviction_techs:
            gain_30d = ((stock['target_30d'] / stock['current_price']) - 1) * 100
            gain_90d = ((stock['target_90d'] / stock['current_price']) - 1) * 100
            
            print(f"\n{stock['ticker']} - {stock['name']}")
            print(f"Conviction Score: {stock['conviction_score']:.1f} (Tech Score: {stock['tech_score']}, AI Boost: {stock['ai_boost']})")
            print(f"Recommendation: {stock['recommendation']}")
            print(f"Current Price: ${stock['current_price']:.2f}")
            print(f"30-Day Target: ${stock['target_30d']:.2f} ({gain_30d:+.1f}%)")
            print(f"90-Day Target: ${stock['target_90d']:.2f} ({gain_90d:+.1f}%)")
            print(f"Revenue Growth: {stock['revenue_growth']*100:.1f}%")
            print(f"Gross Margin: {stock['gross_margin']*100:.1f}%")
            print(f"RSI: {stock['rsi']:.1f}")
    else:
        print("\nNo additional high-conviction tech stocks found in extended analysis.")
        
    # Show best opportunities combining all factors
    print("\n\n")
    print("=" * 80)
    print("TOP 10 TECH OPPORTUNITIES (Combined Analysis)")
    print("=" * 80)
    
    all_results = results_df.nlargest(10, 'conviction_score')
    print("\n| Ticker | Company | Score | Rec | RSI | 30d Return | Rev Growth |")
    print("|--------|---------|-------|-----|-----|------------|------------|")
    
    for _, stock in all_results.iterrows():
        gain_30d = ((stock['target_30d'] / stock['current_price']) - 1) * 100
        print(f"| {stock['ticker']:6} | {stock['name'][:20]:20} | {stock['conviction_score']:5.1f} | {stock['recommendation'][:4]:4} | {stock['rsi']:4.1f} | {gain_30d:+10.1f}% | {stock['revenue_growth']*100:10.1f}% |")

if __name__ == "__main__":
    main()
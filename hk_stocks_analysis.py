"""
Hong Kong Stock Market Analysis
Analyzes HSI components and major HK-listed stocks for high-conviction opportunities
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

class HKStockAnalyzer(StockAnalyzer):
    def __init__(self):
        super().__init__()
        
        # Major Hong Kong stocks including HSI components and popular listings
        # Using .HK suffix for Hong Kong Exchange
        self.stock_universe = {
            # Technology & Internet Giants
            '0700.HK': 'Tencent Holdings',
            '9988.HK': 'Alibaba Group',
            '3690.HK': 'Meituan',
            '9618.HK': 'JD.com',
            '1810.HK': 'Xiaomi Corp',
            '2382.HK': 'Sunny Optical',
            '0992.HK': 'Lenovo Group',
            '9888.HK': 'Baidu Inc',
            '9961.HK': 'Trip.com',
            '2018.HK': 'AAC Technologies',
            '1024.HK': 'Kuaishou Technology',
            '0772.HK': 'China Literature',
            
            # Financial Services
            '0005.HK': 'HSBC Holdings',
            '0011.HK': 'Hang Seng Bank',
            '0388.HK': 'HK Exchanges & Clearing',
            '1299.HK': 'AIA Group',
            '2318.HK': 'Ping An Insurance',
            '3988.HK': 'Bank of China',
            '1398.HK': 'ICBC',
            '0939.HK': 'China Construction Bank',
            '2388.HK': 'BOC Hong Kong',
            '2628.HK': 'China Life Insurance',
            
            # Property & Real Estate
            '0001.HK': 'CK Hutchison',
            '0016.HK': 'Sun Hung Kai Properties',
            '0017.HK': 'New World Development',
            '0012.HK': 'Henderson Land',
            '0101.HK': 'Hang Lung Properties',
            '0688.HK': 'China Overseas',
            '2007.HK': 'Country Garden',
            '0083.HK': 'Sino Land',
            
            # Consumer & Retail
            '9999.HK': 'NetEase',
            '2331.HK': 'Li Ning',
            '1929.HK': 'Chow Tai Fook',
            '2020.HK': 'ANTA Sports',
            '6969.HK': 'Smoore International',
            '0291.HK': 'China Resources Beer',
            '2319.HK': 'China Mengniu Dairy',
            '0175.HK': 'Geely Auto',
            
            # Energy & Resources
            '0857.HK': 'PetroChina',
            '0883.HK': 'CNOOC',
            '0386.HK': 'Sinopec',
            '0003.HK': 'HK & China Gas',
            '0002.HK': 'CLP Holdings',
            
            # Healthcare & Biotech
            '1177.HK': 'Sino Biopharmaceutical',
            '2269.HK': 'WuXi Biologics',
            '1066.HK': 'Weigao Group',
            '6160.HK': 'BeiGene',
            '9926.HK': 'Akeso Inc',
            '1548.HK': 'Genscript Biotech',
            
            # Electric Vehicles & New Energy
            '9868.HK': 'XPeng Motors',
            '9866.HK': 'NIO Inc',
            '1211.HK': 'BYD Company',
            '2015.HK': 'Li Auto',
            
            # Telecommunications
            '0941.HK': 'China Mobile',
            '0728.HK': 'China Telecom',
            '0762.HK': 'China Unicom'
        }
        
    def analyze_hk_specific_factors(self, info, df, ticker):
        """Analyze Hong Kong market specific factors"""
        hk_score = 50  # Base score
        
        # Check for mainland China exposure (important for HK stocks)
        company_name = info.get('longName', '').lower()
        if any(word in company_name for word in ['china', 'chinese', '中国']):
            # China exposure can be positive or negative depending on sentiment
            # For 2025, assuming moderate positive given recovery
            hk_score += 5
            
        # Market cap in HKD
        market_cap = info.get('marketCap', 0)
        if market_cap > 500e9:  # >500B HKD (large cap)
            hk_score += 10
        elif market_cap > 100e9:  # >100B HKD (mid cap)
            hk_score += 5
            
        # Trading volume liquidity check
        avg_volume = info.get('averageVolume', 0)
        if avg_volume > 10000000:  # 10M+ shares daily
            hk_score += 10
        elif avg_volume > 5000000:  # 5M+ shares daily
            hk_score += 5
            
        # Dividend yield (important for HK investors)
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield > 0.05:  # 5%+ yield
            hk_score += 15
        elif dividend_yield > 0.03:  # 3%+ yield
            hk_score += 10
        elif dividend_yield > 0.01:  # 1%+ yield
            hk_score += 5
            
        # Southbound trading eligibility (Stock Connect)
        # Major index constituents are typically eligible
        if ticker in ['0700.HK', '9988.HK', '0005.HK', '1299.HK', '2318.HK', 
                      '3690.HK', '9618.HK', '0388.HK', '1810.HK']:
            hk_score += 10
            
        # Recent momentum (important in HK market)
        if len(df) >= 20:
            one_month_return = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
            if one_month_return > 10:
                hk_score += 10
            elif one_month_return > 5:
                hk_score += 5
            elif one_month_return < -10:
                hk_score -= 10
                
        return min(100, max(0, hk_score))
    
    def calculate_china_tech_score(self, ticker, info):
        """Special scoring for Chinese tech giants"""
        china_tech_boost = 0
        
        # Major Chinese tech companies
        china_tech_leaders = ['0700.HK', '9988.HK', '3690.HK', '9618.HK', 
                              '1810.HK', '9888.HK', '9961.HK', '1024.HK']
        
        if ticker in china_tech_leaders:
            china_tech_boost += 15  # Regulatory clarity improving in 2025
            
            # Additional boost for super giants
            if ticker in ['0700.HK', '9988.HK']:  # Tencent, Alibaba
                china_tech_boost += 5
                
        return china_tech_boost
    
    def generate_hk_recommendation(self, conviction_score, signals, targets, hk_factors):
        """Generate HK-specific recommendations"""
        base_rec = super().generate_recommendation(conviction_score, signals, targets)
        
        # Adjust for HK market characteristics
        if hk_factors > 70 and conviction_score > 65:
            base_rec['recommendation'] = "STRONG BUY"
            base_rec['action'] = "High quality HK stock - accumulate"
        elif hk_factors > 60 and signals['rsi_value'] < 40:
            base_rec['recommendation'] = "BUY"
            base_rec['action'] = "Oversold quality name - good entry"
            
        return base_rec

def main():
    """Run Hong Kong stock analysis"""
    analyzer = HKStockAnalyzer()
    results = []
    
    print("=" * 80)
    print("HONG KONG STOCK MARKET ANALYSIS")
    print("=" * 80)
    print(f"Analyzing {len(analyzer.stock_universe)} major Hong Kong stocks...\n")
    
    high_conviction_stocks = []
    tech_stocks = []
    financial_stocks = []
    
    for ticker in analyzer.stock_universe:
        print(f"Analyzing {ticker} - {analyzer.stock_universe[ticker]}...", end=' ')
        
        try:
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
            
            # HK-specific analysis
            hk_score = analyzer.analyze_hk_specific_factors(info, df, ticker)
            china_tech_boost = analyzer.calculate_china_tech_score(ticker, info)
            
            # Adjusted conviction score
            base_conviction = analyzer.calculate_conviction_score(signals, fundamentals)
            hk_conviction = (base_conviction * 0.5 + hk_score * 0.3 + 
                            fundamentals['fundamental_score'] * 0.2 + china_tech_boost)
            hk_conviction = min(100, hk_conviction)
            
            recommendation = analyzer.generate_hk_recommendation(
                hk_conviction, signals, targets, hk_score)
            
            # Get current price in HKD
            current_price = targets['current_price']
            
            result = {
                'ticker': ticker,
                'name': analyzer.stock_universe[ticker],
                'current_price': current_price,
                'conviction_score': hk_conviction,
                'hk_market_score': hk_score,
                'china_tech_boost': china_tech_boost,
                'recommendation': recommendation['recommendation'],
                'action': recommendation['action'],
                'rsi': signals['rsi_value'],
                'target_30d': targets['target_30d'],
                'target_90d': targets['target_90d'],
                'dividend_yield': info.get('dividendYield', 0),
                'market_cap_b_hkd': info.get('marketCap', 0) / 1e9,
                'pe_ratio': info.get('trailingPE', 0),
                'above_200_sma': signals['above_sma_200'],
                'volume_surge': signals['volume_surge']
            }
            
            results.append(result)
            print(f"Score: {hk_conviction:.1f} - {recommendation['recommendation']}")
            
            if hk_conviction >= 65:
                high_conviction_stocks.append(result)
                
            # Categorize by sector
            if ticker in ['0700.HK', '9988.HK', '3690.HK', '9618.HK', '1810.HK', 
                          '9888.HK', '9961.HK', '1024.HK', '9999.HK']:
                tech_stocks.append(result)
            elif ticker in ['0005.HK', '0011.HK', '0388.HK', '1299.HK', '2318.HK']:
                financial_stocks.append(result)
                
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Create DataFrame and save
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('conviction_score', ascending=False)
    results_df.to_csv('hk_stocks_analysis_2025.csv', index=False)
    
    # Display high conviction stocks
    print("\n\n")
    print("=" * 80)
    print("HIGH-CONVICTION HONG KONG STOCKS (Score >= 65)")
    print("=" * 80)
    
    if high_conviction_stocks:
        high_conviction_stocks.sort(key=lambda x: x['conviction_score'], reverse=True)
        
        for stock in high_conviction_stocks[:10]:  # Top 10
            gain_30d = ((stock['target_30d'] / stock['current_price']) - 1) * 100
            gain_90d = ((stock['target_90d'] / stock['current_price']) - 1) * 100
            
            print(f"\n{stock['ticker']} - {stock['name']}")
            print(f"Conviction Score: {stock['conviction_score']:.1f}")
            print(f"Recommendation: {stock['recommendation']}")
            print(f"Current Price: HK${stock['current_price']:.2f}")
            print(f"30-Day Target: HK${stock['target_30d']:.2f} ({gain_30d:+.1f}%)")
            print(f"90-Day Target: HK${stock['target_90d']:.2f} ({gain_90d:+.1f}%)")
            print(f"Dividend Yield: {stock['dividend_yield']*100:.1f}%")
            print(f"P/E Ratio: {stock['pe_ratio']:.1f}")
            print(f"RSI: {stock['rsi']:.1f}")
            print(f"Action: {stock['action']}")
    else:
        print("\nNo high-conviction stocks found (Score >= 65)")
        
    # Sector summaries
    print("\n\n")
    print("=" * 80)
    print("SECTOR ANALYSIS")
    print("=" * 80)
    
    print("\nTOP TECHNOLOGY STOCKS:")
    tech_sorted = sorted(tech_stocks, key=lambda x: x['conviction_score'], reverse=True)[:5]
    for stock in tech_sorted:
        gain_30d = ((stock['target_30d'] / stock['current_price']) - 1) * 100
        print(f"{stock['ticker']:8} {stock['name']:25} Score: {stock['conviction_score']:5.1f} | {stock['recommendation']:10} | 30d: {gain_30d:+6.1f}%")
    
    print("\nTOP FINANCIAL STOCKS:")
    fin_sorted = sorted(financial_stocks, key=lambda x: x['conviction_score'], reverse=True)[:5]
    for stock in fin_sorted:
        gain_30d = ((stock['target_30d'] / stock['current_price']) - 1) * 100
        print(f"{stock['ticker']:8} {stock['name']:25} Score: {stock['conviction_score']:5.1f} | {stock['recommendation']:10} | 30d: {gain_30d:+6.1f}%")
    
    # Market overview
    print("\n\n")
    print("=" * 80)
    print("HONG KONG MARKET OVERVIEW")
    print("=" * 80)
    
    avg_score = results_df['conviction_score'].mean()
    bullish = len(results_df[results_df['recommendation'].isin(['STRONG BUY', 'BUY'])])
    total = len(results_df)
    
    print(f"Average Conviction Score: {avg_score:.1f}/100")
    print(f"Bullish Stocks: {bullish}/{total} ({bullish/total*100:.1f}%)")
    print(f"High Conviction (65+): {len(high_conviction_stocks)} stocks")
    
    # Best dividend plays
    print("\nBEST DIVIDEND STOCKS:")
    div_stocks = results_df[results_df['dividend_yield'] > 0.03].nlargest(5, 'dividend_yield')
    for _, stock in div_stocks.iterrows():
        print(f"{stock['ticker']:8} {stock['name']:25} Yield: {stock['dividend_yield']*100:5.1f}% | Score: {stock['conviction_score']:5.1f}")

if __name__ == "__main__":
    main()
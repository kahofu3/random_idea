"""
US Stock Market Analysis and Prediction System
July 2025 Edition

This system analyzes US stocks using multiple technical indicators,
market trends, and AI-driven insights to identify high-conviction opportunities.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self):
        self.analysis_date = datetime.now()
        self.lookback_period = 365  # 1 year of data
        
        # Major US stock tickers to analyze (top companies by market cap and key sectors)
        self.stock_universe = {
            # Tech Giants
            'NVDA': 'Nvidia Corp',
            'MSFT': 'Microsoft Corp',
            'AAPL': 'Apple Inc',
            'GOOGL': 'Alphabet Inc',
            'META': 'Meta Platforms',
            'AMZN': 'Amazon.com Inc',
            'AVGO': 'Broadcom Inc',
            
            # AI & Semiconductors
            'AMD': 'Advanced Micro Devices',
            'SMCI': 'Super Micro Computer',
            'ARM': 'Arm Holdings',
            'PLTR': 'Palantir Technologies',
            
            # Financials
            'JPM': 'JPMorgan Chase',
            'BRK-B': 'Berkshire Hathaway',
            'V': 'Visa Inc',
            'MA': 'Mastercard Inc',
            'GS': 'Goldman Sachs',
            'BAC': 'Bank of America',
            
            # Healthcare
            'LLY': 'Eli Lilly',
            'UNH': 'UnitedHealth Group',
            'JNJ': 'Johnson & Johnson',
            'PFE': 'Pfizer Inc',
            'ABBV': 'AbbVie Inc',
            
            # Energy
            'XOM': 'Exxon Mobil',
            'CVX': 'Chevron Corp',
            'COP': 'ConocoPhillips',
            
            # Consumer/Retail
            'TSLA': 'Tesla Inc',
            'WMT': 'Walmart Inc',
            'HD': 'Home Depot',
            'PG': 'Procter & Gamble',
            'KO': 'Coca-Cola Co',
            
            # Industrials
            'CAT': 'Caterpillar Inc',
            'BA': 'Boeing Co',
            'UPS': 'United Parcel Service',
            
            # Utilities & Infrastructure
            'NEE': 'NextEra Energy',
            'SO': 'Southern Company',
            
            # Communication Services
            'DIS': 'Walt Disney Co',
            'NFLX': 'Netflix Inc',
            'T': 'AT&T Inc'
        }
        
    def fetch_stock_data(self, ticker):
        """Fetch historical stock data"""
        try:
            end_date = self.analysis_date
            start_date = end_date - timedelta(days=self.lookback_period)
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return None
            
            # Get additional info
            info = stock.info
            
            return {
                'data': df,
                'info': info,
                'ticker': ticker,
                'name': self.stock_universe.get(ticker, ticker)
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate various technical indicators"""
        indicators = {}
        
        # Price-based indicators
        indicators['sma_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        indicators['sma_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        indicators['sma_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        indicators['ema_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        indicators['ema_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # RSI
        indicators['rsi'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        indicators['macd'] = macd.macd()
        indicators['macd_signal'] = macd.macd_signal()
        indicators['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        indicators['bb_upper'] = bb.bollinger_hband()
        indicators['bb_middle'] = bb.bollinger_mavg()
        indicators['bb_lower'] = bb.bollinger_lband()
        indicators['bb_width'] = bb.bollinger_wband()
        
        # Stochastic
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        indicators['stoch_k'] = stoch.stoch()
        indicators['stoch_d'] = stoch.stoch_signal()
        
        # ATR (Volatility)
        indicators['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        indicators['volume_sma'] = ta.volume.volume_weighted_average_price(df['High'], df['Low'], df['Close'], df['Volume'])
        indicators['obv'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        
        return indicators
    
    def calculate_signals(self, df, indicators):
        """Generate trading signals based on technical indicators"""
        signals = {}
        latest = df.index[-1]
        
        # Trend signals
        current_price = df['Close'].iloc[-1]
        signals['above_sma_20'] = current_price > indicators['sma_20'].iloc[-1]
        signals['above_sma_50'] = current_price > indicators['sma_50'].iloc[-1]
        signals['above_sma_200'] = current_price > indicators['sma_200'].iloc[-1]
        
        # Golden/Death cross
        signals['golden_cross'] = (indicators['sma_50'].iloc[-1] > indicators['sma_200'].iloc[-1] and
                                   indicators['sma_50'].iloc[-5] <= indicators['sma_200'].iloc[-5])
        signals['death_cross'] = (indicators['sma_50'].iloc[-1] < indicators['sma_200'].iloc[-1] and
                                  indicators['sma_50'].iloc[-5] >= indicators['sma_200'].iloc[-5])
        
        # RSI signals
        rsi_value = indicators['rsi'].iloc[-1]
        signals['rsi_value'] = rsi_value
        signals['rsi_oversold'] = rsi_value < 30
        signals['rsi_overbought'] = rsi_value > 70
        signals['rsi_bullish_divergence'] = self._check_bullish_divergence(df['Close'], indicators['rsi'])
        
        # MACD signals
        signals['macd_bullish'] = indicators['macd'].iloc[-1] > indicators['macd_signal'].iloc[-1]
        signals['macd_cross_up'] = (indicators['macd'].iloc[-1] > indicators['macd_signal'].iloc[-1] and
                                    indicators['macd'].iloc[-2] <= indicators['macd_signal'].iloc[-2])
        
        # Bollinger Bands signals
        signals['bb_squeeze'] = indicators['bb_width'].iloc[-1] < indicators['bb_width'].quantile(0.2)
        signals['price_below_lower_bb'] = current_price < indicators['bb_lower'].iloc[-1]
        signals['price_above_upper_bb'] = current_price > indicators['bb_upper'].iloc[-1]
        
        # Volume signals
        signals['volume_surge'] = df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.5
        
        # Momentum score (0-100)
        momentum_score = 0
        if signals['above_sma_20']: momentum_score += 10
        if signals['above_sma_50']: momentum_score += 15
        if signals['above_sma_200']: momentum_score += 20
        if signals['macd_bullish']: momentum_score += 15
        if 40 < rsi_value < 60: momentum_score += 10
        elif 30 < rsi_value <= 40: momentum_score += 15
        elif 60 <= rsi_value < 70: momentum_score += 5
        if signals['volume_surge']: momentum_score += 10
        if not signals['bb_squeeze']: momentum_score += 5
        if signals['golden_cross']: momentum_score += 10
        
        signals['momentum_score'] = momentum_score
        
        return signals
    
    def _check_bullish_divergence(self, price, rsi, window=20):
        """Check for bullish divergence between price and RSI"""
        if len(price) < window * 2:
            return False
        
        # Find recent lows
        price_lows = price.rolling(window).min()
        rsi_lows = rsi.rolling(window).min()
        
        # Check if price made lower low but RSI made higher low
        if (price_lows.iloc[-1] < price_lows.iloc[-window] and
            rsi_lows.iloc[-1] > rsi_lows.iloc[-window]):
            return True
        return False
    
    def calculate_price_targets(self, df, indicators, timeframe_days=30):
        """Calculate price targets based on technical analysis"""
        current_price = df['Close'].iloc[-1]
        volatility = df['Close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
        
        # Support and resistance levels
        recent_high = df['High'].rolling(20).max().iloc[-1]
        recent_low = df['Low'].rolling(20).min().iloc[-1]
        
        # Calculate targets
        targets = {
            'current_price': current_price,
            'support_1': max(indicators['bb_lower'].iloc[-1], recent_low),
            'support_2': current_price * (1 - volatility * np.sqrt(timeframe_days/252)),
            'resistance_1': min(indicators['bb_upper'].iloc[-1], recent_high),
            'resistance_2': current_price * (1 + volatility * np.sqrt(timeframe_days/252)),
            'target_30d': current_price * (1 + self._estimate_return(df, indicators, 30)),
            'target_90d': current_price * (1 + self._estimate_return(df, indicators, 90)),
            'stop_loss': current_price * 0.95  # 5% stop loss
        }
        
        return targets
    
    def _estimate_return(self, df, indicators, days):
        """Estimate expected return based on technical indicators"""
        # Base return on historical performance
        historical_return = df['Close'].pct_change(days).mean()
        
        # Adjust based on current momentum
        rsi = indicators['rsi'].iloc[-1]
        momentum_adjustment = 0
        
        if 30 < rsi < 50:  # Oversold to neutral
            momentum_adjustment = 0.02
        elif 50 < rsi < 70:  # Bullish momentum
            momentum_adjustment = 0.01
        elif rsi > 70:  # Overbought
            momentum_adjustment = -0.01
        
        # Trend adjustment
        if df['Close'].iloc[-1] > indicators['sma_200'].iloc[-1]:
            momentum_adjustment += 0.01
        
        estimated_return = historical_return + momentum_adjustment
        return np.clip(estimated_return * (days/30), -0.3, 0.5)  # Cap returns at -30% to +50%
    
    def analyze_fundamentals(self, info):
        """Analyze fundamental metrics"""
        fundamentals = {
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'price_to_book': info.get('priceToBook', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'profit_margin': info.get('profitMargins', 0),
            'beta': info.get('beta', 1),
            'dividend_yield': info.get('dividendYield', 0)
        }
        
        # Calculate fundamental score
        score = 50  # Base score
        
        # P/E ratio scoring
        if 0 < fundamentals['pe_ratio'] < 15:
            score += 10
        elif 15 <= fundamentals['pe_ratio'] < 25:
            score += 5
        elif fundamentals['pe_ratio'] > 40:
            score -= 10
            
        # Growth scoring
        if fundamentals['revenue_growth'] > 0.15:
            score += 10
        elif fundamentals['revenue_growth'] > 0.05:
            score += 5
            
        # Profitability
        if fundamentals['profit_margin'] > 0.20:
            score += 10
        elif fundamentals['profit_margin'] > 0.10:
            score += 5
            
        # Debt levels
        if fundamentals['debt_to_equity'] < 0.5:
            score += 5
        elif fundamentals['debt_to_equity'] > 2:
            score -= 10
            
        fundamentals['fundamental_score'] = min(100, max(0, score))
        return fundamentals
    
    def calculate_conviction_score(self, signals, fundamentals):
        """Calculate overall conviction score for the stock"""
        # Weight technical and fundamental scores
        technical_weight = 0.6
        fundamental_weight = 0.4
        
        technical_score = signals['momentum_score']
        fundamental_score = fundamentals.get('fundamental_score', 50)
        
        conviction_score = (technical_score * technical_weight + 
                           fundamental_score * fundamental_weight)
        
        # Adjust for special conditions
        if signals.get('golden_cross'):
            conviction_score += 5
        if signals.get('rsi_bullish_divergence'):
            conviction_score += 5
        if signals.get('macd_cross_up'):
            conviction_score += 3
            
        return min(100, conviction_score)
    
    def generate_recommendation(self, conviction_score, signals, targets):
        """Generate buy/sell/hold recommendation"""
        if conviction_score >= 75:
            recommendation = "STRONG BUY"
            action = "Accumulate on any weakness"
        elif conviction_score >= 65:
            recommendation = "BUY"
            action = "Build position gradually"
        elif conviction_score >= 50:
            recommendation = "HOLD"
            action = "Monitor for better entry"
        elif conviction_score >= 40:
            recommendation = "REDUCE"
            action = "Take partial profits"
        else:
            recommendation = "SELL"
            action = "Exit position"
            
        # Risk assessment
        risk_level = "Low"
        if signals['rsi_value'] > 70:
            risk_level = "High - Overbought"
        elif signals['rsi_value'] < 30:
            risk_level = "Medium - Oversold bounce expected"
        elif targets['current_price'] > targets['resistance_1'] * 0.98:
            risk_level = "Medium - Near resistance"
            
        return {
            'recommendation': recommendation,
            'action': action,
            'risk_level': risk_level,
            'conviction_score': conviction_score
        }
    
    def scan_all_stocks(self):
        """Scan all stocks in the universe and generate recommendations"""
        results = []
        
        print("Starting comprehensive US stock market analysis...")
        print(f"Analyzing {len(self.stock_universe)} major US stocks\n")
        
        for ticker in self.stock_universe:
            print(f"Analyzing {ticker}...", end=' ')
            
            # Fetch data
            stock_data = self.fetch_stock_data(ticker)
            if not stock_data or stock_data['data'].empty:
                print("No data available")
                continue
                
            df = stock_data['data']
            info = stock_data['info']
            
            # Calculate indicators
            indicators = self.calculate_technical_indicators(df)
            signals = self.calculate_signals(df, indicators)
            targets = self.calculate_price_targets(df, indicators)
            fundamentals = self.analyze_fundamentals(info)
            
            # Calculate conviction score
            conviction_score = self.calculate_conviction_score(signals, fundamentals)
            
            # Generate recommendation
            recommendation = self.generate_recommendation(conviction_score, signals, targets)
            
            # Compile results
            result = {
                'ticker': ticker,
                'name': stock_data['name'],
                'sector': info.get('sector', 'Unknown'),
                'current_price': targets['current_price'],
                'market_cap_b': fundamentals['market_cap'] / 1e9 if fundamentals['market_cap'] else 0,
                'conviction_score': conviction_score,
                'recommendation': recommendation['recommendation'],
                'action': recommendation['action'],
                'risk_level': recommendation['risk_level'],
                'rsi': signals['rsi_value'],
                'momentum_score': signals['momentum_score'],
                'fundamental_score': fundamentals['fundamental_score'],
                'target_30d': targets['target_30d'],
                'target_90d': targets['target_90d'],
                'support': targets['support_1'],
                'resistance': targets['resistance_1'],
                'stop_loss': targets['stop_loss'],
                'volume_surge': signals['volume_surge'],
                'macd_bullish': signals['macd_bullish'],
                'above_200_sma': signals['above_sma_200']
            }
            
            results.append(result)
            print(f"Score: {conviction_score:.1f} - {recommendation['recommendation']}")
            
        return pd.DataFrame(results)

def main():
    """Run the stock analysis"""
    analyzer = StockAnalyzer()
    
    # Perform comprehensive analysis
    results_df = analyzer.scan_all_stocks()
    
    # Sort by conviction score
    results_df = results_df.sort_values('conviction_score', ascending=False)
    
    # Save full results
    results_df.to_csv('us_stock_analysis_2025.csv', index=False)
    print(f"\nFull analysis saved to 'us_stock_analysis_2025.csv'")
    
    # Display top recommendations
    print("\n" + "="*80)
    print("TOP HIGH-CONVICTION STOCKS (Score >= 70)")
    print("="*80)
    
    high_conviction = results_df[results_df['conviction_score'] >= 70]
    
    if not high_conviction.empty:
        for _, stock in high_conviction.iterrows():
            print(f"\n{stock['ticker']} - {stock['name']}")
            print(f"Sector: {stock['sector']}")
            print(f"Conviction Score: {stock['conviction_score']:.1f}")
            print(f"Recommendation: {stock['recommendation']}")
            print(f"Current Price: ${stock['current_price']:.2f}")
            print(f"30-Day Target: ${stock['target_30d']:.2f} ({((stock['target_30d']/stock['current_price']-1)*100):.1f}%)")
            print(f"90-Day Target: ${stock['target_90d']:.2f} ({((stock['target_90d']/stock['current_price']-1)*100):.1f}%)")
            print(f"Risk Level: {stock['risk_level']}")
            print(f"Action: {stock['action']}")
    else:
        print("No stocks currently meet high conviction criteria (Score >= 70)")
    
    # Sector analysis
    print("\n" + "="*80)
    print("SECTOR PERFORMANCE ANALYSIS")
    print("="*80)
    
    sector_analysis = results_df.groupby('sector').agg({
        'conviction_score': 'mean',
        'ticker': 'count'
    }).round(1)
    sector_analysis.columns = ['Avg Conviction Score', 'Stock Count']
    sector_analysis = sector_analysis.sort_values('Avg Conviction Score', ascending=False)
    print(sector_analysis)
    
    # Market overview
    print("\n" + "="*80)
    print("MARKET OVERVIEW")
    print("="*80)
    
    bullish_stocks = len(results_df[results_df['recommendation'].isin(['STRONG BUY', 'BUY'])])
    bearish_stocks = len(results_df[results_df['recommendation'].isin(['SELL', 'REDUCE'])])
    neutral_stocks = len(results_df[results_df['recommendation'] == 'HOLD'])
    
    print(f"Bullish Stocks: {bullish_stocks} ({bullish_stocks/len(results_df)*100:.1f}%)")
    print(f"Neutral Stocks: {neutral_stocks} ({neutral_stocks/len(results_df)*100:.1f}%)")
    print(f"Bearish Stocks: {bearish_stocks} ({bearish_stocks/len(results_df)*100:.1f}%)")
    
    # Technical signals summary
    print("\n" + "="*80)
    print("TECHNICAL SIGNALS SUMMARY")
    print("="*80)
    
    above_200_sma = len(results_df[results_df['above_200_sma']])
    macd_bullish = len(results_df[results_df['macd_bullish']])
    volume_surges = len(results_df[results_df['volume_surge']])
    
    print(f"Stocks above 200-day SMA: {above_200_sma} ({above_200_sma/len(results_df)*100:.1f}%)")
    print(f"Stocks with bullish MACD: {macd_bullish} ({macd_bullish/len(results_df)*100:.1f}%)")
    print(f"Stocks with volume surge: {volume_surges} ({volume_surges/len(results_df)*100:.1f}%)")
    
    return results_df

if __name__ == "__main__":
    main()
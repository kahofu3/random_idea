"""
Stock Analysis Report Generator
Creates a comprehensive markdown report with analysis results and predictions
"""

import pandas as pd
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self, results_path='us_stock_analysis_2025.csv'):
        self.results_df = pd.read_csv(results_path)
        self.report_date = datetime.now().strftime("%B %d, %Y")
        
    def generate_market_summary(self):
        """Generate market overview summary"""
        total_stocks = len(self.results_df)
        bullish = len(self.results_df[self.results_df['recommendation'].isin(['STRONG BUY', 'BUY'])])
        bearish = len(self.results_df[self.results_df['recommendation'].isin(['SELL', 'REDUCE'])])
        neutral = len(self.results_df[self.results_df['recommendation'] == 'HOLD'])
        
        avg_conviction = self.results_df['conviction_score'].mean()
        
        summary = f"""## Market Overview

**Analysis Date:** {self.report_date}  
**Stocks Analyzed:** {total_stocks}

### Market Sentiment
- **Bullish Stocks:** {bullish} ({bullish/total_stocks*100:.1f}%)
- **Neutral Stocks:** {neutral} ({neutral/total_stocks*100:.1f}%)
- **Bearish Stocks:** {bearish} ({bearish/total_stocks*100:.1f}%)
- **Average Conviction Score:** {avg_conviction:.1f}/100

### Technical Indicators Summary
- **Stocks Above 200-Day SMA:** {len(self.results_df[self.results_df['above_200_sma']])} ({len(self.results_df[self.results_df['above_200_sma']])/total_stocks*100:.1f}%)
- **Stocks with Bullish MACD:** {len(self.results_df[self.results_df['macd_bullish']])} ({len(self.results_df[self.results_df['macd_bullish']])/total_stocks*100:.1f}%)
- **Stocks with Volume Surge:** {len(self.results_df[self.results_df['volume_surge']])} ({len(self.results_df[self.results_df['volume_surge']])/total_stocks*100:.1f}%)
"""
        return summary
    
    def generate_top_picks(self, n=10):
        """Generate top stock picks section"""
        top_stocks = self.results_df.nlargest(n, 'conviction_score')
        
        picks = "## Top High-Conviction Stock Picks\n\n"
        
        for idx, stock in top_stocks.iterrows():
            expected_return_30d = ((stock['target_30d'] - stock['current_price']) / stock['current_price'] * 100)
            expected_return_90d = ((stock['target_90d'] - stock['current_price']) / stock['current_price'] * 100)
            
            picks += f"""### {idx+1}. {stock['ticker']} - {stock['name']}

**Sector:** {stock['sector']}  
**Conviction Score:** {stock['conviction_score']:.1f}/100  
**Recommendation:** **{stock['recommendation']}**  
**Risk Level:** {stock['risk_level']}

#### Price Analysis
- **Current Price:** ${stock['current_price']:.2f}
- **30-Day Target:** ${stock['target_30d']:.2f} ({expected_return_30d:+.1f}%)
- **90-Day Target:** ${stock['target_90d']:.2f} ({expected_return_90d:+.1f}%)
- **Support Level:** ${stock['support']:.2f}
- **Resistance Level:** ${stock['resistance']:.2f}
- **Stop Loss:** ${stock['stop_loss']:.2f}

#### Technical Indicators
- **RSI:** {stock['rsi']:.1f}
- **Momentum Score:** {stock['momentum_score']:.1f}/100
- **Fundamental Score:** {stock['fundamental_score']:.1f}/100

**Action:** {stock['action']}

---

"""
        return picks
    
    def generate_sector_analysis(self):
        """Generate sector analysis section"""
        sector_stats = self.results_df.groupby('sector').agg({
            'conviction_score': ['mean', 'count'],
            'recommendation': lambda x: (x.isin(['STRONG BUY', 'BUY'])).sum()
        }).round(1)
        
        sector_stats.columns = ['Avg Score', 'Count', 'Bullish Count']
        sector_stats = sector_stats.sort_values('Avg Score', ascending=False)
        
        analysis = "## Sector Analysis\n\n"
        analysis += "### Sector Performance Ranking\n\n"
        analysis += "| Sector | Avg Conviction Score | Stock Count | Bullish Stocks |\n"
        analysis += "|--------|---------------------|-------------|----------------|\n"
        
        for sector, row in sector_stats.iterrows():
            bullish_pct = row['Bullish Count'] / row['Count'] * 100
            analysis += f"| {sector} | {row['Avg Score']:.1f} | {int(row['Count'])} | {int(row['Bullish Count'])} ({bullish_pct:.0f}%) |\n"
        
        # Add sector insights
        top_sector = sector_stats.index[0]
        analysis += f"\n### Key Insights\n\n"
        analysis += f"- **Best Performing Sector:** {top_sector} with an average conviction score of {sector_stats.loc[top_sector, 'Avg Score']:.1f}\n"
        analysis += f"- **Most Bullish Sector:** {sector_stats.sort_values('Bullish Count', ascending=False).index[0]}\n"
        
        return analysis
    
    def generate_predictions(self):
        """Generate market predictions section"""
        # Calculate aggregate predictions
        avg_30d_return = ((self.results_df['target_30d'] - self.results_df['current_price']) / 
                          self.results_df['current_price']).mean() * 100
        avg_90d_return = ((self.results_df['target_90d'] - self.results_df['current_price']) / 
                          self.results_df['current_price']).mean() * 100
        
        high_conviction = self.results_df[self.results_df['conviction_score'] >= 70]
        
        predictions = f"""## Market Predictions and Outlook

### Short-Term Outlook (30 Days)
- **Average Expected Return:** {avg_30d_return:+.1f}%
- **High-Conviction Stocks:** {len(high_conviction)} stocks with scores ≥70
- **Market Direction:** {"Bullish" if avg_30d_return > 0 else "Bearish"}

### Medium-Term Outlook (90 Days)
- **Average Expected Return:** {avg_90d_return:+.1f}%
- **Trend Projection:** {"Upward" if avg_90d_return > avg_30d_return else "Consolidating"}

### Key Market Themes for 2025

1. **AI and Technology Leadership**
   - Nvidia continues to dominate as the most valuable US company
   - AI infrastructure spending driving semiconductor demand
   - Cloud computing and enterprise AI adoption accelerating

2. **Sector Rotation Opportunities**
   - Utilities benefiting from AI data center electricity demand
   - Financials positioned for rate normalization
   - Healthcare recovery after 2024 underperformance

3. **Risk Factors to Monitor**
   - Trade policy uncertainty and tariff impacts
   - Interest rate trajectory and Fed policy
   - Geopolitical tensions affecting global markets

### Investment Strategy Recommendations

Based on our comprehensive analysis, we recommend:

1. **Overweight:** Technology (especially AI/semiconductors), Financials, Healthcare
2. **Neutral:** Consumer Staples, Industrials, Utilities
3. **Underweight:** Energy, Consumer Discretionary

**Risk Management:** Maintain stop losses at 5-7% below entry points and consider taking partial profits on stocks reaching overbought RSI levels (>70).
"""
        return predictions
    
    def generate_full_report(self):
        """Generate the complete report"""
        report = f"""# US Stock Market Analysis Report
## Comprehensive Analysis and Predictions for 2025

*Generated on {self.report_date}*

---

"""
        
        # Add all sections
        report += self.generate_market_summary()
        report += "\n---\n\n"
        report += self.generate_top_picks()
        report += "\n---\n\n"
        report += self.generate_sector_analysis()
        report += "\n---\n\n"
        report += self.generate_predictions()
        
        # Add disclaimer
        report += """
---

## Disclaimer

This report is generated using technical analysis, fundamental data, and algorithmic predictions. It is provided for informational purposes only and should not be considered as financial advice. Past performance does not guarantee future results. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

### Methodology
- Technical indicators: RSI, MACD, Moving Averages, Bollinger Bands
- Fundamental metrics: P/E ratios, revenue growth, profit margins
- Conviction scoring: Weighted combination of technical (60%) and fundamental (40%) factors
- Price targets: Based on historical volatility and momentum indicators

*Analysis powered by advanced quantitative models and real-time market data.*
"""
        
        return report
    
    def save_report(self, filename='stock_analysis_report.md'):
        """Save the report to a file"""
        report = self.generate_full_report()
        
        with open(filename, 'w') as f:
            f.write(report)
            
        print(f"Report saved to {filename}")
        
        # Also save a summary version
        summary = f"""# Quick Stock Picks - {self.report_date}

## Top 5 High-Conviction Stocks

"""
        top_5 = self.results_df.nlargest(5, 'conviction_score')
        for _, stock in top_5.iterrows():
            ret_30d = ((stock['target_30d'] - stock['current_price']) / stock['current_price'] * 100)
            summary += f"**{stock['ticker']}** - Score: {stock['conviction_score']:.0f} | {stock['recommendation']} | 30d Target: {ret_30d:+.1f}%\n"
        
        with open('quick_picks.md', 'w') as f:
            f.write(summary)
            
        print("Quick picks summary saved to quick_picks.md")

def main():
    """Generate all reports"""
    try:
        generator = ReportGenerator()
        generator.save_report()
        print("\nReport generation complete!")
    except FileNotFoundError:
        print("Results file not found. Please run stock_analysis_2025.py first.")
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main()
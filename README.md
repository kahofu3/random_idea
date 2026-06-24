# US Stock Market Analysis & Prediction System
## July 2025 Edition

A comprehensive Python-based system for analyzing US stocks using technical indicators, fundamental data, and AI-driven insights to identify high-conviction investment opportunities.

## 🚀 Features

- **Comprehensive Stock Scanning**: Analyzes 40+ major US stocks across all sectors
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands, and more
- **Fundamental Analysis**: P/E ratios, revenue growth, profit margins, debt levels
- **Conviction Scoring**: Proprietary scoring system (0-100) combining technical and fundamental factors
- **Price Predictions**: 30-day and 90-day price targets based on volatility and momentum
- **Risk Assessment**: Automated risk level classification for each stock
- **Sector Analysis**: Comparative sector performance and rotation opportunities
- **Visual Dashboard**: Interactive charts and visualizations
- **Automated Reports**: Markdown reports with actionable insights

## 📋 Requirements

- Python 3.8+
- Internet connection for real-time data fetching

## 🛠️ Installation

1. Clone or download this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## 🏃 Quick Start

### 1. Run the Main Analysis

```bash
python stock_analysis_2025.py
```

This will:
- Scan all stocks in the universe
- Calculate technical indicators
- Generate conviction scores
- Save results to `us_stock_analysis_2025.csv`
- Display top picks in the console

### 2. Generate Visualizations

```bash
python stock_visualization.py
```

This creates:
- `conviction_scores.png` - Bar chart of top stocks
- `sector_analysis.png` - Sector performance comparison
- `risk_return_analysis.png` - Risk vs return scatter plot
- `stock_analysis_dashboard.html` - Interactive dashboard
- Individual stock charts for top 5 picks

### 3. Generate Report

```bash
python generate_report.py
```

This creates:
- `stock_analysis_report.md` - Comprehensive analysis report
- `quick_picks.md` - Quick summary of top 5 stocks

## 📊 Understanding the Analysis

### Conviction Score (0-100)
- **75-100**: STRONG BUY - High confidence, accumulate positions
- **65-74**: BUY - Good opportunity, build position gradually
- **50-64**: HOLD - Neutral, wait for better entry
- **40-49**: REDUCE - Take partial profits
- **0-39**: SELL - Exit position

### Technical Indicators Used
- **RSI (Relative Strength Index)**: Momentum indicator (30=oversold, 70=overbought)
- **MACD**: Trend following indicator
- **Moving Averages**: 20, 50, 200-day SMAs for trend identification
- **Bollinger Bands**: Volatility and support/resistance levels
- **Volume Analysis**: Unusual volume detection

### Risk Levels
- **Low**: Normal market conditions
- **Medium**: Near support/resistance or oversold
- **High**: Overbought conditions or high volatility

## 📈 Current Market Insights (July 2025)

Based on recent analysis:

1. **Technology Sector**: Led by Nvidia (now the most valuable US company), AI and semiconductor stocks show strong momentum
2. **Sector Rotation**: Utilities and Financials showing unexpected strength
3. **Market Risks**: Trade policy uncertainty and tariff concerns creating volatility
4. **Key Themes**: AI infrastructure buildout, rate normalization, healthcare recovery

## 🎯 Top Sectors to Watch

1. **Technology** - AI/semiconductor leadership
2. **Financials** - Rate normalization benefits
3. **Healthcare** - Recovery from 2024 underperformance
4. **Utilities** - AI data center electricity demand

## ⚠️ Disclaimer

This system is for educational and informational purposes only. It should not be considered financial advice. Always:
- Conduct your own research
- Consult with qualified financial advisors
- Consider your risk tolerance
- Never invest more than you can afford to lose

## 🔧 Customization

You can modify the stock universe in `stock_analysis_2025.py`:

```python
self.stock_universe = {
    'AAPL': 'Apple Inc',
    'MSFT': 'Microsoft Corp',
    # Add your stocks here
}
```

## 📝 Output Files

- `us_stock_analysis_2025.csv` - Raw analysis data
- `stock_analysis_report.md` - Detailed markdown report
- `quick_picks.md` - Summary of top picks
- `*.png` - Various charts and visualizations
- `*.html` - Interactive dashboards

## 🐛 Troubleshooting

1. **No data for ticker**: Stock may be delisted or ticker incorrect
2. **Connection errors**: Check internet connection
3. **Missing indicators**: Some stocks may have insufficient historical data

## 📚 Further Reading

- [Technical Analysis Guide](https://www.investopedia.com/technical-analysis-4689657)
- [Understanding RSI](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Explained](https://www.investopedia.com/terms/m/macd.asp)

---

*Last Updated: July 2025*
*Version: 1.0*
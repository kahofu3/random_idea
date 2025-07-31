"""
Stock Analysis Visualization Module
Creates charts and visualizations for the analysis results
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environment
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta

class StockVisualizer:
    def __init__(self, results_df=None):
        self.results_df = results_df
        self.style_plots()
        
    def style_plots(self):
        """Set up plot styling"""
        # Use a compatible style
        plt.style.use('ggplot')
        sns.set_palette("husl")
        
    def load_results(self, csv_path='us_stock_analysis_2025.csv'):
        """Load results from CSV"""
        self.results_df = pd.read_csv(csv_path)
        return self.results_df
    
    def plot_conviction_scores(self, top_n=20):
        """Plot top stocks by conviction score"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        top_stocks = self.results_df.nlargest(top_n, 'conviction_score')
        
        colors = ['darkgreen' if score >= 70 else 'green' if score >= 60 
                  else 'orange' if score >= 50 else 'red' 
                  for score in top_stocks['conviction_score']]
        
        bars = ax.barh(top_stocks['ticker'], top_stocks['conviction_score'], color=colors)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}', ha='left', va='center')
        
        ax.set_xlabel('Conviction Score')
        ax.set_title(f'Top {top_n} Stocks by Conviction Score', fontsize=16)
        ax.set_xlim(0, 100)
        
        # Add threshold lines
        ax.axvline(x=70, color='darkgreen', linestyle='--', alpha=0.5, label='Strong Buy (70+)')
        ax.axvline(x=50, color='orange', linestyle='--', alpha=0.5, label='Hold (50+)')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig('conviction_scores.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_sector_analysis(self):
        """Plot sector performance analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Average conviction score by sector
        sector_avg = self.results_df.groupby('sector')['conviction_score'].mean().sort_values(ascending=False)
        sector_avg.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('Average Conviction Score by Sector')
        ax1.set_xlabel('Sector')
        ax1.set_ylabel('Average Conviction Score')
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5)
        
        # Stock count by recommendation
        rec_counts = self.results_df.groupby('recommendation').size()
        colors = {'STRONG BUY': 'darkgreen', 'BUY': 'green', 
                  'HOLD': 'yellow', 'REDUCE': 'orange', 'SELL': 'red'}
        rec_colors = [colors.get(x, 'gray') for x in rec_counts.index]
        
        rec_counts.plot(kind='pie', ax=ax2, colors=rec_colors, autopct='%1.1f%%')
        ax2.set_title('Distribution of Recommendations')
        ax2.set_ylabel('')
        
        plt.tight_layout()
        plt.savefig('sector_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_risk_return_scatter(self):
        """Plot risk-return scatter plot"""
        fig = plt.figure(figsize=(12, 8))
        
        # Calculate expected return
        self.results_df['expected_return_30d'] = (
            (self.results_df['target_30d'] - self.results_df['current_price']) / 
            self.results_df['current_price'] * 100
        )
        
        # Use RSI as a proxy for risk (higher RSI = higher risk)
        self.results_df['risk_score'] = self.results_df['rsi'].apply(
            lambda x: abs(x - 50) / 50 * 100  # Distance from neutral
        )
        
        # Create scatter plot
        scatter = plt.scatter(self.results_df['risk_score'], 
                            self.results_df['expected_return_30d'],
                            s=self.results_df['market_cap_b'] * 2,  # Size by market cap
                            c=self.results_df['conviction_score'],
                            cmap='RdYlGn', alpha=0.6)
        
        # Add labels for top conviction stocks
        top_stocks = self.results_df.nlargest(10, 'conviction_score')
        for _, stock in top_stocks.iterrows():
            plt.annotate(stock['ticker'], 
                        (stock['risk_score'], stock['expected_return_30d']),
                        fontsize=8)
        
        plt.colorbar(scatter, label='Conviction Score')
        plt.xlabel('Risk Score (based on RSI)')
        plt.ylabel('Expected 30-Day Return (%)')
        plt.title('Risk-Return Analysis with Conviction Scores')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.axvline(x=50, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('risk_return_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_interactive_dashboard(self):
        """Create an interactive Plotly dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Conviction Scores', 'Sector Distribution', 
                          'Technical Indicators', 'Price Targets'),
            specs=[[{'type': 'bar'}, {'type': 'pie'}],
                   [{'type': 'scatter'}, {'type': 'bar'}]]
        )
        
        # 1. Conviction scores bar chart
        top_20 = self.results_df.nlargest(20, 'conviction_score')
        fig.add_trace(
            go.Bar(x=top_20['ticker'], y=top_20['conviction_score'],
                   name='Conviction Score',
                   marker_color=top_20['conviction_score'],
                   marker_colorscale='RdYlGn'),
            row=1, col=1
        )
        
        # 2. Sector pie chart
        sector_counts = self.results_df['sector'].value_counts()
        fig.add_trace(
            go.Pie(labels=sector_counts.index, values=sector_counts.values,
                   name='Sector Distribution'),
            row=1, col=2
        )
        
        # 3. RSI vs Momentum scatter
        fig.add_trace(
            go.Scatter(x=self.results_df['rsi'], 
                      y=self.results_df['momentum_score'],
                      mode='markers+text',
                      text=self.results_df['ticker'],
                      textposition='top center',
                      marker=dict(
                          size=self.results_df['conviction_score'] / 5,
                          color=self.results_df['conviction_score'],
                          colorscale='RdYlGn',
                          showscale=True
                      ),
                      name='RSI vs Momentum'),
            row=2, col=1
        )
        
        # 4. Price targets
        top_10 = self.results_df.nlargest(10, 'conviction_score')
        fig.add_trace(
            go.Bar(x=top_10['ticker'], 
                   y=(top_10['target_30d'] - top_10['current_price']) / top_10['current_price'] * 100,
                   name='30-Day Return %'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Stock Analysis Dashboard - July 2025",
            showlegend=False,
            height=800
        )
        
        fig.write_html('stock_analysis_dashboard.html')
        return fig
        
    def plot_stock_chart(self, ticker, period='6mo'):
        """Plot individual stock chart with technical indicators"""
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.5, 0.25, 0.25],
                           subplot_titles=(f'{ticker} Price Chart', 'RSI', 'Volume'))
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'],
                                    name='Price'),
                     row=1, col=1)
        
        # Add moving averages
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'],
                                mode='lines', name='SMA20',
                                line=dict(color='orange')),
                     row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'],
                                mode='lines', name='SMA50',
                                line=dict(color='blue')),
                     row=1, col=1)
        
        # RSI
        # Simple RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(go.Scatter(x=df.index, y=rsi,
                                mode='lines', name='RSI',
                                line=dict(color='purple')),
                     row=2, col=1)
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Volume
        colors = ['red' if row['Close'] < row['Open'] else 'green' 
                  for index, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'],
                            name='Volume',
                            marker_color=colors),
                     row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} Technical Analysis',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        fig.write_html(f'{ticker}_chart.html')
        return fig

def main():
    """Create all visualizations"""
    visualizer = StockVisualizer()
    
    # Load results
    try:
        visualizer.load_results()
        print("Creating visualizations...")
        
        # Create all plots
        visualizer.plot_conviction_scores()
        visualizer.plot_sector_analysis()
        visualizer.plot_risk_return_scatter()
        
        # Create interactive dashboard
        dashboard = visualizer.create_interactive_dashboard()
        print("Interactive dashboard saved as 'stock_analysis_dashboard.html'")
        
        # Create individual stock charts for top 5 stocks
        top_5 = visualizer.results_df.nlargest(5, 'conviction_score')
        for _, stock in top_5.iterrows():
            visualizer.plot_stock_chart(stock['ticker'])
            print(f"Created chart for {stock['ticker']}")
            
        print("\nAll visualizations created successfully!")
        
    except FileNotFoundError:
        print("Results file not found. Please run stock_analysis_2025.py first.")
    except Exception as e:
        print(f"Error creating visualizations: {e}")

if __name__ == "__main__":
    main()
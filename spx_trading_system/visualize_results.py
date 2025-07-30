"""
Visualize Backtest Results
"""
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load results
with open('optimized_backtest_results.json', 'r') as f:
    results = json.load(f)

# Create DataFrame from results
df = pd.DataFrame(results['summary'])

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Returns vs Win Rate
ax = axes[0, 0]
scatter = ax.scatter(df['win_rate'] * 100, df['annual_return'] * 100, 
                    s=df['total_trades'] * 3, alpha=0.7, c=df['sharpe_ratio'], 
                    cmap='viridis')
ax.set_xlabel('Win Rate (%)')
ax.set_ylabel('Annual Return (%)')
ax.set_title('Returns vs Win Rate (size = # trades, color = Sharpe)')
ax.grid(True, alpha=0.3)

# Add strategy labels
for idx, row in df.iterrows():
    ax.annotate(row['strategy_name'], 
                (row['win_rate'] * 100, row['annual_return'] * 100),
                fontsize=8, ha='center')

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Sharpe Ratio')

# 2. Risk-Return Profile
ax = axes[0, 1]
ax.scatter(df['max_drawdown'] * 100, df['annual_return'] * 100, 
          s=100, alpha=0.7)
ax.set_xlabel('Max Drawdown (%)')
ax.set_ylabel('Annual Return (%)')
ax.set_title('Risk-Return Profile')
ax.grid(True, alpha=0.3)

# Add labels
for idx, row in df.iterrows():
    ax.annotate(row['strategy_name'], 
                (row['max_drawdown'] * 100, row['annual_return'] * 100),
                fontsize=8, ha='center')

# 3. Strategy Performance Metrics
ax = axes[1, 0]
metrics = ['annual_return', 'win_rate', 'sharpe_ratio']
strategy_names = df['strategy_name'].tolist()
x = np.arange(len(strategy_names))
width = 0.25

for i, metric in enumerate(metrics):
    values = df[metric].tolist()
    if metric == 'annual_return':
        values = [v * 100 for v in values]  # Convert to percentage
    elif metric == 'win_rate':
        values = [v * 100 for v in values]  # Convert to percentage
    
    ax.bar(x + i * width, values, width, label=metric.replace('_', ' ').title())

ax.set_xlabel('Strategy')
ax.set_ylabel('Value')
ax.set_title('Strategy Performance Comparison')
ax.set_xticks(x + width)
ax.set_xticklabels(strategy_names, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# 4. Composite Score Ranking
ax = axes[1, 1]
sorted_df = df.sort_values('composite_score', ascending=True)
y_pos = np.arange(len(sorted_df))
ax.barh(y_pos, sorted_df['composite_score'], alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(sorted_df['strategy_name'])
ax.set_xlabel('Composite Score')
ax.set_title('Strategy Ranking by Composite Score')
ax.grid(True, alpha=0.3, axis='x')

# Add values on bars
for i, v in enumerate(sorted_df['composite_score']):
    ax.text(v + 0.01, i, f'{v:.3f}', va='center')

plt.tight_layout()
plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary table
print("\nSTRATEGY PERFORMANCE SUMMARY TABLE")
print("="*100)
print(f"{'Strategy':<20} {'Return':<10} {'Win Rate':<10} {'Sharpe':<10} {'Max DD':<10} {'Trades':<10} {'Score':<10}")
print("="*100)

for _, row in df.sort_values('composite_score', ascending=False).iterrows():
    print(f"{row['strategy_name']:<20} "
          f"{row['annual_return']*100:>8.1f}% "
          f"{row['win_rate']*100:>8.1f}% "
          f"{row['sharpe_ratio']:>9.2f} "
          f"{row['max_drawdown']*100:>8.1f}% "
          f"{row['total_trades']:>9} "
          f"{row['composite_score']:>9.3f}")

# Best strategy details
print("\n" + "="*100)
print("BEST STRATEGY DETAILS:")
print("="*100)
best = results['best_overall']
print(f"Strategy: {best['strategy_name']}")
print(f"Timeframe: {best['timeframe']}")
print(f"Annual Return: {best['annual_return']*100:.2f}%")
print(f"Win Rate: {best['win_rate']*100:.2f}%")
print(f"Sharpe Ratio: {best['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {best['max_drawdown']*100:.2f}%")
print(f"Total P&L: ${best['total_pnl']:,.2f}")
print(f"Expected Value per Trade: ${best['expected_value']:.2f}")
print(f"Total Trades: {best['total_trades']}")
print(f"Composite Score: {best['composite_score']:.3f}")
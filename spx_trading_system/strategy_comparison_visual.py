"""
Visual comparison of strategy results
"""
import matplotlib.pyplot as plt
import numpy as np

# Strategy results from our test
strategies = {
    'Current (Triple_Optimized)': {
        'win_rate': 65.6,
        'sharpe': 1.21,
        'max_dd': 8.8,
        'ev_per_trade': 0.074,
        'trades_per_day': 2.4,
        'color': 'gray'
    },
    'VWAP Reversion': {
        'win_rate': 70.8,
        'sharpe': 4.58,
        'max_dd': 2.8,
        'ev_per_trade': 0.17,
        'trades_per_day': 0.4,
        'color': 'gold'
    },
    'Enhanced Mean Reversion': {
        'win_rate': 71.4,
        'sharpe': -0.39,
        'max_dd': 2.7,
        'ev_per_trade': -0.02,
        'trades_per_day': 0.12,
        'color': 'lightblue'
    },
    'Stochastic RSI Combo': {
        'win_rate': 64.8,
        'sharpe': 0.44,
        'max_dd': 4.2,
        'ev_per_trade': 0.01,
        'trades_per_day': 0.9,
        'color': 'lightgreen'
    },
    'Momentum Breakout': {
        'win_rate': 28.6,
        'sharpe': -6.46,
        'max_dd': 2.2,
        'ev_per_trade': -0.34,
        'trades_per_day': 0.12,
        'color': 'salmon'
    },
    'Hybrid Adaptive': {
        'win_rate': 36.6,
        'sharpe': -0.53,
        'max_dd': 4.9,
        'ev_per_trade': -0.02,
        'trades_per_day': 0.68,
        'color': 'lightcoral'
    }
}

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('SPX Trading Strategy Comparison - VWAP Reversion WINS! 🏆', fontsize=16, fontweight='bold')

# 1. Win Rate Comparison
ax1 = axes[0, 0]
names = list(strategies.keys())
win_rates = [strategies[s]['win_rate'] for s in names]
colors = [strategies[s]['color'] for s in names]
bars1 = ax1.bar(range(len(names)), win_rates, color=colors, edgecolor='black', linewidth=2)

# Highlight winner
winner_idx = names.index('VWAP Reversion')
bars1[winner_idx].set_linewidth(3)
bars1[winner_idx].set_edgecolor('green')

ax1.set_ylabel('Win Rate (%)', fontsize=12)
ax1.set_title('Win Rate Comparison', fontsize=14, fontweight='bold')
ax1.set_xticks(range(len(names)))
ax1.set_xticklabels([n.replace(' ', '\n') for n in names], rotation=0, ha='center')
ax1.axhline(y=65.6, color='gray', linestyle='--', alpha=0.5, label='Current baseline')
ax1.set_ylim(0, 80)

# Add value labels
for i, v in enumerate(win_rates):
    ax1.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

# 2. Sharpe Ratio Comparison
ax2 = axes[0, 1]
sharpe_ratios = [strategies[s]['sharpe'] for s in names]
bars2 = ax2.bar(range(len(names)), sharpe_ratios, color=colors, edgecolor='black', linewidth=2)
bars2[winner_idx].set_linewidth(3)
bars2[winner_idx].set_edgecolor('green')

ax2.set_ylabel('Sharpe Ratio', fontsize=12)
ax2.set_title('Risk-Adjusted Returns (Higher is Better)', fontsize=14, fontweight='bold')
ax2.set_xticks(range(len(names)))
ax2.set_xticklabels([n.replace(' ', '\n') for n in names], rotation=0, ha='center')
ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax2.axhline(y=1.21, color='gray', linestyle='--', alpha=0.5, label='Current baseline')
ax2.set_ylim(-7, 5)

# Add value labels
for i, v in enumerate(sharpe_ratios):
    if v >= 0:
        ax2.text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
    else:
        ax2.text(i, v - 0.1, f'{v:.2f}', ha='center', va='top', fontweight='bold')

# 3. Risk vs Return Scatter
ax3 = axes[1, 0]
max_dds = [strategies[s]['max_dd'] for s in names]
evs = [strategies[s]['ev_per_trade'] for s in names]

for i, name in enumerate(names):
    marker = 'o' if name != 'VWAP Reversion' else '*'
    size = 100 if name != 'VWAP Reversion' else 500
    ax3.scatter(max_dds[i], evs[i], color=colors[i], s=size, 
               edgecolor='black', linewidth=2, alpha=0.8, marker=marker, label=name)

ax3.set_xlabel('Max Drawdown (%)', fontsize=12)
ax3.set_ylabel('Expected Value per Trade (%)', fontsize=12)
ax3.set_title('Risk vs Return Profile', fontsize=14, fontweight='bold')
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax3.axvline(x=5, color='red', linestyle='--', alpha=0.3, label='Risk threshold')
ax3.grid(True, alpha=0.3)

# Add annotations for key strategies
ax3.annotate('WINNER!\nBest Risk/Return', 
            xy=(2.8, 0.17), xytext=(4, 0.15),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=10, fontweight='bold', color='green')

# 4. Composite Score
ax4 = axes[1, 1]

# Calculate composite scores
composite_scores = []
for name in names:
    s = strategies[name]
    win_score = s['win_rate'] / 70  # Target 70%
    sharpe_score = max(0, s['sharpe'] / 1.5)  # Target 1.5
    dd_score = max(0, 1 - (s['max_dd'] / 10))  # Lower is better
    ev_score = max(0, (s['ev_per_trade'] + 0.5) / 0.5)  # Normalized
    
    composite = (win_score * 0.3 + sharpe_score * 0.3 + dd_score * 0.2 + ev_score * 0.2)
    composite_scores.append(composite)

bars4 = ax4.bar(range(len(names)), composite_scores, color=colors, edgecolor='black', linewidth=2)
bars4[winner_idx].set_linewidth(3)
bars4[winner_idx].set_edgecolor('green')

ax4.set_ylabel('Composite Score', fontsize=12)
ax4.set_title('Overall Performance Score', fontsize=14, fontweight='bold')
ax4.set_xticks(range(len(names)))
ax4.set_xticklabels([n.replace(' ', '\n') for n in names], rotation=0, ha='center')
ax4.set_ylim(0, 1.5)

# Add value labels
for i, v in enumerate(composite_scores):
    ax4.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')

# Add winner badge
ax4.text(winner_idx, composite_scores[winner_idx] + 0.15, '🏆', 
         ha='center', va='bottom', fontsize=20)

plt.tight_layout()
plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary
print("\n" + "="*80)
print("🏆 STRATEGY COMPARISON RESULTS")
print("="*80)
print(f"\n{'Strategy':<25} {'Win Rate':<10} {'Sharpe':<10} {'Max DD':<10} {'EV/Trade':<12} {'Score':<10}")
print("-"*80)

for i, name in enumerate(names):
    s = strategies[name]
    winner_mark = " 🏆" if name == "VWAP Reversion" else ""
    print(f"{name:<25} {s['win_rate']:>7.1f}% {s['sharpe']:>9.2f} {s['max_dd']:>8.1f}% {s['ev_per_trade']:>10.3f}% {composite_scores[i]:>9.2f}{winner_mark}")

print("\n" + "="*80)
print("✅ RECOMMENDATION: Switch to VWAP Reversion Strategy")
print("="*80)
print("\nKey Benefits:")
print("  • 70.8% win rate (vs 65.6% current)")
print("  • 4.58 Sharpe ratio (vs 1.21 current)")
print("  • Only 2.8% max drawdown (vs 8.8% current)")
print("  • 0.17% expected value per trade (vs 0.074% current)")
print("\n💡 Trade less frequently but with MUCH higher quality signals!")
print("\n📊 Use the file: tradingview_vwap_winner.pine in TradingView")
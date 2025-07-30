"""
Test script to verify SPX Trading System installation
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from config.config import TRADING_CONFIG
        print("✓ Config module loaded")
        
        from src.data_handler import DataHandler
        print("✓ DataHandler loaded")
        
        from src.indicators import TechnicalIndicators
        print("✓ TechnicalIndicators loaded")
        
        from src.strategy import TradingStrategy
        print("✓ TradingStrategy loaded")
        
        from src.backtest import Backtester
        print("✓ Backtester loaded")
        
        from src.visualization import ReportGenerator
        print("✓ ReportGenerator loaded")
        
        from src.optimizer import StrategyOptimizer
        print("✓ StrategyOptimizer loaded")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    try:
        from src.data_handler import DataHandler
        from src.indicators import TechnicalIndicators
        from src.strategy import TradingStrategy
        
        # Test data handler initialization
        data_handler = DataHandler()
        print("✓ DataHandler initialized")
        
        # Test indicators initialization
        indicators = TechnicalIndicators()
        print("✓ TechnicalIndicators initialized")
        
        # Test strategy initialization
        strategy = TradingStrategy()
        print("✓ TradingStrategy initialized")
        print(f"  Initial capital: ${strategy.initial_capital:,.2f}")
        print(f"  Risk per trade: {strategy.risk_per_trade * 100}%")
        
        return True
    except Exception as e:
        print(f"✗ Functionality error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("SPX Trading System - Installation Test")
    print("="*60)
    
    # Test imports
    import_success = test_imports()
    
    # Test basic functionality
    func_success = test_basic_functionality()
    
    # Summary
    print("\n" + "="*60)
    if import_success and func_success:
        print("✓ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run a simple backtest:")
        print("   python main.py --mode backtest --timeframe 5m")
        print("\n2. Run parameter optimization:")
        print("   python main.py --mode optimize --timeframe 5m")
        print("\n3. Run full analysis with report:")
        print("   python main.py --mode full --timeframe 5m --report")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- Ensure all dependencies are installed: pip install -r requirements.txt")
        print("- TA-Lib requires system-level installation")
    print("="*60)

if __name__ == "__main__":
    main()
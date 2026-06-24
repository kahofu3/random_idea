"""
SPX Trading System - Main Script
Run backtests, optimization, and generate reports
"""
import os
import sys
import argparse
import logging
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import TRADING_CONFIG, INDICATOR_PARAMS, BACKTEST_CONFIG
from src.data_handler import DataHandler
from src.indicators import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester
from src.visualization import ReportGenerator
from src.optimizer import StrategyOptimizer

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_single_backtest(timeframe: str = '5m', 
                       start_date: str = None,
                       end_date: str = None,
                       params: dict = None) -> dict:
    """
    Run a single backtest with specified parameters
    
    Args:
        timeframe: Trading timeframe ('5m' or '10m')
        start_date: Start date for backtest
        end_date: End date for backtest
        params: Indicator parameters (uses default if None)
        
    Returns:
        Backtest results dictionary
    """
    logger.info(f"Starting backtest for {timeframe} timeframe...")
    
    # Use config defaults if not specified
    if start_date is None:
        start_date = TRADING_CONFIG['start_date']
    if end_date is None:
        end_date = TRADING_CONFIG['end_date']
    if params is None:
        params = INDICATOR_PARAMS
    
    # Initialize components
    data_handler = DataHandler()
    indicators = TechnicalIndicators()
    strategy = TradingStrategy()
    backtester = Backtester(strategy)
    
    # Fetch data
    logger.info(f"Fetching data from {start_date} to {end_date}...")
    data = data_handler.fetch_data(
        interval=TRADING_CONFIG['timeframes'][timeframe],
        start_date=start_date,
        end_date=end_date
    )
    logger.info(f"Loaded {len(data)} data points")
    
    # Calculate indicators
    logger.info("Calculating technical indicators...")
    data_with_indicators = indicators.calculate_all_indicators(data, params)
    
    # Run backtest
    logger.info("Running backtest simulation...")
    results = backtester.run_backtest(data_with_indicators, params)
    
    # Print summary
    backtester.print_summary()
    
    return results


def run_optimization(timeframe: str = '5m',
                    start_date: str = None,
                    end_date: str = None) -> dict:
    """
    Run parameter optimization to find best indicators
    
    Args:
        timeframe: Trading timeframe
        start_date: Start date for optimization
        end_date: End date for optimization
        
    Returns:
        Optimization results
    """
    logger.info("Starting parameter optimization...")
    
    # Use config defaults if not specified
    if start_date is None:
        start_date = TRADING_CONFIG['start_date']
    if end_date is None:
        end_date = TRADING_CONFIG['end_date']
    
    # Load data
    data_handler = DataHandler()
    data = data_handler.fetch_data(
        interval=TRADING_CONFIG['timeframes'][timeframe],
        start_date=start_date,
        end_date=end_date
    )
    
    # Run optimization
    optimizer = StrategyOptimizer(data)
    results = optimizer.find_best_indicators()
    
    if results:
        logger.info(f"Optimization complete!")
        logger.info(f"Best indicator set: {results['best_indicator_set']}")
        logger.info(f"Best score: {results['best_score']:.4f}")
        
        # Save results
        optimizer.save_results('reports/optimization_results.json')
        
        # Print detailed report
        print("\n" + optimizer.generate_optimization_report())
        
        return results
    else:
        logger.error("Optimization failed - no valid results")
        return None


def run_walk_forward_analysis(timeframe: str = '5m',
                            start_date: str = None,
                            end_date: str = None) -> list:
    """
    Run walk-forward analysis
    
    Args:
        timeframe: Trading timeframe
        start_date: Start date
        end_date: End date
        
    Returns:
        Walk-forward results
    """
    logger.info("Starting walk-forward analysis...")
    
    # Use config defaults if not specified
    if start_date is None:
        start_date = TRADING_CONFIG['start_date']
    if end_date is None:
        end_date = TRADING_CONFIG['end_date']
    
    # Load data
    data_handler = DataHandler()
    data = data_handler.fetch_data(
        interval=TRADING_CONFIG['timeframes'][timeframe],
        start_date=start_date,
        end_date=end_date
    )
    
    # Run walk-forward optimization
    optimizer = StrategyOptimizer(data)
    results = optimizer.walk_forward_optimization()
    
    if results:
        logger.info(f"Walk-forward analysis complete - {len(results)} windows")
        
        # Calculate average performance
        avg_test_score = sum(r['test_score'] for r in results) / len(results)
        logger.info(f"Average out-of-sample score: {avg_test_score:.4f}")
        
        # Save results
        with open('reports/walk_forward_results.json', 'w') as f:
            json.dump(results, f, indent=4, default=str)
        
        return results
    else:
        logger.error("Walk-forward analysis failed")
        return []


def main():
    """
    Main entry point with command-line interface
    """
    parser = argparse.ArgumentParser(description='SPX Trading System')
    parser.add_argument('--mode', type=str, default='backtest',
                       choices=['backtest', 'optimize', 'walk-forward', 'full'],
                       help='Operation mode')
    parser.add_argument('--timeframe', type=str, default='5m',
                       choices=['5m', '10m'],
                       help='Trading timeframe')
    parser.add_argument('--start-date', type=str, default=None,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--report', action='store_true',
                       help='Generate full report')
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    logger.info(f"Starting SPX Trading System in {args.mode} mode")
    
    if args.mode == 'backtest':
        # Run single backtest with default parameters
        results = run_single_backtest(
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if args.report and results:
            reporter = ReportGenerator()
            reporter.generate_full_report(results)
            
    elif args.mode == 'optimize':
        # Find optimal parameters
        opt_results = run_optimization(
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if opt_results and args.report:
            # Run backtest with optimal parameters
            logger.info("Running backtest with optimal parameters...")
            results = run_single_backtest(
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                params=opt_results['best_params']
            )
            
            if results:
                reporter = ReportGenerator()
                reporter.generate_full_report(results, "SPX_Optimized")
                
    elif args.mode == 'walk-forward':
        # Run walk-forward analysis
        wf_results = run_walk_forward_analysis(
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if wf_results:
            logger.info("Walk-forward analysis completed successfully")
            
    elif args.mode == 'full':
        # Run complete analysis pipeline
        logger.info("Running full analysis pipeline...")
        
        # Step 1: Optimization
        opt_results = run_optimization(
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if opt_results:
            # Step 2: Backtest with optimal parameters
            logger.info("Testing optimal parameters...")
            backtest_results = run_single_backtest(
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                params=opt_results['best_params']
            )
            
            # Step 3: Generate comprehensive report
            if backtest_results:
                reporter = ReportGenerator()
                report_folder = reporter.generate_full_report(
                    backtest_results, 
                    f"SPX_Full_Analysis_{args.timeframe}"
                )
                
                # Save optimization results in report folder
                with open(os.path.join(report_folder, 'optimization_results.json'), 'w') as f:
                    json.dump(opt_results, f, indent=4, default=str)
                
                logger.info(f"Full analysis complete! Results saved in: {report_folder}")
    
    logger.info("SPX Trading System execution completed")


if __name__ == "__main__":
    main()
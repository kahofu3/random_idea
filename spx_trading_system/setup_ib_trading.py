#!/usr/bin/env python3
"""
Setup script for Interactive Brokers SPX Trading System
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'reports']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Created necessary directories")


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    # Install main requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Installed main requirements")
    except subprocess.CalledProcessError:
        print("⚠️  Some main requirements failed to install (TA-Lib often needs system installation)")
    
    # Install IB requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_ib.txt"])
        print("✅ Installed IB requirements")
    except subprocess.CalledProcessError:
        print("❌ Failed to install IB requirements")
        sys.exit(1)


def setup_environment():
    """Set up environment file"""
    if not Path('.env').exists() and Path('.env.example').exists():
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your IB credentials")
    else:
        print("ℹ️  .env file already exists")


def check_ib_gateway():
    """Check IB Gateway/TWS requirements"""
    print_header("Interactive Brokers Requirements")
    
    print("To use this trading bot, you need:")
    print("1. An Interactive Brokers account (paper or live)")
    print("2. IB Gateway or Trader Workstation (TWS) installed")
    print("3. API connections enabled in IB Gateway/TWS")
    print("\nIB Gateway Setup:")
    print("- Download from: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php")
    print("- Enable API connections: Configure -> Settings -> API -> Settings")
    print("- Check 'Enable ActiveX and Socket Clients'")
    print("- Add trusted IP: 127.0.0.1")
    print("- Socket port: 7497 (paper) or 7496 (live)")


def test_connection():
    """Test IB connection"""
    print_header("Testing IB Connection")
    
    try:
        from ib_insync import IB
        ib = IB()
        
        # Try to connect
        try:
            ib.connect('127.0.0.1', 7497, clientId=999)
            print("✅ Successfully connected to IB Gateway (paper trading)")
            
            # Get account info
            account = ib.managedAccounts()
            if account:
                print(f"✅ Connected to account: {account[0]}")
            
            ib.disconnect()
            
        except Exception as e:
            print(f"❌ Could not connect to IB Gateway: {e}")
            print("\nMake sure:")
            print("1. IB Gateway is running")
            print("2. API connections are enabled")
            print("3. Port 7497 (paper) or 7496 (live) is correct")
            
    except ImportError:
        print("❌ ib_insync not installed properly")


def create_run_script():
    """Create run scripts for different platforms"""
    # Unix/Linux/Mac script
    unix_script = """#!/bin/bash
# SPX Trading Bot Runner

echo "Starting SPX Trading Bot..."
echo "Make sure IB Gateway is running!"
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the trading bot
python3 ib_live_trader.py
"""
    
    # Windows script
    windows_script = """@echo off
REM SPX Trading Bot Runner

echo Starting SPX Trading Bot...
echo Make sure IB Gateway is running!
echo.

REM Activate virtual environment if exists
if exist venv\\Scripts\\activate (
    call venv\\Scripts\\activate
)

REM Run the trading bot
python ib_live_trader.py
pause
"""
    
    with open('run_trader.sh', 'w') as f:
        f.write(unix_script)
    os.chmod('run_trader.sh', 0o755)
    
    with open('run_trader.bat', 'w') as f:
        f.write(windows_script)
    
    print("✅ Created run scripts: run_trader.sh (Unix/Mac) and run_trader.bat (Windows)")


def main():
    """Main setup function"""
    print_header("SPX Trading System - IB Setup")
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Check IB requirements
    check_ib_gateway()
    
    # Test connection
    test_connection()
    
    # Create run scripts
    create_run_script()
    
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("1. Edit .env file with your IB credentials")
    print("2. Start IB Gateway or TWS")
    print("3. Run the trading bot:")
    print("   - Unix/Mac: ./run_trader.sh")
    print("   - Windows: run_trader.bat")
    print("   - Or directly: python ib_live_trader.py")
    print("\n⚠️  ALWAYS TEST WITH PAPER TRADING FIRST!")
    print("\nFor monitoring:")
    print("- Check logs/ib_trading.log for activity")
    print("- Check logs/trades.csv for trade history")
    

if __name__ == "__main__":
    main()
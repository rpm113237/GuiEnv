#!/bin/bash
# Install pigpio in GuiEnv virtual environment
# This script automates the entire installation process

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          Installing pigpio in GuiEnv                          ║"
echo "║      (Python library + System daemon)                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Activate virtual environment
echo -e "${BLUE}Step 1: Activating virtual environment...${NC}"
cd /home/rpm/GuiEnv
source bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo

# Step 2: Upgrade pip
echo -e "${BLUE}Step 2: Upgrading pip...${NC}"
pip install --quiet --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"
echo

# Step 3: Install pigpio Python library
echo -e "${BLUE}Step 3: Installing pigpio Python library...${NC}"
pip install pigpio
echo -e "${GREEN}✓ pigpio library installed${NC}"
echo

# Step 4: Verify Python library
echo -e "${BLUE}Step 4: Verifying Python library...${NC}"
PIGPIO_VERSION=$(python3 -c "import pigpio; print(pigpio.VERSION)" 2>/dev/null || echo "unknown")
echo -e "${GREEN}✓ pigpio version: ${PIGPIO_VERSION}${NC}"
echo

# Step 5: Deactivate virtual environment
echo -e "${BLUE}Step 5: Deactivating virtual environment...${NC}"
deactivate
echo -e "${GREEN}✓ Virtual environment deactivated${NC}"
echo

# Step 6: Install system daemon
echo -e "${BLUE}Step 6: Installing pigpiod daemon (system-wide)...${NC}"
echo "This requires sudo. You may be prompted for your password."
sudo apt-get update --quiet
sudo apt-get install -y pigpiod
echo -e "${GREEN}✓ pigpiod daemon installed${NC}"
echo

# Step 7: Enable daemon on boot
echo -e "${BLUE}Step 7: Enabling daemon to start on boot...${NC}"
sudo systemctl enable pigpiod
echo -e "${GREEN}✓ pigpiod enabled for auto-start${NC}"
echo

# Step 8: Start daemon
echo -e "${BLUE}Step 8: Starting pigpiod daemon...${NC}"
sudo systemctl start pigpiod
echo -e "${GREEN}✓ pigpiod daemon started${NC}"
echo

# Step 9: Verify daemon
echo -e "${BLUE}Step 9: Verifying daemon is running...${NC}"
if systemctl is-active --quiet pigpiod; then
    echo -e "${GREEN}✓ pigpiod daemon is running${NC}"
else
    echo -e "${YELLOW}⚠ pigpiod daemon may not be running${NC}"
    echo "Try: sudo systemctl status pigpiod"
fi
echo

# Step 10: Test connection
echo -e "${BLUE}Step 10: Testing daemon connection...${NC}"
source bin/activate
python3 << 'PYTHON_TEST'
import pigpio
pi = pigpio.pi()
if pi.connected:
    print('\033[0;32m✓ Successfully connected to pigpiod daemon\033[0m')
    pi.stop()
else:
    print('\033[1;33m⚠ Could not connect to daemon\033[0m')
    print('  Try: sudo systemctl restart pigpiod')
PYTHON_TEST
deactivate
echo

echo "╔════════════════════════════════════════════════════════════════╗"
echo -e "${GREEN}║                 ✓ Installation Complete!              ║${NC}"
echo "╚════════════════════════════════════════════════════════════════╝"
echo
echo -e "${GREEN}What's installed:${NC}"
echo "  ✓ pigpio Python library (in virtual environment)"
echo "  ✓ pigpiod daemon (system-wide service)"
echo "  ✓ Daemon enabled for auto-start on boot"
echo
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Run your application: python3 BLE_plus_serial.py"
echo "  2. Motor control will work automatically"
echo
echo -e "${BLUE}Useful commands:${NC}"
echo "  Activate venv:        source /home/rpm/GuiEnv/bin/activate"
echo "  Check daemon status:  sudo systemctl status pigpiod"
echo "  Stop daemon:          sudo systemctl stop pigpiod"
echo "  Start daemon:         sudo systemctl start pigpiod"
echo "  View daemon logs:     sudo journalctl -u pigpiod -n 20"
echo

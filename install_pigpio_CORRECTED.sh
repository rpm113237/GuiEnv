#!/bin/bash

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   PIGPIO Installation for GuiEnv (Corrected)                   ║"
echo "║   Raspberry Pi 4 - Hardware PWM via GPIO 18                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Update package lists
echo "Step 1: Updating package lists..."
sudo apt-get update -qq
echo "✓ Package lists updated"
echo ""

# Step 2: Install system dependencies (only what's available)
echo "Step 2: Installing pigpio system tools and libraries..."
sudo apt-get install -y pigpio-tools python3-pigpio libpigpiod-if2-1t64
echo "✓ System packages installed"
echo ""

# Step 3: Activate virtual environment
echo "Step 3: Activating GuiEnv virtual environment..."
source /home/rpm/GuiEnv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 4: Install/upgrade pip
echo "Step 4: Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"
echo ""

# Step 5: Install pigpio Python library
echo "Step 5: Installing pigpio Python library..."
pip install pigpio -q
echo "✓ pigpio Python library installed"
echo ""

# Step 6: Verify Python library
echo "Step 6: Verifying pigpio Python library..."
python3 -c "import pigpio; print(f'✓ pigpio library version: {pigpio.VERSION}')"
echo ""

# Step 7: Install pigpiod daemon from source
echo "Step 7: Installing pigpiod daemon from source..."
echo "        (This is necessary because pigpiod is not in apt repos)"
echo ""

# Check if already downloaded
if [ ! -d /tmp/pigpio ]; then
    echo "   - Downloading pigpio source from GitHub..."
    cd /tmp
    git clone https://github.com/joan2937/pigpio.git -q
    cd pigpio
else
    echo "   - pigpio source already exists, using cached version"
    cd /tmp/pigpio
    git pull -q
fi

echo "   - Building pigpiod daemon..."
make -j4 -q 2>/dev/null || make -q

echo "   - Installing pigpiod daemon to /usr/local/bin..."
sudo make install -q

# Return to GuiEnv directory
cd /home/rpm/GuiEnv

echo "✓ pigpiod daemon installed to /usr/local/bin"
echo ""

# Step 8: Create systemd service file for pigpiod (if not already present)
echo "Step 8: Setting up pigpiod as system service..."

if [ ! -f /etc/systemd/system/pigpiod.service ]; then
    echo "   - Creating pigpiod.service..."
    sudo tee /etc/systemd/system/pigpiod.service > /dev/null << 'SERVICE'
[Unit]
Description=pigpio daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/pigpiod
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE
    
    echo "   - Reloading systemd daemon..."
    sudo systemctl daemon-reload -q
    echo "✓ Service file created and registered"
else
    echo "   - Service file already exists"
fi
echo ""

# Step 9: Enable and start pigpiod
echo "Step 9: Enabling and starting pigpiod service..."
sudo systemctl enable pigpiod -q
sudo systemctl start pigpiod

# Give it a moment to start
sleep 1

# Check if running
if sudo systemctl is-active --quiet pigpiod; then
    echo "✓ pigpiod service started and enabled for auto-start"
else
    echo "⚠ Warning: pigpiod may not have started. Check with: sudo systemctl status pigpiod"
fi
echo ""

# Step 10: Verify daemon connection
echo "Step 10: Verifying daemon connection..."
python3 << 'PYTHON'
import pigpio
import time

try:
    pi = pigpio.pi()
    if pi.connected:
        print(f"✓ Successfully connected to pigpiod daemon")
        # Try reading a GPIO mode as a sanity check
        mode = pi.get_mode(18)
        print(f"✓ GPIO 18 is accessible (current mode: {mode})")
        pi.stop()
    else:
        print("✗ Failed to connect to pigpiod daemon")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
PYTHON

echo ""

# Step 11: Deactivate virtual environment
echo "Step 11: Deactivating virtual environment..."
deactivate
echo "✓ Virtual environment deactivated"
echo ""

# Final summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ INSTALLATION COMPLETE!                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "What was installed:"
echo "  ✓ System pigpio tools and libraries"
echo "  ✓ pigpio Python library (in virtual environment)"
echo "  ✓ pigpiod daemon (from source)"
echo "  ✓ systemd service for auto-start"
echo ""
echo "Next steps:"
echo "  1. Verify daemon is running:"
echo "     sudo systemctl status pigpiod"
echo ""
echo "  2. Connect your BTS7960 motor driver:"
echo "     GPIO 18  = Speed (PWM)"
echo "     GPIO 23  = Direction 1"
echo "     GPIO 24  = Direction 2"
echo ""
echo "  3. Run your application:"
echo "     cd /home/rpm/GuiEnv && source bin/activate"
echo "     python3 BLE_plus_serial.py"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status pigpiod       # Check daemon status"
echo "  sudo systemctl restart pigpiod      # Restart daemon"
echo "  sudo journalctl -u pigpiod -n 20   # View daemon logs"
echo ""

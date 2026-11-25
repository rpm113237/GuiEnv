# Installing pigpio in GuiEnv Virtual Environment

## Quick Install (3 Steps)

### Step 1: Activate the Virtual Environment
```bash
cd /home/rpm/GuiEnv
source bin/activate
```

You should see the prompt change to something like:
```
(GuiEnv) rpm@hostname:~/GuiEnv$
```

### Step 2: Install pigpio Python Library
```bash
pip install pigpio
```

### Step 3: Verify Installation
```bash
python3 -c "import pigpio; print(f'pigpio version: {pigpio.VERSION}')"
```

If successful, you'll see the version number.

---

## Full Installation Guide with All Steps

### Prerequisites
- Virtual environment already created (✅ You have this)
- pip package manager (✅ Included with venv)
- Raspberry Pi 4 (assumed)

### Installation Steps

#### 1. Activate Virtual Environment
```bash
cd /home/rpm/GuiEnv
source bin/activate
```

Expected output:
```
(GuiEnv) rpm@hostname:~/GuiEnv$
```

#### 2. Upgrade pip (Recommended)
```bash
pip install --upgrade pip
```

This ensures you have the latest pip for smooth installation.

#### 3. Install pigpio Library
```bash
pip install pigpio
```

Output should show:
```
Successfully installed pigpio-X.XX.X
```

#### 4. Install pigpiod Daemon (System-wide)
This requires sudo and is separate from the Python library:

```bash
# Update package list
sudo apt-get update

# Install pigpiod daemon
sudo apt-get install -y pigpiod

# Enable daemon to start on boot (optional but recommended)
sudo systemctl enable pigpiod

# Start daemon immediately
sudo systemctl start pigpiod

# Verify daemon is running
systemctl status pigpiod
```

Expected output:
```
● pigpiod.service - Raspberry Pi GPIO control service
   Loaded: loaded...
   Active: active (running)...
```

#### 5. Verify Everything Works
```bash
# Check Python library
python3 -c "import pigpio; print(f'Python lib: {pigpio.VERSION}')"

# Check daemon is running
ps aux | grep pigpiod

# Try to connect from Python
python3 -c "
import pigpio
pi = pigpio.pi()
if pi.connected:
    print('✓ Connected to pigpio daemon')
    pi.stop()
else:
    print('✗ Failed to connect to daemon')
"
```

---

## Complete Installation Commands (Copy-Paste Ready)

### For Python Library Only (In Virtual Environment)
```bash
cd /home/rpm/GuiEnv
source bin/activate
pip install --upgrade pip
pip install pigpio
python3 -c "import pigpio; print(f'pigpio version: {pigpio.VERSION}')"
deactivate
```

### For Full Installation (Python + Daemon)
```bash
# Activate venv and install Python library
cd /home/rpm/GuiEnv
source bin/activate
pip install --upgrade pip
pip install pigpio
python3 -c "import pigpio; print(f'✓ Python lib installed: {pigpio.VERSION}')"
deactivate

# Install system daemon (requires sudo)
sudo apt-get update
sudo apt-get install -y pigpiod
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Verify daemon
systemctl status pigpiod

# Final verification
ps aux | grep pigpiod
```

---

## Verification Checklist

After installation, verify each component:

```bash
# 1. Check Python library is installed
cd /home/rpm/GuiEnv
source bin/activate
python3 -c "import pigpio; print(f'✓ pigpio: {pigpio.VERSION}')"

# 2. Check daemon is running
sudo systemctl status pigpiod

# 3. Check daemon can be accessed
python3 -c "
import pigpio
pi = pigpio.pi()
if pi.connected:
    print('✓ Daemon connection: OK')
    # Try to read a GPIO pin
    mode = pi.get_mode(17)  # GPIO 17
    print(f'✓ GPIO read test: OK (GPIO 17 mode = {mode})')
    pi.stop()
else:
    print('✗ Daemon connection: FAILED')
    print('  Run: sudo systemctl start pigpiod')
"

deactivate
```

---

## Troubleshooting

### Issue: "No module named pigpio"
```bash
# Solution: Make sure venv is activated
cd /home/rpm/GuiEnv
source bin/activate
pip install pigpio
```

### Issue: "Failed to connect to pigpio daemon"
```bash
# Solution: Start the daemon
sudo systemctl start pigpiod

# Or enable it permanently
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Verify it's running
systemctl status pigpiod
```

### Issue: "Permission denied" when installing
```bash
# Solution: Use pip with user scope
pip install --user pigpio

# Or ensure venv is activated
source bin/activate
pip install pigpio
```

### Issue: Daemon won't start
```bash
# Check if already running
ps aux | grep pigpiod

# Check logs
sudo journalctl -u pigpiod -n 20

# Try manual start
sudo pigpiod

# Stop manual instance
sudo pkill pigpiod

# Restart service
sudo systemctl restart pigpiod
```

---

## Two Components: Understand the Difference

### 1. Python Library (`pigpio` package)
- **What it is**: Python module to control GPIO
- **Install in**: Virtual environment
- **Command**: `pip install pigpio`
- **Used by**: Your Python application
- **Location**: `/home/rpm/GuiEnv/lib/python3.13/site-packages/pigpio.py`

### 2. Daemon (`pigpiod` service)
- **What it is**: Background service that handles GPIO
- **Install in**: System-wide (requires sudo)
- **Command**: `sudo apt-get install pigpiod`
- **Used by**: Python library communicates with this
- **Location**: `/usr/bin/pigpiod`

**You need BOTH for the motor driver to work:**
1. Python library (in your venv)
2. Daemon running (system service)

---

## Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `source /home/rpm/GuiEnv/bin/activate` |
| Install pigpio lib | `pip install pigpio` |
| Check installation | `python3 -c "import pigpio; print(pigpio.VERSION)"` |
| Start daemon | `sudo systemctl start pigpiod` |
| Check daemon status | `sudo systemctl status pigpiod` |
| Enable auto-start | `sudo systemctl enable pigpiod` |
| Stop daemon | `sudo systemctl stop pigpiod` |
| View daemon logs | `sudo journalctl -u pigpiod` |
| Test connection | `python3 test_pigpio.py` (see below) |

---

## Test Script

Create a file `test_pigpio.py` to verify everything:

```python
#!/usr/bin/env python3
"""Test pigpio installation and daemon connection"""

import sys

# Test 1: Python library import
print("Test 1: Checking pigpio import...")
try:
    import pigpio
    print(f"✓ pigpio library imported successfully (v{pigpio.VERSION})")
except ImportError as e:
    print(f"✗ Failed to import pigpio: {e}")
    print("  Run: pip install pigpio")
    sys.exit(1)

# Test 2: Daemon connection
print("\nTest 2: Checking daemon connection...")
pi = pigpio.pi()
if pi.connected:
    print("✓ Connected to pigpio daemon")
else:
    print("✗ Failed to connect to daemon")
    print("  Run: sudo systemctl start pigpiod")
    sys.exit(1)

# Test 3: GPIO access
print("\nTest 3: Testing GPIO access...")
try:
    # Try to get mode of GPIO 17
    mode = pi.get_mode(17)
    print(f"✓ GPIO access working (GPIO 17 mode = {mode})")
except Exception as e:
    print(f"✗ GPIO access failed: {e}")
    pi.stop()
    sys.exit(1)

# Test 4: GPIO 18 (our PWM pin)
print("\nTest 4: Testing GPIO 18 (PWM pin)...")
try:
    # Try to get mode of GPIO 18
    mode = pi.get_mode(18)
    print(f"✓ GPIO 18 accessible (mode = {mode})")
except Exception as e:
    print(f"✗ GPIO 18 access failed: {e}")
    pi.stop()
    sys.exit(1)

# Cleanup
pi.stop()

print("\n" + "="*50)
print("✓ All tests passed! pigpio is ready to use.")
print("="*50)
```

Run it with:
```bash
cd /home/rpm/GuiEnv
source bin/activate
python3 test_pigpio.py
```

---

## Final Verification

After installation, your system should have:

```
✓ Python library in venv
  /home/rpm/GuiEnv/lib/python3.13/site-packages/pigpio.py

✓ Daemon installed system-wide
  /usr/bin/pigpiod

✓ Daemon running as service
  systemctl status pigpiod → active (running)

✓ Your app can import and use
  python3 -c "import pigpio"

✓ Ready for BTS7960 motor control
  GPIO 18 (PWM0) accessible
  GPIO 23, 24 (direction) accessible
```

---

## Next Steps

After installing pigpio:

1. ✅ Verify installation with test script above
2. ✅ Ensure daemon is running: `sudo systemctl start pigpiod`
3. ✅ Run your application: `python3 BLE_plus_serial.py`
4. ✅ Motor control should work automatically

The `BLE_plus_serial.py` has built-in error handling:
- If pigpio not installed: Warning logged, app continues
- If daemon not running: Warning logged, motor disabled
- If GPIO unavailable: Graceful degradation

But for full functionality, pigpio + daemon are required.

---

## Command Summary (Copy-Paste)

### Installation (5 minutes)
```bash
# Activate virtual environment
cd /home/rpm/GuiEnv && source bin/activate

# Install pigpio library
pip install --upgrade pip && pip install pigpio

# Verify Python library
python3 -c "import pigpio; print(f'✓ Library: {pigpio.VERSION}')"

# Deactivate venv
deactivate

# Install system daemon
sudo apt-get update && sudo apt-get install -y pigpiod

# Enable and start daemon
sudo systemctl enable pigpiod && sudo systemctl start pigpiod

# Verify daemon
sudo systemctl status pigpiod
```

That's it! You're ready to use the motor driver.


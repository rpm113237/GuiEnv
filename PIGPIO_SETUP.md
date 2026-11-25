# Quick pigpio Setup Guide

## 🚀 5-Minute Setup

### Step 1: Install pigpio
```bash
sudo apt-get update
sudo apt-get install pigpio python3-pigpio
```

### Step 2: Start and Enable Daemon
```bash
# Start the daemon
sudo systemctl start pigpiod

# Enable on boot (recommended)
sudo systemctl enable pigpiod
```

### Step 3: Verify Installation
```bash
# Check daemon is running
ps aux | grep pigpiod

# Should show something like:
# root      1234  0.0  0.1   1234  5678 ?  Ss  14:50   0:00 /usr/bin/pigpiod

# Test pigpio connection
python3 << 'EOF'
import pigpio
pi = pigpio.pi()
if pi.connected:
    print("✓ pigpio connected successfully!")
    pi.stop()
else:
    print("✗ Failed to connect to pigpio daemon")
EOF
```

### Step 4: Run Application
```bash
cd /home/rpm/GuiEnv
sudo python3 BLE_plus_serial.py
```

### Step 5: Verify Motor Works
- Look for log message: `"BTS7960 motor driver initialized successfully (pigpio hardware PWM)"`
- Run AutoCal calibration
- Watch motor respond smoothly

## ✅ Installation Checklist

```
□ Installed pigpio packages
□ Started pigpiod daemon
□ Verified daemon is running (ps aux)
□ Tested Python connection
□ Application runs without errors
□ Motor initialization message appears
□ AutoCal test successful
```

## 🔧 Common Commands

### Daemon Management
```bash
# Start daemon
sudo systemctl start pigpiod

# Stop daemon
sudo systemctl stop pigpiod

# Restart daemon
sudo systemctl restart pigpiod

# Check status
sudo systemctl status pigpiod

# View logs
sudo journalctl -u pigpiod -f
```

### Manual Daemon (for debugging)
```bash
# Run in foreground (shows debug output)
sudo pigpiod -v

# Kill it with Ctrl+C
```

### Python Testing
```bash
python3 << 'EOF'
import pigpio

# Connect to daemon
pi = pigpio.pi()

# Check connection
print("Connected:", pi.connected)

# Test GPIO write
pi.set_mode(23, pigpio.OUTPUT)
pi.write(23, 1)  # Set HIGH
print("GPIO 23 set to HIGH")

pi.write(23, 0)  # Set LOW
print("GPIO 23 set to LOW")

# Test PWM
pi.hardware_PWM(25, 1000, 500000)  # 50% duty
print("PWM set to 50%")

pi.hardware_PWM(25, 1000, 0)  # 0% duty
print("PWM stopped")

# Cleanup
pi.stop()
print("Done!")
EOF
```

## 🐛 Troubleshooting

### "pigpio daemon not running"
```bash
# Start it
sudo systemctl start pigpiod

# Or run manually
sudo pigpiod

# Check if it's running
ps aux | grep pigpiod
```

### "Connection refused" or socket error
```bash
# Restart the daemon
sudo systemctl restart pigpiod

# Check daemon logs
sudo journalctl -u pigpiod -n 20
```

### Permission denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio $(whoami)

# Log out and back in
# Then test
python3 -c "import pigpio; pi = pigpio.pi(); print('Connected:', pi.connected)"
```

### "pigpio not installed"
```bash
sudo apt-get install pigpio python3-pigpio
```

## 📊 Verification Output

After successful setup:

```bash
$ ps aux | grep pigpiod
root      1234  0.0  0.1   1234  5678 ?  Ss  14:50   0:00 /usr/bin/pigpiod

$ python3 -c "import pigpio; pi = pigpio.pi(); print('Connected:', pi.connected); pi.stop()"
Connected: True

$ sudo python3 BLE_plus_serial.py
# ... normal application startup ...
# Should see: "BTS7960 motor driver initialized successfully (pigpio hardware PWM)"
```

## 🎯 Next Steps

1. ✅ Install pigpio (above)
2. ✅ Start pigpiod daemon
3. Run your application: `sudo python3 BLE_plus_serial.py`
4. Test with AutoCal calibration
5. Enjoy superior motor control! 🎉

## 📞 Need Help?

**Check these files:**
- `PIGPIO_UPGRADE.md` - Detailed upgrade information
- `BTS7960_MOTOR_DRIVER.md` - Motor control reference
- `Getting_Started.md` - General quick start

**Common Issues:**
- Daemon not starting? → Check `sudo systemctl status pigpiod`
- Connection errors? → Restart daemon with `sudo systemctl restart pigpiod`
- Python errors? → Verify package with `python3 -c "import pigpio"`

---

**That's it!** You now have professional-grade hardware PWM for your motor control. 🚀

# ⚠️ FIX: "Unable to locate package pigpiod"

## The Problem

When you ran:
```bash
sudo apt-get install pigpiod
```

You got:
```
E: Unable to locate package pigpiod
```

**Why?** The `pigpiod` daemon package is **NOT in the standard Raspberry Pi apt repositories**.

---

## The Solution

The corrected installation script handles this by:

1. **Installing available system packages:**
   ```bash
   sudo apt-get install pigpio-tools python3-pigpio libpigpiod-if2-1t64
   ```

2. **Building pigpiod from source:**
   - Downloads official source from GitHub
   - Compiles it
   - Installs to `/usr/local/bin/pigpiod`

3. **Creating a systemd service** for auto-start

---

## 🚀 Quick Fix - Use the Corrected Script

```bash
bash /home/rpm/GuiEnv/install_pigpio_CORRECTED.sh
```

**What it does:**
- ✅ Installs system packages (pigpio-tools, python3-pigpio)
- ✅ Installs pigpio Python library (pip install pigpio)
- ✅ Clones pigpio source from GitHub
- ✅ Builds pigpiod daemon
- ✅ Installs pigpiod to /usr/local/bin
- ✅ Creates systemd service
- ✅ Enables auto-start
- ✅ Verifies everything works

**Time:** ~5-10 minutes (includes compilation)

---

## What Gets Installed

### System Packages (via apt)
```
✓ pigpio-tools           - Command-line tools
✓ python3-pigpio         - Python library from apt
✓ libpigpiod-if2-1t64    - Library dependencies
```

### From Source (via GitHub)
```
✓ pigpiod daemon         - GPIO daemon
✓ pigpio.py              - Additional Python module
```

### In Virtual Environment (via pip)
```
✓ pigpio                 - Python module for daemon control
```

---

## Why Build from Source?

**pigpiod** (the daemon) is maintained by the original pigpio author but not packaged in apt repositories.

**Solution:** Build from official source:
```
https://github.com/joan2937/pigpio.git
```

This is the **official, authoritative source** and is what all Raspberry Pi GPIO projects use.

---

## Locations After Installation

```
System Packages:
  /usr/bin/pigpio-tools        - Command-line tools
  /usr/lib/*/pigpio*           - System libraries

From Source (compiled):
  /usr/local/bin/pigpiod       - Daemon executable
  /usr/local/bin/pig2vcd       - Utilities
  /usr/local/lib/libpigpio*    - Compiled libraries

Virtual Environment:
  /home/rpm/GuiEnv/lib/python3.13/site-packages/pigpio.py

Systemd Service:
  /etc/systemd/system/pigpiod.service
```

---

## Verify Installation

After running the corrected script:

```bash
# 1. Check if daemon is running
sudo systemctl status pigpiod

# 2. Test Python library
cd /home/rpm/GuiEnv && source bin/activate
python3 -c "import pigpio; print(pigpio.VERSION)"

# 3. Test daemon connection
python3 -c "
import pigpio
pi = pigpio.pi()
print('Connected!' if pi.connected else 'Failed!')
pi.stop()
"

# 4. Deactivate
deactivate
```

---

## Common Issues & Fixes

### "git: command not found"
```bash
sudo apt-get install git
```

### "make: command not found"
```bash
sudo apt-get install build-essential
```

### "pigpiod: command not found"
```bash
# The script installs to /usr/local/bin, so try:
/usr/local/bin/pigpiod

# Or check if service is running:
sudo systemctl status pigpiod
```

### "Cannot connect to daemon"
```bash
# Restart the daemon:
sudo systemctl restart pigpiod

# Or start it manually:
sudo /usr/local/bin/pigpiod
```

---

## Files Available

| File | Purpose |
|------|---------|
| `install_pigpio_CORRECTED.sh` | ✅ **USE THIS ONE** - Fixed to handle apt issue |
| `install_pigpio.sh` | Old script (tried to install non-existent pigpiod package) |
| `PIGPIO_INSTALLATION.md` | General installation guide |
| `PIGPIO_QUICKSTART.txt` | Quick reference |

---

## Next Steps

1. **Run the corrected script:**
   ```bash
   bash /home/rpm/GuiEnv/install_pigpio_CORRECTED.sh
   ```

2. **Wait for completion** (5-10 minutes)

3. **Verify installation:**
   ```bash
   sudo systemctl status pigpiod
   ```

4. **Connect your motor hardware**

5. **Run your application:**
   ```bash
   cd /home/rpm/GuiEnv && source bin/activate
   python3 BLE_plus_serial.py
   ```

---

## Technical Details

### Why This Approach Works

The issue is that Raspberry Pi OS doesn't include `pigpiod` in its apt repositories. However:

1. The **pigpio library** is available in apt (`python3-pigpio`)
2. The **source code** is freely available on GitHub
3. Building from source is straightforward (just `make` and `make install`)

By combining both approaches:
- ✅ Get system support from apt packages
- ✅ Build the daemon from official source
- ✅ Set up systemd for auto-start
- ✅ Full compatibility with your application

### The Two-Component Architecture Still Works

```
Your Code (BLE_plus_serial.py)
        ↓
pigpio Python module (pip + apt)
        ↓
pigpiod daemon (built from source)
        ↓
GPIO Hardware (Broadcom BCM2711)
        ↓
BTS7960 Motor Driver
```

Nothing changes from your application perspective—the daemon is now installed, just built from source instead of from apt.

---

## Support Files

- `QUICK_REFERENCE.md` - Motor control cheat sheet
- `motor_control_examples.py` - 10 usage examples
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `RPI4_HARDWARE_PWM_NOTES.md` - Hardware PWM info
- `WIRING_DIAGRAM.txt` - GPIO connection diagram

---

**Version:** 2.0 (Corrected for pigpiod availability)
**Created:** 2024-11-24
**Status:** ✅ Ready to run

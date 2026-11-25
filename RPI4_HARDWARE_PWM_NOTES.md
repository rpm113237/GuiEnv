# Raspberry Pi 4 Hardware PWM Configuration

## Important Update: Using True Hardware PWM

The BTS7960 motor driver now uses **GPIO 18 (PWM0)** for hardware PWM control, which is true hardware PWM on the Raspberry Pi 4.

### Hardware PWM Pins on Raspberry Pi 4

| PWM Channel | GPIO Pins | Usage |
|------------|-----------|-------|
| PWM0 | GPIO 12, GPIO 18 | Hardware PWM channel 0 |
| PWM1 | GPIO 13, GPIO 19 | Hardware PWM channel 1 |

### Current Configuration

```
GPIO 23 (IN1)   → Direction control
GPIO 24 (IN2)   → Direction control  
GPIO 18 (PWM0)  → Hardware PWM speed control ✅
```

### Why GPIO 18 Instead of GPIO 25?

- **GPIO 25**: Regular GPIO pin (software-emulated PWM via bit-banging)
  - Higher CPU overhead
  - Less stable frequency
  - Software timing-dependent

- **GPIO 18**: True Hardware PWM0 (dedicated PWM hardware)
  - True hardware PWM from Broadcom chip
  - Minimal CPU overhead
  - Precise, stable frequency
  - Not affected by OS scheduling

### Alternative Configurations

If GPIO 18 is needed for other purposes, you can use:

**Option 1: Use GPIO 12 (PWM0)**
```python
BTS7960_EN = 12  # Alternative PWM0 pin
```

**Option 2: Use GPIO 13 or 19 (PWM1)**
```python
BTS7960_EN = 13  # PWM1 channel
# or
BTS7960_EN = 19  # PWM1 channel
```

### How to Change the PWM Pin

If you need to use a different PWM pin:

1. Edit `BLE_plus_serial.py`
2. Find line: `BTS7960_EN = 18`
3. Change to desired GPIO: `BTS7960_EN = 12` (or 13, 19)
4. Update wiring diagram accordingly
5. Restart application

### Verification

To verify GPIO 18 is working as hardware PWM:

```bash
# Check if pigpiod is running
systemctl status pigpiod

# Monitor CPU usage while motor running
top  # Should show minimal CPU usage

# Check actual PWM frequency
# Motor should respond smoothly without jitter
```

### Technical Details

**Raspberry Pi 4 PWM Specifications:**
- Frequency range: 10 Hz to 125 MHz
- Duty cycle resolution: 1,000,000 steps (0-1,000,000)
- Supported frequency in this implementation: 1000 Hz
- Response time: < 1 microsecond
- Hardware provider: Broadcom BCM2711 chip

### Performance Comparison

| Metric | GPIO 18 (Hardware PWM) | GPIO 25 (Software PWM) |
|--------|------------------------|------------------------|
| CPU Usage | Minimal | Significant |
| Frequency Stability | Excellent | Variable |
| Response Time | < 1µs | Variable |
| Jitter | None | Present |
| OS Scheduling Impact | No | Yes |

### Implementation Impact

The change from GPIO 25 to GPIO 18 is **transparent**:
- No code changes required (already updated in BLE_plus_serial.py)
- Same motor control logic
- Same sensitivity tuning
- Better performance automatically

### Notes

- GPIO 18 is the recommended pin for this application on Raspberry Pi 4
- pigpio daemon handles all hardware PWM details internally
- The motor will respond more smoothly with true hardware PWM
- Multiple motors can be controlled if using different PWM channels (PWM0 and PWM1)

---

**Status**: Updated for Raspberry Pi 4 Hardware PWM ✅
**Pin**: GPIO 18 (PWM0 - True Hardware PWM)
**Performance**: Improved stability and reliability

# BTS7960 Motor Driver Integration - Getting Started

## 🎯 What's New

Your `BLE_plus_serial.py` application now includes **automatic motor control** using the BTS7960 PWM motor driver! 

The motor will automatically drive based on the delta value (difference between current sensor reading and target) during the AutoSendLoop calibration sequence.

## 📋 Quick Setup Checklist

```
□ Read this Getting Started guide
□ Review WIRING_DIAGRAM.txt for hardware connections
□ Connect BTS7960 to GPIO pins 23, 24, 25
□ Connect motor to BTS7960 output
□ Connect power supply to BTS7960
□ Run the application with sudo
□ Trigger AutoCal to test motor
□ Fine-tune sensitivity if needed
□ Run safety validation tests
```

## 🔌 Hardware Setup (5 minutes)

### Pin Connections
```
Raspberry Pi GPIO          BTS7960 Motor Driver
├── GPIO 23 ────────────→ IN1 (Direction)
├── GPIO 24 ────────────→ IN2 (Direction)
├── GPIO 25 ────────────→ EN  (PWM Speed)
└── GND    ────────────→ GND

Motor:
├── BTS7960 OUT1 ────────→ Motor + Terminal
└── BTS7960 OUT2 ────────→ Motor - Terminal
```

**See WIRING_DIAGRAM.txt for detailed diagrams and power connections.**

## 🚀 Running the Application

```bash
# Navigate to project directory
cd /home/rpm/GuiEnv

# Run with sudo (required for GPIO access)
sudo python3 BLE_plus_serial.py

# Check for initialization message in output:
# "BTS7960 motor driver initialized successfully"
```

## 🧪 Quick Test

1. **Start the application**: `sudo python3 BLE_plus_serial.py`
2. **Set calibration parameters**:
   - Start: 0
   - Step: 10
   - Num Steps: 1
3. **Click "Start AutoCal"**
4. **Watch the motor**: It should spin based on sensor overshoot/undershoot
5. **Motor should stop** when target is reached (within 5 lbs tolerance)

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **BTS7960_MOTOR_DRIVER.md** | Complete technical guide with all details |
| **WIRING_DIAGRAM.txt** | Hardware wiring diagrams and pin connections |
| **motor_control_examples.py** | 10 usage examples with code |
| **MOTOR_TESTING_GUIDE.md** | 7 comprehensive test procedures |
| **INTEGRATION_SUMMARY.md** | Complete integration overview |
| **Getting_Started.md** | This file |

## ⚙️ How It Works

### During AutoSendLoop Calibration:
1. Application sets a target value (TGT)
2. Gets current sensor reading (SF)
3. **Calculates delta**: `delval = SF - TGT`
4. **Controls motor**: Speed proportional to delta
   - If `delval > 0` (overshoot): Motor runs **reverse**
   - If `delval < 0` (undershoot): Motor runs **forward**
   - If `delval ≈ 0` (at target): Motor **stops**
5. Sensor adjusts, loop repeats until target reached
6. Next calibration step begins

### Motor Speed Mapping:
```
speed_percent = min(|delval| / sensitivity * 100, max_duty)

Default sensitivity: 10.0 lbs per 1% duty cycle
Example:
  delval = 5 lbs   → 50% speed
  delval = 10 lbs  → 100% speed (at max)
  delval = 2 lbs   → 20% speed
```

## 🔧 Key Methods

Three new methods added to your application:

### `init_motor_driver()`
Runs at startup. Initializes GPIO and PWM.
- Sets up pins 23, 24, 25
- Creates PWM at 1000 Hz
- Logs status

### `control_motor(delval, max_duty=100.0)`
Controls motor speed and direction.
- **delval**: The delta value (positive=forward, negative=reverse)
- **max_duty**: Maximum speed limit (0-100%)
- **Example**: `app.control_motor(5.0)` runs motor forward at proportional speed

### `stop_motor()`
Safely stops motor and cleans up GPIO.
- Called automatically on shutdown
- Prevents GPIO errors on reboot
- **Example**: `app.stop_motor()` stops motor

## 🎚️ Customization

### Adjust Motor Sensitivity
Make motor more or less responsive:

**In `BLE_plus_serial.py`, find `control_motor()` method:**
```python
sensitivity = 10.0  # Modify this value
```

- **Lower value** (e.g., 5.0) = Motor responds faster to same delta
- **Higher value** (e.g., 20.0) = Motor responds slower to same delta

### Adjust Target Tolerance
Change when motor stops (currently 5 lbs):

**In `AutoSendLoop()` method:**
```python
if abs(delval) <= 5 and ...  # Change 5 to desired tolerance
```

### Limit Motor Maximum Speed
Cap motor speed during calibration:

**In `AutoSendLoop()` method:**
```python
self.control_motor(delval, max_duty=75.0)  # Limit to 75% speed
```

### Change GPIO Pins
If using different pins, edit constants at top of file:
```python
BTS7960_IN1 = 23   # Change to your IN1 pin
BTS7960_IN2 = 24   # Change to your IN2 pin
BTS7960_EN = 25    # Change to your EN pin
```

## 🛡️ Safety Features

✅ **Automatic stops**:
- When target reached (delta ≤ 5 lbs)
- On timeout (60 seconds)
- On application exit

✅ **Error handling**:
- Gracefully handles GPIO failures
- Continues if motor unavailable
- Logs all errors

✅ **Speed limiting**:
- Use `max_duty` parameter to limit speed
- Prevents runaway conditions
- Protects load

## 🐛 Troubleshooting

### Motor doesn't move
1. Run with `sudo`: `sudo python3 BLE_plus_serial.py`
2. Check connections match wiring diagram
3. Verify motor power supply is connected
4. Check terminal output for error messages

### Motor moves wrong direction
- **Option A**: Swap IN1 and IN2 connections
- **Option B**: Swap motor wire connections (OUT1 ↔ OUT2)

### Motor too slow/fast
1. Adjust sensitivity factor in `control_motor()` method
2. Test with new value
3. Find sweet spot for your application

### GPIO errors on startup
```bash
# Clean up previous GPIO session
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# Then try again
sudo python3 BLE_plus_serial.py
```

## 🧪 Testing

For comprehensive testing procedures, see **MOTOR_TESTING_GUIDE.md**:

1. **GPIO Access Test** - Verify hardware access
2. **Direction Test** - Verify motor moves correctly
3. **Speed Test** - Verify PWM speed control
4. **Integration Test** - Full application test
5. **Sensitivity Test** - Calibrate responsiveness
6. **Logging Test** - Debug motor behavior
7. **Safety Test** - Validate all stop conditions

## 📖 Read First

Before deploying, please read in this order:

1. **This file** (Getting_Started.md) - Overview
2. **WIRING_DIAGRAM.txt** - Hardware setup
3. **BTS7960_MOTOR_DRIVER.md** - Full documentation
4. **MOTOR_TESTING_GUIDE.md** - Testing procedures

## 💡 Pro Tips

1. **Test with low speeds first** using `max_duty=25.0` or similar
2. **Monitor terminal output** for debug information during testing
3. **Record your sensitivity calibration** value for future reference
4. **Never operate without mechanical feedback** (sensor reading)
5. **Use fused power supplies** to protect equipment
6. **Keep GPIO pins clear** of interference from motor power lines

## 🔗 Reference Links

- [38-3d.co.uk BTS7960 Guide](https://38-3d.co.uk/blogs/blog/using-the-bts7960-with-the-raspberry-pi)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)
- [BTS7960 Datasheet](https://www.ti.com/product/BTS7960B)

## 📞 Support

If you encounter issues:

1. **Check terminal output** for error messages
2. **Review troubleshooting** in BTS7960_MOTOR_DRIVER.md
3. **Run GPIO test** from MOTOR_TESTING_GUIDE.md
4. **Review wiring** in WIRING_DIAGRAM.txt
5. **Check code comments** in control_motor() method

## ✨ What's Included

**Modified Files:**
- `BLE_plus_serial.py` - Core application with motor control

**New Documentation:**
- `BTS7960_MOTOR_DRIVER.md` - Technical guide
- `WIRING_DIAGRAM.txt` - Hardware diagrams
- `motor_control_examples.py` - Code examples
- `MOTOR_TESTING_GUIDE.md` - Test procedures
- `INTEGRATION_SUMMARY.md` - Integration overview
- `Getting_Started.md` - This file

## 🎓 Learning Path

**Complete Beginner:**
1. Read Getting_Started.md (this file)
2. Review WIRING_DIAGRAM.txt
3. Connect hardware
4. Run application

**Intermediate:**
1. Run GPIO Access Test
2. Run Direction Test
3. Run Speed Test
4. Run Integration Test

**Advanced:**
1. Review motor_control_examples.py
2. Study control_motor() method
3. Implement custom control logic
4. Experiment with sensitivity tuning

## 🚨 Important Safety Notes

⚠️ **Always:**
- Run with `sudo` for GPIO access
- Use fused power supplies
- Test without mechanical load first
- Have emergency stop capability
- Never let motor stall under load
- Keep fingers away from moving parts

## 📝 Version Information

- **BTS7960 Motor Driver Support**: v1.0
- **Compatible with**: Raspberry Pi 3, 4, 5
- **GPIO Library**: RPi.GPIO
- **Python Version**: 3.6+
- **Installation**: Already integrated in your code

## 🎉 You're Ready!

Your motor control is fully integrated and ready to use!

**Next Steps:**
1. Set up hardware following WIRING_DIAGRAM.txt
2. Run the application: `sudo python3 BLE_plus_serial.py`
3. Test with AutoCal calibration
4. Run optional tests from MOTOR_TESTING_GUIDE.md
5. Fine-tune sensitivity for your application

---

**Happy motor controlling!** 🚀

For detailed technical information, see BTS7960_MOTOR_DRIVER.md
For testing procedures, see MOTOR_TESTING_GUIDE.md
For wiring details, see WIRING_DIAGRAM.txt

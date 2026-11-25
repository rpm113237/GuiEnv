# BTS7960 Motor Driver - Complete Documentation Index

## 🚀 Start Here

### Quick Start Guides (Read First)
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 5-minute developer cheat sheet
   - Setup instructions
   - Pin configuration
   - Code usage examples
   - Common issues

2. **[PIGPIO_SETUP.md](PIGPIO_SETUP.md)** - Hardware daemon installation
   - Install pigpio
   - Start daemon
   - Verify setup

---

## 📚 Complete Documentation

### Implementation Details
3. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Full technical reference
   - Hardware configuration details
   - Code implementation walkthrough
   - Integration explanation
   - Performance characteristics
   - Troubleshooting guide

4. **[BTS7960_MOTOR_DRIVER.md](BTS7960_MOTOR_DRIVER.md)** - Hardware specifications
   - Device datasheet summary
   - Pin descriptions
   - Electrical characteristics
   - Safety considerations

### Integration & Examples
5. **[motor_control_examples.py](motor_control_examples.py)** - 10 usage examples
   - Basic motor control
   - Reverse control
   - Speed limiting
   - Smooth ramp up
   - Controlled sequences
   - AutoSendLoop integration
   - Sensitivity tuning
   - Error handling
   - Emergency stop
   - PID-like control simulation

6. **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Integration details
   - How motor control fits into the app
   - AutoSendLoop modifications
   - API reference
   - Configuration options

### Testing & Validation
7. **[MOTOR_TESTING_GUIDE.md](MOTOR_TESTING_GUIDE.md)** - Testing procedures
   - Pre-test checklist
   - Basic functionality tests
   - Performance validation
   - Safety checks

### Wiring & Hardware
8. **[WIRING_DIAGRAM.txt](WIRING_DIAGRAM.txt)** - Pin connection diagram
   - Raspberry Pi GPIO pinout
   - BTS7960 pin assignments
   - Motor connections
   - Power requirements

---

## 🔧 Key Files in Codebase

### Main Application
- **[BLE_plus_serial.py](BLE_plus_serial.py)** - Main app with motor integration
  - Lines 702-737: `init_motor_driver()` - Initialization
  - Lines 739-776: `control_motor()` - Motor control logic
  - Lines 779-797: `stop_motor()` - Cleanup
  - Lines 380-415: `AutoSendLoop()` - Integration point

### Support Files
- **motor_control_examples.py** - Reference implementations
- **BLE_plus_serial_bk.py** - Backup of original

---

## 📋 Documentation Map

```
BTS7960 Motor Driver Documentation
│
├─ Quick Start
│  ├─ QUICK_REFERENCE.md ..................... 5-min cheat sheet
│  └─ PIGPIO_SETUP.md ....................... Installation guide
│
├─ Implementation
│  ├─ IMPLEMENTATION_SUMMARY.md ............. Technical details
│  ├─ BTS7960_MOTOR_DRIVER.md .............. Hardware specs
│  └─ motor_control_examples.py ............ 10 code examples
│
├─ Integration
│  ├─ INTEGRATION_SUMMARY.md ............... How it fits
│  └─ BLE_plus_serial.py ................... Main application
│
├─ Hardware
│  ├─ WIRING_DIAGRAM.txt ................... Pin connections
│  └─ MOTOR_TESTING_GUIDE.md ............... Test procedures
│
└─ This File
   └─ DOCUMENTATION_INDEX.md ............... You are here
```

---

## 🎯 Documentation by Use Case

### "I just want to get it working"
1. Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Follow: [PIGPIO_SETUP.md](PIGPIO_SETUP.md)
3. Run: [motor_control_examples.py](motor_control_examples.py) Example 1

### "I need to understand how it works"
1. Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. Study: [BTS7960_MOTOR_DRIVER.md](BTS7960_MOTOR_DRIVER.md)
3. Review: [motor_control_examples.py](motor_control_examples.py) all examples
4. Check: Code in [BLE_plus_serial.py](BLE_plus_serial.py) lines 702-797

### "I need to debug an issue"
1. Check: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) Troubleshooting section
2. Verify: Setup with [PIGPIO_SETUP.md](PIGPIO_SETUP.md)
3. Test: Steps in [MOTOR_TESTING_GUIDE.md](MOTOR_TESTING_GUIDE.md)
4. Reference: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) Troubleshooting

### "I need to modify the motor behavior"
1. Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) Sensitivity Tuning
2. Study: `control_motor()` method in [BLE_plus_serial.py](BLE_plus_serial.py)
3. Example: [motor_control_examples.py](motor_control_examples.py) Example 7
4. Reference: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) Sensitivity section

### "I need to integrate this into another project"
1. Review: [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)
2. Study: [motor_control_examples.py](motor_control_examples.py) Example 6
3. Copy: `init_motor_driver()`, `control_motor()`, `stop_motor()` from [BLE_plus_serial.py](BLE_plus_serial.py)
4. Configure: GPIO pins for your hardware
5. Test: Using [MOTOR_TESTING_GUIDE.md](MOTOR_TESTING_GUIDE.md)

---

## 📊 Document Statistics

| Document | Lines | Focus |
|----------|-------|-------|
| QUICK_REFERENCE.md | 197 | Setup & usage |
| IMPLEMENTATION_SUMMARY.md | 265 | Technical details |
| BTS7960_MOTOR_DRIVER.md | ~100 | Hardware specs |
| INTEGRATION_SUMMARY.md | ~100 | App integration |
| MOTOR_TESTING_GUIDE.md | ~80 | Testing |
| motor_control_examples.py | ~250 | Code examples |
| WIRING_DIAGRAM.txt | ~50 | Wiring |
| PIGPIO_SETUP.md | ~100 | Installation |

---

## 🔑 Key Concepts

### Hardware PWM (not Software PWM)
- **Why**: Precise frequency, lower CPU overhead, stable motor control
- **Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) section "Why Hardware PWM"
- **Config**: 1000 Hz frequency, GPIO 25 enable pin

### Motor Speed Calculation
- **Formula**: `speed = min(|delval| / sensitivity * 100, max_duty)`
- **Default**: sensitivity = 10.0 lbs per 1% duty
- **Tuning**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [motor_control_examples.py](motor_control_examples.py) Example 7

### Delta-Based Control
- **Concept**: Motor speed automatically adjusts based on weight difference
- **Calculation**: `delval = current_weight - target_weight`
- **Direction**: Positive = forward, Negative = reverse
- **Integration**: [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) or AutoSendLoop() method

### Error Handling
- **Strategy**: Graceful degradation if pigpio unavailable
- **Behavior**: Application continues, motor disabled
- **Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) Error Handling section

---

## ✅ Verification Checklist

Before deploying to production, verify:

- [ ] Read QUICK_REFERENCE.md
- [ ] Followed PIGPIO_SETUP.md
- [ ] Reviewed WIRING_DIAGRAM.txt
- [ ] Completed MOTOR_TESTING_GUIDE.md
- [ ] Understood IMPLEMENTATION_SUMMARY.md
- [ ] Reviewed motor_control_examples.py
- [ ] Tested AutoSendLoop() with real hardware
- [ ] Verified error handling behavior
- [ ] Checked daemon startup on boot
- [ ] Documented any custom modifications

---

## 🔗 External References

### pigpio Documentation
- Official: http://abyz.me.uk/rpi/pigpio/
- Python: http://abyz.me.uk/rpi/pigpio/python.html

### BTS7960 Hardware
- Reference: https://38-3d.co.uk/blogs/blog/using-the-bts7960-with-the-raspberry-pi
- Datasheet: Included in [BTS7960_MOTOR_DRIVER.md](BTS7960_MOTOR_DRIVER.md)

### Raspberry Pi GPIO
- Pinout: https://pinout.xyz/
- GPIO Documentation: https://www.raspberrypi.org/documentation/

---

## 📝 Notes

- All GPIO pins use BCM (Broadcom) numbering, not physical pin numbers
- Hardware PWM available on GPIO 12, 13, 18, 19 (this uses GPIO 25 as general PWM pin via pigpio)
- pigpio daemon must be running for motor control to work
- Motor control fails gracefully if daemon is unavailable
- Sensitivity factor (10.0) is easily adjustable for different loads

---

## 🎓 Learning Path

**Beginner** (New to this project):
1. QUICK_REFERENCE.md
2. WIRING_DIAGRAM.txt
3. PIGPIO_SETUP.md
4. motor_control_examples.py (Examples 1-3)

**Intermediate** (Want to modify behavior):
1. IMPLEMENTATION_SUMMARY.md
2. INTEGRATION_SUMMARY.md
3. motor_control_examples.py (Examples 4-7)
4. BLE_plus_serial.py (Lines 702-797)

**Advanced** (Need to extend/integrate):
1. BTS7960_MOTOR_DRIVER.md
2. MOTOR_TESTING_GUIDE.md
3. motor_control_examples.py (Examples 8-10)
4. Full BLE_plus_serial.py code review

---

## 📞 Support & Troubleshooting

For common issues:
1. First: Check QUICK_REFERENCE.md Troubleshooting section
2. Then: Review MOTOR_TESTING_GUIDE.md
3. Finally: See IMPLEMENTATION_SUMMARY.md Troubleshooting section

For specific scenarios:
- Motor not responding → Check WIRING_DIAGRAM.txt and PIGPIO_SETUP.md
- Incorrect speed → Review QUICK_REFERENCE.md Sensitivity Tuning
- High CPU usage → Verify pigpio hardware PWM in IMPLEMENTATION_SUMMARY.md
- Integration issues → Study INTEGRATION_SUMMARY.md

---

## 📄 Document Versions

All documents updated: 2024
Implementation Status: ✅ Production Ready
Motor Driver: BTS7960
Control Method: pigpio Hardware PWM (1000 Hz)
Integration Status: Fully integrated in AutoSendLoop

---

**Navigation**: [Home](README.md) | [Docs](#) | [Examples](motor_control_examples.py) | [Wiring](WIRING_DIAGRAM.txt)

---

*Last Updated: 2024*
*Status: Complete and Production Ready* ✅

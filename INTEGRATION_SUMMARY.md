# BTS7960 Motor Driver - Integration Summary

## What Was Added

The BTS7960 PWM motor driver has been fully integrated into your `BLE_plus_serial.py` application. The motor is now automatically controlled during the `AutoSendLoop` calibration sequence based on the delta value between the sensor reading and target.

## Files Modified

### Main Application
- **`BLE_plus_serial.py`** - Core integration
  - Added RPi.GPIO import and initialization
  - Added `BTS7960_IN1`, `BTS7960_IN2`, `BTS7960_EN` pin constants
  - Added motor initialization in `__init__` method
  - Added three motor control methods
  - Modified `AutoSendLoop` to control motor
  - Modified `close_app` to safely stop motor

## Files Created

### Documentation
1. **`BTS7960_MOTOR_DRIVER.md`** - Complete user guide
   - Hardware setup and wiring
   - Motor control behavior
   - Pin configuration
   - Code integration details
   - Troubleshooting guide
   - Customization options
   - Safety considerations

2. **`motor_control_examples.py`** - Usage examples
   - 10 different usage patterns
   - Basic to advanced control
   - Integration examples
   - Sensitivity tuning guide
   - Error handling
   - PID-like control simulation

3. **`MOTOR_TESTING_GUIDE.md`** - Testing procedures
   - 7 comprehensive tests
   - Step-by-step instructions
   - GPIO validation
   - Direction verification
   - Speed calibration
   - Integration testing
   - Safety checklist

4. **`INTEGRATION_SUMMARY.md`** - This file

## Key Features Implemented

### Motor Control Methods

#### `init_motor_driver()`
- Initializes GPIO pins (23, 24, 25)
- Creates PWM object at 1000 Hz
- Handles errors gracefully if GPIO unavailable
- Logs initialization status

#### `control_motor(delval, max_duty=100.0)`
- Controls motor based on delta value
- Forward when delval > 0
- Reverse when delval < 0
- Stop when delval ≈ 0
- Speed proportional to |delval|
- Includes debug logging
- Error handling and fallback

#### `stop_motor()`
- Safely stops motor
- Cleans up GPIO resources
- Called during application shutdown

### Integration Points

1. **AutoSendLoop Enhancement**
   - Motor activated during calibration
   - Speed adjusts with sensor delta
   - Automatic stop at target tolerance
   - Emergency stop on timeout

2. **Application Lifecycle**
   - Motor initialized at startup
   - Motor stopped at shutdown
   - Graceful error handling throughout

## Hardware Configuration

```
Raspberry Pi GPIO          BTS7960 Driver          Motor
├── GPIO 23 (IN1)   ────→  IN1
├── GPIO 24 (IN2)   ────→  IN2
├── GPIO 25 (EN)    ────→  EN (PWM)
├── GND             ────→  GND
└── +5V             ────→  Power (if needed)

BTS7960 Output:
├── OUT1  ────→  Motor +
└── OUT2  ────→  Motor -
```

**To adjust pin assignments**, edit these constants in `BLE_plus_serial.py`:
```python
BTS7960_IN1 = 23   # Change to your IN1 pin
BTS7960_IN2 = 24   # Change to your IN2 pin
BTS7960_EN = 25    # Change to your EN pin
```

## Motor Behavior

### Forward Direction
- When `SF` (Sensor Force) > `TGT` (Target)
- Motor runs forward at speed proportional to overage

### Reverse Direction
- When `SF` < `TGT`
- Motor runs reverse to increase sensor reading

### Stop Conditions
1. Target reached (delta ≤ 5 lbs tolerance)
2. Timeout expires (60 seconds default)
3. AutoSendLoop completes
4. Application closes

### Speed Mapping
```
speed_percent = min(|delval| / sensitivity * 100, max_duty)

Default sensitivity: 10.0 lbs per 1% duty
Example: delval=5 lbs → 50% speed
         delval=10 lbs → 100% speed (capped)
```

## Quick Start

### 1. Connect Hardware
- Wire BTS7960 to GPIO pins 23, 24, 25
- Connect motor to BTS7960 OUT1/OUT2
- Provide adequate power to motor and driver

### 2. Run Application
```bash
cd /home/rpm/GuiEnv
sudo python3 BLE_plus_serial.py
```

### 3. Start Calibration
- Set calibration parameters (Start, Step, Num Steps)
- Click "Start AutoCal"
- Watch motor move as calibration progresses

### 4. Verify Operation
- Check terminal output for initialization message
- Confirm motor direction matches sensor overshoot/undershoot
- Verify motor stops at target tolerance

## Testing

See `MOTOR_TESTING_GUIDE.md` for detailed testing procedures:

1. GPIO Access Check
2. Motor Direction Test
3. PWM Speed Control Test
4. Integration Test
5. Sensitivity Calibration
6. Logging and Debugging
7. Safety Validation

## Customization Options

### Adjust Motor Sensitivity
Edit `control_motor()` method:
```python
sensitivity = 10.0  # Modify this value (lower = faster response)
```

### Adjust Target Tolerance
Edit `AutoSendLoop()` method:
```python
if abs(delval) <= 5 and ...  # Change 5 to desired tolerance
```

### Change PWM Frequency
Edit constant at top of file:
```python
BTS7960_PWM_FREQ = 1000  # Modify frequency in Hz
```

### Limit Motor Speed
Call with custom max_duty:
```python
self.control_motor(delval, max_duty=75.0)  # Limit to 75%
```

## Troubleshooting

### Motor Not Moving
1. Run as root: `sudo python3 BLE_plus_serial.py`
2. Check GPIO connections
3. Verify power to motor and driver
4. Review terminal output for errors

### Motor Wrong Direction
- Swap IN1 and IN2 connections, or
- Swap motor wire connections

### Motor Speed Not Responding
- Adjust sensitivity value in `control_motor()`
- Check PWM frequency setting
- Verify motor power supply

### GPIO Errors
- Ensure only one app accessing GPIO
- Clean up previous GPIO: `python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"`

## Code Structure

### New Methods Added to AsyncScannerApp
```
init_motor_driver()
├── GPIO setup
├── Pin configuration
└── PWM initialization

control_motor(delval, max_duty)
├── Direction control (IN1, IN2)
├── Speed calculation
└── PWM duty cycle adjustment

stop_motor()
├── Stop PWM
├── Set pins to LOW
└── GPIO cleanup
```

### Modified Methods
```
__init__()
└── Added motor initialization

AutoSendLoop()
└── Added motor control calls during calibration

close_app()
└── Added motor cleanup on shutdown
```

## Safety Features

✓ Graceful error handling if GPIO unavailable
✓ Automatic motor stop on timeout
✓ Automatic motor stop at target tolerance
✓ Motor cleanup on application exit
✓ Debug logging for troubleshooting
✓ Speed limiting capability (max_duty parameter)
✓ Emergency stop via `control_motor(0)`

## Performance Notes

- Motor updates: Every 500ms during AutoSendLoop
- PWM frequency: 1000 Hz (suitable for most DC motors)
- GPIO operations: Non-blocking, async-safe
- Logging: DEBUG level (not shown by default)
- Error handling: Exceptions logged, app continues

## References

- [38-3d.co.uk BTS7960 Guide](https://38-3d.co.uk/blogs/blog/using-the-bts7960-with-the-raspberry-pi)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)
- [BTS7960 Datasheet](https://www.ti.com/product/BTS7960B)

## Support Files

- **BTS7960_MOTOR_DRIVER.md** - Detailed technical documentation
- **motor_control_examples.py** - Usage patterns and examples
- **MOTOR_TESTING_GUIDE.md** - Comprehensive testing procedures
- **INTEGRATION_SUMMARY.md** - This quick reference

## Next Steps

1. Review `BTS7960_MOTOR_DRIVER.md` for detailed setup
2. Run GPIO test from `MOTOR_TESTING_GUIDE.md`
3. Connect hardware following wiring diagram
4. Test motor control with provided examples
5. Calibrate sensitivity for your application
6. Run full integration test with application
7. Perform safety validation before deployment

## Questions or Issues?

Refer to the troubleshooting section in `BTS7960_MOTOR_DRIVER.md` or review the testing procedures in `MOTOR_TESTING_GUIDE.md`.

Good luck with your project! 🚀

# BTS7960 Motor Driver Integration Guide

## Overview
The BTS7960 PWM motor driver has been integrated into the `BLE_plus_serial.py` application. The motor is automatically controlled during the `AutoSendLoop` based on the delta value (`delval`) between the current sensor reading (SF) and target value (TGT).

## Hardware Setup

### Pin Configuration (GPIO BCM Numbering)
The following GPIO pins are used to control the BTS7960 motor driver:

| Component | GPIO Pin | Function |
|-----------|----------|----------|
| IN1 | GPIO 23 | Direction Control 1 |
| IN2 | GPIO 24 | Direction Control 2 |
| EN  | GPIO 25 | PWM Speed Control (Enable) |

**To adjust pin assignments**, edit the constants at the top of `BLE_plus_serial.py`:
```python
BTS7960_IN1 = 23  # GPIO 23 - Control direction
BTS7960_IN2 = 24  # GPIO 24 - Control direction
BTS7960_EN = 25   # GPIO 25 - PWM for speed control (enable)
BTS7960_PWM_FREQ = 1000  # PWM frequency in Hz
```

### Wiring Diagram
```
Raspberry Pi              BTS7960 Motor Driver
─────────────            ─────────────────────
GPIO 23 (IN1)  ────────→ IN1
GPIO 24 (IN2)  ────────→ IN2
GPIO 25 (EN)   ────────→ EN (PWM)
GND            ────────→ GND

Motor connections:
Motor+ ────────→ OUT1
Motor- ────────→ OUT2
```

## Motor Control Behavior

### Direction Control
The motor direction is controlled by IN1 and IN2 pins:
- **Forward**: IN1=HIGH, IN2=LOW (when delval > 0)
- **Reverse**: IN1=LOW, IN2=HIGH (when delval < 0)
- **Stop**: IN1=LOW, IN2=LOW (when delval ≈ 0)

### Speed Control
Motor speed is controlled via PWM on the EN pin. The speed is mapped from the delta value:

```
speed_percent = min(|delval| / sensitivity * 100, max_duty)
```

**Default sensitivity**: 10.0 lbs per 1% duty cycle
- To increase motor responsiveness: **lower** the sensitivity value
- To decrease motor responsiveness: **increase** the sensitivity value

For example:
- If `delval = 5` and `sensitivity = 10.0`: speed = 50% duty cycle
- If `delval = 15` and `sensitivity = 10.0`: speed = 100% (capped by max_duty)

### AutoSendLoop Operation
During calibration, the motor will:
1. **Start** when delval exceeds the threshold
2. **Run forward/reverse** depending on sign of delval
3. **Adjust speed** proportionally to delval magnitude
4. **Stop automatically** when:
   - Target is reached (delval ≤ 5 lbs)
   - Timeout occurs (60 seconds)
   - Loop completes

## Code Integration

### Key Methods Added

#### `init_motor_driver()`
Initializes GPIO pins and creates PWM object. Called during app startup.
- Sets BCM pin numbering
- Configures IN1, IN2, EN as outputs
- Creates PWM at 1000 Hz on EN pin

#### `control_motor(delval, max_duty=100.0)`
Controls motor based on delta value.
- **Parameters**:
  - `delval`: Delta value (SF - TGT). Positive=forward, Negative=reverse
  - `max_duty`: Maximum PWM duty cycle (0-100). Default=100%
- **Returns**: None
- **Logging**: Debug messages show motor state and speed

#### `stop_motor()`
Safely stops the motor and cleans up GPIO resources.
- Sets all pins to LOW
- Stops PWM
- Calls GPIO.cleanup()

### Modified Methods

#### `AutoSendLoop()`
Added motor control calls:
```python
# Calculate delval as before
delval = float(self.SF_lbl.cget("text").split(':')[1]) - float(self.TGT_lbl.cget("text").split(':')[1])

# Control motor based on delval
self.control_motor(delval, max_duty=100.0)

# Stop motor when target reached or timeout occurs
self.control_motor(0)
```

#### `close_app()`
Now calls `stop_motor()` to ensure clean shutdown:
```python
def close_app(self):
    self.stop_motor()  # Clean motor shutdown
    self.is_running = False
    self.destroy()
```

## Troubleshooting

### Motor Not Moving
1. **Check GPIO permissions**: Run with `sudo` on Raspberry Pi
2. **Verify pin connections**: Use `gpio readall` to test GPIO functionality
3. **Check logging output**: Look for initialization errors
4. **Enable debug logging**: Change logging level to DEBUG for verbose output

### Motor Moving in Wrong Direction
- Swap IN1 and IN2 connections, or
- Swap motor wire connections (Motor+ and Motor-)

### Motor Speed Not Responding
1. **Adjust sensitivity factor** in `control_motor()` method
2. **Check PWM frequency** (default 1000 Hz)
3. **Verify max_duty parameter** is not too low

### GPIO Errors on Startup
- Ensure only one application is accessing GPIO at a time
- If previous run crashed, manually clean GPIO: `python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"`

## Customization

### Adjust Motor Sensitivity
Edit the `control_motor()` method:
```python
sensitivity = 10.0  # Modify this value
speed_percent = min(abs(delval) / sensitivity * 100, max_duty)
```

### Adjust Target Tolerance
Edit the `AutoSendLoop()` method:
```python
if abs(delval) <= 5 and ...  # Change 5 to desired tolerance
```

### Adjust Maximum Duty Cycle
Call with custom max_duty:
```python
self.control_motor(delval, max_duty=75.0)  # Limit to 75% speed
```

### Change PWM Frequency
Edit the constant at top of file:
```python
BTS7960_PWM_FREQ = 1000  # Change to desired frequency (Hz)
```

## Safety Considerations

1. **Always test with low speeds first** using small max_duty values
2. **Never operate motor without mechanical load feedback**
3. **Use emergency stop button** to halt motor if needed
4. **Proper power supply**: Ensure adequate current capacity for motor
5. **Keep GPIO configuration consistent** across reboots

## Example Usage

```python
# Manual motor control (outside AutoSendLoop)
app.control_motor(5.0)   # Forward at proportional speed
app.control_motor(-3.0)  # Reverse at proportional speed
app.control_motor(0)     # Stop motor

# With speed limit
app.control_motor(10.0, max_duty=50.0)  # Limited to 50% speed
```

## Performance Notes

- Motor updates occur every 500ms in AutoSendLoop
- PWM frequency: 1000 Hz (suitable for most DC motors)
- GPIO operations are non-blocking
- Motor control logging uses DEBUG level (not shown by default)

## References
- [38-3d.co.uk BTS7960 Guide](https://38-3d.co.uk/blogs/blog/using-the-bts7960-with-the-raspberry-pi)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)
- [BTS7960 Datasheet](https://www.ti.com/product/BTS7960B)

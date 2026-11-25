"""
BTS7960 Motor Driver Testing Guide
Step-by-step instructions to test motor control functionality
"""

# ============================================================================
# QUICK TEST: Verify GPIO Pin Functionality
# ============================================================================

GPIO_TEST = """
# Run on Raspberry Pi to verify GPIO pins are accessible
$ gpio readall

# This will show all GPIO pins and their current state
# Verify pins 23, 24, 25 are listed and accessible
"""

# ============================================================================
# TEST 1: GPIO Access Check
# ============================================================================

TEST_1_GPIO_ACCESS = """
#!/usr/bin/env python3
# Verify GPIO module loads and pins can be configured

import RPi.GPIO as GPIO
import logging

logging.basicConfig(level=logging.INFO)

BTS7960_IN1 = 23
BTS7960_IN2 = 24
BTS7960_EN = 25

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    print("Setting up GPIO pins...")
    GPIO.setup(BTS7960_IN1, GPIO.OUT)
    GPIO.setup(BTS7960_IN2, GPIO.OUT)
    GPIO.setup(BTS7960_EN, GPIO.OUT)
    
    print("✓ GPIO pins 23, 24, 25 configured successfully")
    
    # Test setting pins
    print("Testing pin outputs...")
    GPIO.output(BTS7960_IN1, GPIO.HIGH)
    print("✓ GPIO 23 (IN1) set HIGH")
    
    GPIO.output(BTS7960_IN2, GPIO.HIGH)
    print("✓ GPIO 24 (IN2) set HIGH")
    
    GPIO.output(BTS7960_IN1, GPIO.LOW)
    GPIO.output(BTS7960_IN2, GPIO.LOW)
    print("✓ All pins reset to LOW")
    
    # Test PWM
    print("Testing PWM...")
    pwm = GPIO.PWM(BTS7960_EN, 1000)
    pwm.start(0)
    print("✓ PWM initialized at 1000 Hz")
    
    pwm.ChangeDutyCycle(50)
    print("✓ PWM duty cycle set to 50%")
    
    pwm.stop()
    GPIO.cleanup()
    print("✓ Cleanup successful")
    
except Exception as e:
    print(f"✗ Error: {e}")
    GPIO.cleanup()
"""

# ============================================================================
# TEST 2: Motor Direction Test
# ============================================================================

TEST_2_MOTOR_DIRECTION = """
#!/usr/bin/env python3
# Test motor direction control

import RPi.GPIO as GPIO
import time

BTS7960_IN1 = 23
BTS7960_IN2 = 24
BTS7960_EN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BTS7960_IN1, GPIO.OUT)
GPIO.setup(BTS7960_IN2, GPIO.OUT)
GPIO.setup(BTS7960_EN, GPIO.OUT)

pwm = GPIO.PWM(BTS7960_EN, 1000)
pwm.start(0)

try:
    # Test Forward
    print("Testing FORWARD direction...")
    GPIO.output(BTS7960_IN1, GPIO.HIGH)
    GPIO.output(BTS7960_IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(50)
    print("  Motor should move FORWARD at 50% speed")
    time.sleep(2)
    
    # Test Reverse
    print("Testing REVERSE direction...")
    GPIO.output(BTS7960_IN1, GPIO.LOW)
    GPIO.output(BTS7960_IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(50)
    print("  Motor should move REVERSE at 50% speed")
    time.sleep(2)
    
    # Test Stop
    print("Testing STOP...")
    GPIO.output(BTS7960_IN1, GPIO.LOW)
    GPIO.output(BTS7960_IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)
    print("  Motor should stop")
    time.sleep(1)
    
    print("✓ Direction test complete")
    
finally:
    pwm.stop()
    GPIO.cleanup()
"""

# ============================================================================
# TEST 3: PWM Speed Control Test
# ============================================================================

TEST_3_PWM_SPEED = """
#!/usr/bin/env python3
# Test PWM speed control (0-100% duty cycle)

import RPi.GPIO as GPIO
import time

BTS7960_IN1 = 23
BTS7960_IN2 = 24
BTS7960_EN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BTS7960_IN1, GPIO.OUT)
GPIO.setup(BTS7960_IN2, GPIO.OUT)
GPIO.setup(BTS7960_EN, GPIO.OUT)

GPIO.output(BTS7960_IN1, GPIO.HIGH)  # Forward
GPIO.output(BTS7960_IN2, GPIO.LOW)

pwm = GPIO.PWM(BTS7960_EN, 1000)
pwm.start(0)

try:
    print("Testing PWM duty cycle from 0% to 100%...")
    
    for duty in range(0, 101, 10):
        pwm.ChangeDutyCycle(duty)
        print(f"  Duty cycle: {duty}% (should be proportionally faster)")
        time.sleep(1)
    
    print("✓ Speed test complete")
    
finally:
    pwm.stop()
    GPIO.cleanup()
"""

# ============================================================================
# TEST 4: Integration Test with Application
# ============================================================================

TEST_4_INTEGRATION = """
Step-by-step integration test:

1. Run the main application:
   $ sudo python3 BLE_plus_serial.py

2. Watch the terminal output for:
   "BTS7960 motor driver initialized successfully"

3. Trigger the AutoSendLoop calibration:
   - Set Start, Step, and Num Steps values
   - Click "Start AutoCal" button

4. During AutoSendLoop, observe:
   - Terminal messages showing delval values
   - Motor spinning/reversing based on delval
   - Motor speed changing as delval changes
   - Motor stopping when target reached

5. Expected behavior:
   - Motor starts when delval increases
   - Forward/Reverse direction matches sensor overshoot/undershoot
   - Motor stops at ~5 lbs tolerance
   - Motor stops on timeout
   - No errors in log output

6. If motor doesn't move:
   - Check GPIO pin connections
   - Verify power supply to motor and driver
   - Check terminal for error messages
   - Review troubleshooting section in BTS7960_MOTOR_DRIVER.md
"""

# ============================================================================
# TEST 5: Sensitivity Calibration
# ============================================================================

TEST_5_SENSITIVITY_CALIBRATION = """
How to calibrate motor sensitivity for your application:

1. Record baseline behavior with default sensitivity (10.0):
   - Note how fast motor responds to small delval changes
   - Note maximum speed at max delval
   
2. If motor is too slow:
   - Decrease sensitivity value (e.g., 10.0 → 5.0)
   - Run test again
   - Repeat until satisfied
   
3. If motor is too fast:
   - Increase sensitivity value (e.g., 10.0 → 15.0)
   - Run test again
   - Repeat until satisfied

4. Update the sensitivity value in control_motor() method:
   
   def control_motor(self, delval: float, max_duty: float = 100.0):
       # ...
       sensitivity = 5.0  # Adjust this for your load/motor combo
       speed_percent = min(abs(delval) / sensitivity * 100, max_duty)

5. Test with realistic load and sensor readings

Formula:
  speed_percent = min(|delval| / sensitivity * 100, max_duty)
  
Example calculations:
  - delval=5, sensitivity=10 → speed=50%
  - delval=10, sensitivity=10 → speed=100% (capped)
  - delval=5, sensitivity=5 → speed=100% (capped)
  - delval=5, sensitivity=20 → speed=25%
"""

# ============================================================================
# TEST 6: Logging and Debugging
# ============================================================================

TEST_6_LOGGING = """
Enable detailed logging to debug motor behavior:

1. In BLE_plus_serial.py, change logging level to DEBUG:
   logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")

2. Run application:
   $ sudo python3 BLE_plus_serial.py 2>&1 | tee motor_debug.log

3. Trigger AutoSendLoop and observe output:
   - "[DEBUG] Motor forward at 50.0% duty (delval=5.00)"
   - "[DEBUG] Motor reverse at 25.0% duty (delval=-2.50)"
   - "[DEBUG] Motor stopped (delval=0)"
   - "[INFO] BTS7960 motor driver initialized successfully"
   - "[ERROR] Error controlling motor: ..." (if any)

4. Save log file for analysis:
   $ grep -i motor motor_debug.log > motor_activity.log

5. Analyze motor commands:
   - Look for unexpected direction changes
   - Check for intermittent errors
   - Verify speed changes correlate with delval
"""

# ============================================================================
# TEST 7: Safety Test
# ============================================================================

TEST_7_SAFETY = """
Safety validation checklist:

□ Motor never moves unexpectedly on startup
□ Motor stops when application exits gracefully
□ Motor stops when AutoSendLoop completes
□ Motor stops on timeout (60 seconds)
□ Motor never starts without delval command
□ Emergency stop (control_motor(0)) works immediately
□ GPIO is properly cleaned up after each run
□ No motor movement at 0% duty cycle
□ Motor direction matches sensor feedback
□ Speed is proportional to delval magnitude

Before deployment:
□ Test with actual mechanical load
□ Test emergency stop multiple times
□ Verify motor never stalls for extended periods
□ Check power supply voltage/current rating
□ Verify all wires are secure
□ Test GPIO functionality after each power cycle
"""

# ============================================================================
# RUNNING THE TESTS
# ============================================================================

EXECUTION_ORDER = """
Recommended test execution order:

1. GPIO Access Check (TEST_1)
   - Verifies hardware access
   - Run with: sudo python3 test_gpio_access.py
   
2. Motor Direction Test (TEST_2)
   - Verifies motor moves in correct directions
   - Requires motor mechanically free to move
   - Run with: sudo python3 test_motor_direction.py
   
3. PWM Speed Control Test (TEST_3)
   - Verifies speed changes with PWM
   - Should hear motor pitch change
   - Run with: sudo python3 test_pwm_speed.py
   
4. Integration Test (TEST_4)
   - Tests complete application flow
   - Set realistic calibration parameters
   - Run with: sudo python3 BLE_plus_serial.py
   
5. Sensitivity Calibration (TEST_5)
   - Fine-tune motor responsiveness
   - Adapt to your specific load
   - Modify control_motor() sensitivity value
   
6. Logging and Debugging (TEST_6)
   - Capture detailed behavior
   - Save logs for analysis
   - Useful for troubleshooting
   
7. Safety Test (TEST_7)
   - Verify no dangerous behaviors
   - Test all stop conditions
   - Final validation before production
"""

if __name__ == "__main__":
    print("BTS7960 Motor Control Testing Guide")
    print("\nAvailable tests:")
    print("  TEST_1: GPIO Access Check")
    print("  TEST_2: Motor Direction Test")
    print("  TEST_3: PWM Speed Control Test")
    print("  TEST_4: Integration Test")
    print("  TEST_5: Sensitivity Calibration")
    print("  TEST_6: Logging and Debugging")
    print("  TEST_7: Safety Test")
    print("\nSee source for detailed test procedures")
    print("\nTo run a test, extract the code and execute with:")
    print("  sudo python3 test_script.py")

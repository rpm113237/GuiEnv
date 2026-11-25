"""
BTS7960 Motor Control Examples
Examples showing how to use the motor control functions
"""

import asyncio
import logging

# Note: These are reference examples. In practice, use the methods
# integrated into AsyncScannerApp class.

# Configure logging to see motor debug messages
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")

class MotorControlExamples:
    """Example usage patterns for BTS7960 motor control"""

    def example_1_basic_control(self, app):
        """Example 1: Basic motor control based on delta value"""
        delval = 15.0  # 15 lbs difference
        
        # Motor will move forward at proportional speed
        app.control_motor(delval)

    def example_2_reverse_control(self, app):
        """Example 2: Reverse motor control"""
        delval = -8.0  # -8 lbs difference (overshoot)
        
        # Motor will move reverse at proportional speed
        app.control_motor(delval)

    def example_3_speed_limited(self, app):
        """Example 3: Control motor with speed limit"""
        delval = 25.0
        
        # Motor limited to 50% maximum speed
        app.control_motor(delval, max_duty=50.0)

    def example_4_smooth_ramp_up(self, app):
        """Example 4: Gradually increase motor speed"""
        async def ramp_speed():
            for speed_target in range(0, 100, 10):
                # Simulate delval by scaling from 0 to 25 lbs
                delval = (speed_target / 100.0) * 25.0
                app.control_motor(delval)
                await asyncio.sleep(0.5)
            
            # Stop motor
            app.control_motor(0)
        
        return asyncio.create_task(ramp_speed())

    def example_5_controlled_sequence(self, app):
        """Example 5: Sequence of motor operations"""
        async def sequence():
            # Forward at full speed
            app.control_motor(10.0, max_duty=100.0)
            await asyncio.sleep(2)
            
            # Slow down
            app.control_motor(10.0, max_duty=50.0)
            await asyncio.sleep(2)
            
            # Reverse
            app.control_motor(-5.0)
            await asyncio.sleep(1)
            
            # Stop
            app.control_motor(0)
        
        return asyncio.create_task(sequence())

    def example_6_autosendloop_integration(self):
        """Example 6: How motor control integrates in AutoSendLoop"""
        # This shows the actual integration in AutoSendLoop
        
        code_snippet = """
        async def AutoSendLoop(self):
            for i in range(int(self.autocal_numstep_ent.get())):
                # ... set target value ...
                
                while True:
                    # Get current delta
                    delval = float(self.SF_lbl.cget("text").split(':')[1]) - \
                             float(self.TGT_lbl.cget("text").split(':')[1])
                    
                    # MOTOR CONTROL: Automatically adjust speed based on delval
                    self.control_motor(delval, max_duty=100.0)
                    
                    # Check if target reached
                    if abs(delval) <= 5:
                        # MOTOR STOP: Stop when target reached
                        self.control_motor(0)
                        break
                    
                    # Check timeout
                    if elapsed > timeout:
                        # MOTOR STOP: Stop on timeout
                        self.control_motor(0)
                        break
                    
                    await asyncio.sleep(0.5)
        """
        
        return code_snippet

    def example_7_sensitivity_tuning(self):
        """Example 7: How to adjust motor sensitivity"""
        
        tuning_guide = {
            "sensitivity_factor": 10.0,  # Default: lbs per 1% duty cycle
            
            "scenarios": {
                "fast_response": {
                    "value": 5.0,
                    "effect": "Motor runs faster for same delval",
                    "use_case": "Light loads, quick adjustments"
                },
                "slow_response": {
                    "value": 20.0,
                    "effect": "Motor runs slower for same delval",
                    "use_case": "Heavy loads, precise control"
                },
                "medium_response": {
                    "value": 10.0,
                    "effect": "Balanced speed response",
                    "use_case": "Default, general purpose"
                }
            },
            
            "adjustment": """
            In control_motor() method:
            sensitivity = 10.0  # Modify this value
            speed_percent = min(abs(delval) / sensitivity * 100, max_duty)
            """
        }
        
        return tuning_guide

    def example_8_error_handling(self, app):
        """Example 8: Error handling for motor control"""
        try:
            # This will safely handle errors if GPIO not available
            app.control_motor(10.0)
        except Exception as e:
            logging.error(f"Motor control error: {e}")
            # Application continues even if motor unavailable

    def example_9_emergency_stop(self, app):
        """Example 9: Emergency stop"""
        # Immediately stop motor
        app.control_motor(0)
        
        # For complete shutdown (cleanup GPIO)
        app.stop_motor()

    def example_10_pid_control_simulation(self, app):
        """Example 10: Simulated PID-like control"""
        async def pid_control_loop():
            kp = 5.0  # Proportional gain
            target = 50.0
            
            for _ in range(100):  # 50 seconds at 500ms intervals
                current = 45.0  # Simulated current value
                error = target - current
                
                # PID output (simplified - proportional only)
                pid_output = kp * error
                
                # Motor responds to error
                app.control_motor(pid_output)
                
                await asyncio.sleep(0.5)
            
            app.control_motor(0)
        
        return asyncio.create_task(pid_control_loop())


# Usage instructions:
# 1. Import this module in your application
# 2. Create an instance of MotorControlExamples
# 3. Call example methods, passing the app instance
# 4. Examples show different control patterns
# 5. Adapt examples to your specific needs

if __name__ == "__main__":
    print("BTS7960 Motor Control Examples")
    print("See docstrings for detailed usage information")
    
    examples = MotorControlExamples()
    
    # Print all example descriptions
    for attr in dir(examples):
        if attr.startswith("example_"):
            method = getattr(examples, attr)
            print(f"\n{attr}: {method.__doc__}")

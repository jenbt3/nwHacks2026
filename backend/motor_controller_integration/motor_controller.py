import serial
import time

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

class MotorBridge:
    def __init__(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            time.sleep(2) # Wait for Arduino reset
            self.ser.flush()
            print("Connected to Arduino Servo Bridge")
        except:
            print("Warning: Arduino not found. Motor commands will be ignored.")
            self.ser = None

    def process_joystick(self, angle, force):
        """Maps 0-360 degrees to F/B commands for the stepper"""
        if not self.ser or force < 0.5: # Ignore small movements (deadzone)
            return

        # Determine direction based on joystick angle
        # Right (0 deg) -> 'F', Left (180 deg) -> 'B'
        command_dir = None
        
        if (angle >= 0 and angle <= 45) or (angle >= 315 and angle <= 360):
            command_dir = 'F'
        elif (angle >= 135 and angle <= 225):
            command_dir = 'B'

        if command_dir:
            # Map force (0 to ~3) to number of steps (e.g., 50 to 150)
            steps = int(force * 50)
            self.send_to_arduino(command_dir, steps)

    def send_to_arduino(self, direction, steps):
        if self.ser:
            cmd = f"{direction},{steps}\n"
            self.ser.write(cmd.encode())
            # We don't wait for "DONE" here to keep the video feed smooth
            # But we flush to ensure immediate movement
            self.ser.flush()

# Global instance for the FastAPI app to use
motor_bridge = MotorBridge()
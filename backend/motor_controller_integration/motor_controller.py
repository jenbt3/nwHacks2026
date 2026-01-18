import serial
import time
import logging

logger = logging.getLogger("motor_bridge")

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

class MotorBridge:
    def __init__(self):
        self.ser = None
        self.last_cmd_time = 0
        self.cmd_interval = 0.05  # 20Hz rate limit to match Arduino processing speed
        
        try:
            # Open port with timeout=0 for non-blocking writes
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)
            time.sleep(2) # Wait for Arduino bootloader reset
            self.ser.flush()
            logger.info("Connected to Arduino Single-Axis Bridge")
        except Exception as e:
            logger.error(f"Motor Hardware Error: {e}")
            logger.warning("Joystick commands will be ignored for this session.")

    def process_joystick(self, angle, force):
        """
        Maps 360-degree joystick movement to 1-axis 'F' and 'B' commands.
        """
        if not self.ser:
            return

        # Stop logic: If force is near zero, don't send commands
        if force < 0.1:
            return

        # Rate limiting to prevent serial buffer congestion
        current_time = time.time()
        if current_time - self.last_cmd_time < self.cmd_interval:
            return

        command_dir = None
        
        # Determine direction based on joystick angle (Single-Axis mapping)
        # Right/Forward (0 deg) -> 'F'
        if (angle >= 0 and angle <= 90) or (angle >= 270 and angle <= 360):
            command_dir = 'F'
        # Left/Backward (180 deg) -> 'B'
        elif (angle > 90 and angle < 270):
            command_dir = 'B'

        if command_dir:
            # Map force (0.1 to ~3) to number of steps (e.g., 5 to 150)
            steps = int(force * 50)
            self.send_to_arduino(command_dir, steps)
            self.last_cmd_time = current_time

    def send_to_arduino(self, direction, steps):
        try:
            # Format expected by arduino_motor.cpp: "F,200\n"
            cmd = f"{direction},{steps}\n"
            self.ser.write(cmd.encode())
            # Do not use flush() here; it can block the main FastAPI thread
        except Exception as e:
            logger.error(f"Serial transmission failed: {e}")

# Global instance for use in main.py
motor_bridge = MotorBridge()
import serial
import time

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

def initialize_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        ser.flush()
        print(f"Connected to Arduino on {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting: {e}")
        return None

def send_command(ser, direction, steps):
    """
    Sends command strictly as 'F,200' or 'B,200'
    """
    command = f"{direction},{steps}\n"
    ser.write(command.encode('utf-8'))
    print(f"Sent to Arduino: {command.strip()}")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Arduino replied: {line}")
            if "DONE" in line:
                break

if __name__ == "__main__":
    arduino = initialize_serial()
    
    if arduino:
        print("\n--- MOTOR TEST MODE ---")
        print("Type 'exit' to quit.")
        print("Format: Direction (F/B) then Steps")
        
        try:
            while True:
                user_dir = input("\nEnter Direction (F/B): ").upper()
                if user_dir == 'EXIT':
                    break
                
                if user_dir not in ['F', 'B']:
                    print("Invalid direction. Use F or B.")
                    continue
                
                try:
                    user_steps = int(input("Enter Steps (e.g., 200): "))
                except ValueError:
                    print("Steps must be a number.")
                    continue
                
                send_command(arduino, user_dir, user_steps)
                
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            arduino.close()
            print("Serial Connection Closed.")
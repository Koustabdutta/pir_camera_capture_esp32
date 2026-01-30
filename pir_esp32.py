# pir_esp32.py - ESP32 MicroPython Code
import network
import urequests as requests
import ujson as json
from machine import Pin
import time
import gc

# WiFi Configuration
WIFI_SSID = "Koustab"
WIFI_PASSWORD = "Koustab#2000"

# Server Configuration (Your desktop IP)
SERVER_URL = "http://192.168.29.173:5000/api/motion"

# PIR Sensor Pin
PIR_PIN = 14  # GPIO 14

# Global variables
motion_detected = False
last_motion_time = 0
MOTION_COOLDOWN = 10000  # 10 seconds in milliseconds

# Initialize PIR sensor
pir = Pin(PIR_PIN, Pin.IN)

def connect_wifi():
    """Connect to WiFi network"""
    sta_if = network.WLAN(network.STA_IF)
    
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection
        timeout = 20  # 20 seconds timeout
        while not sta_if.isconnected() and timeout > 0:
            time.sleep(1)
            print(".", end="")
            timeout -= 1
            
        if sta_if.isconnected():
            print("\nWiFi Connected!")
            print("IP Address:", sta_if.ifconfig()[0])
            return True
        else:
            print("\nFailed to connect to WiFi")
            return False
    else:
        print("Already connected to WiFi")
        print("IP Address:", sta_if.ifconfig()[0])
        return True

def send_motion_data():
    """Send motion detection data to server"""
    try:
        # Prepare JSON data
        data = {
            "sensor_id": "esp32_pir_01",
            "motion": True,
            "timestamp": time.ticks_ms(),
            "location": "Room_1",
            "device_type": "ESP32",
            "firmware": "MicroPython"
        }
        
        # Convert to JSON string
        json_data = json.dumps(data)
        
        # Send HTTP POST request
        print("Sending motion data to server...")
        response = requests.post(
            SERVER_URL,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print("Response Status:", response.status_code)
        if response.status_code == 200:
            print("Data sent successfully!")
        else:
            print("Failed to send data")
        
        response.close()
        return True
        
    except Exception as e:
        print("Error sending data:", e)
        return False

def main():
    """Main program loop"""
    print("ESP32 PIR Motion Sensor")
    print("=======================")
    
    # Connect to WiFi
    if not connect_wifi():
        print("Failed to connect. Check WiFi credentials.")
        return
    
    print("\nMotion detection started...")
    print("Waiting for motion...")
    
    while True:
        try:
            # Read PIR sensor
            pir_value = pir.value()
            current_time = time.ticks_ms()
            
            if pir_value == 1 and not motion_detected:
                motion_detected = True
                last_motion_time = current_time
                
                print("\n" + "="*40)
                print("MOTION DETECTED!")
                print("="*40)
                
                # Send data to server
                send_motion_data()
                
                # Flash LED (built-in)
                led = Pin(2, Pin.OUT)
                for _ in range(3):
                    led.on()
                    time.sleep(0.1)
                    led.off()
                    time.sleep(0.1)
            
            # Reset motion detection after cooldown
            if motion_detected and (time.ticks_diff(current_time, last_motion_time) > MOTION_COOLDOWN):
                motion_detected = False
                print("Motion cleared - Ready for next detection")
            
            # Small delay to prevent CPU overload
            time.sleep(0.1)
            
            # Garbage collection to prevent memory issues
            gc.collect()
            
        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(5)  # Wait before retrying

# Run the main function
if __name__ == "__main__":
    main()
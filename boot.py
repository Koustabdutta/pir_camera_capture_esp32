# boot.py - Runs on ESP32 startup
import machine
import time

# Disable access point
import network
ap = network.WLAN(network.AP_IF)
ap.active(False)

print("ESP32 Booted Successfully!")
print("Starting PIR Motion Sensor...")
time.sleep(1)

# Import main program
try:
    import pir_esp32
    pir_esp32.main()
except Exception as e:
    print("Error starting main program:", e)
    print("Rebooting in 10 seconds...")
    time.sleep(10)
    machine.reset()
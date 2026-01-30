# ESP32 Motion Detection System with Deep Learning

![Project Banner](https://img.shields.io/badge/ESP32-PIR%20Motion%20Detection-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![OpenCV](https://img.shields.io/badge/Computer%20Vision-OpenCV-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

A complete IoT project that detects motion using ESP32 with PIR sensor, captures images via USB camera, and analyzes them using deep learning to identify humans. Features real-time web dashboard with interactive GUI.

## 🌟 Features

### **Hardware Features:**
- ESP32-based motion detection with PIR sensor
- USB camera integration for image capture
- Real-time data transmission over WiFi
- Built-in LED indicators for motion alerts

### **Software Features:**
- **Real-time Dashboard**: Interactive web interface showing motion events
- **Human Detection**: Deep learning-based human recognition using OpenCV
- **Multi-method Detection**: Combines HOG, Haar Cascades, and MobileNet
- **Event Logging**: Complete history of motion events with timestamps
- **Image Storage**: Automatic saving of raw and processed images
- **WebSocket Support**: Real-time updates without page refresh
- **RESTful API**: Full API for integration with other systems

### **Detection Methods:**
1. **HOG (Histogram of Oriented Gradients)**: Fast human body detection
2. **Haar Cascades**: Face detection for better accuracy
3. **MobileNet SSD**: Deep learning-based object detection (optional)

## 📁 Project Structure

```
MotionDetectionProject/
├── desktop_server/
│   ├── main.py              # Main Flask server
│   ├── camera_manager.py    # Camera handling
│   ├── human_detector.py    # Deep learning detection
│   └── utils.py             # Utility functions
├── esp32_code/
│   ├── pir_esp32.py         # Main ESP32 code
│   ├── boot.py             # Startup script
│   └── config.py           # Configuration
├── templates/
│   └── index.html          # Web dashboard
├── static/
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── data/
│   ├── captures/          # Captured images
│   │   ├── raw/          # Original images
│   │   └── processed/    # Annotated images
│   └── logs/             # Server logs
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠 Hardware Requirements

### **Components:**
1. **ESP32 Development Board**
2. **PIR Sensor (HC-SR501)**
3. **USB Camera** (connected to desktop)
4. **Jumper Wires**
5. **Breadboard** (optional)

### **Wiring Diagram:**
```
PIR Sensor → ESP32
VCC → 3.3V or 5V
OUT → GPIO 14
GND → GND
```

## 💻 Software Requirements

### **ESP32 (MicroPython):**
- Thonny IDE with MicroPython
- Network access (WiFi)

### **Desktop Server (Python 3.8+):**
- Python 3.8 or higher
- Flask web framework
- OpenCV for computer vision
- TensorFlow (optional for deep learning)

## 🚀 Installation & Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/esp32-motion-detection.git
cd esp32-motion-detection
```

### **2. Set Up ESP32 (Thonny IDE)**

#### **Install MicroPython on ESP32:**
1. Open Thonny IDE
2. Go to **Tools → Options → Interpreter**
3. Select **MicroPython (ESP32)**
4. Click **Install or update MicroPython**
5. Choose latest ESP32 firmware

#### **Upload ESP32 Code:**
1. Connect ESP32 via USB
2. Open `esp32_code/pir_esp32.py` in Thonny
3. Update WiFi credentials:
   ```python
   WIFI_SSID = "YOUR_WIFI_NAME"
   WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
   ```
4. Update server IP (find with `ipconfig` or `ifconfig`):
   ```python
   SERVER_URL = "http://YOUR_DESKTOP_IP:5000/api/motion"
   ```
5. Click **File → Save to ESP32**

### **3. Set Up Desktop Server**

#### **Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

#### **Required Packages:**
```txt
flask==2.3.3
flask-cors==4.0.0
flask-socketio==5.3.4
opencv-python==4.8.1.78
numpy==1.24.4
pillow==10.0.0
python-socketio==5.9.0
eventlet==0.33.3
```

#### **Run the Server:**
```bash
cd desktop_server
python main.py
```

### **4. Configure Camera**
1. Connect USB camera to desktop
2. The server will automatically detect the camera
3. Click "Start Camera" on the dashboard to activate

## 📊 Usage Guide

### **1. Starting the System**
```bash
# Start the desktop server
python desktop_server/main.py

# Server will show:
# Local URL: http://localhost:5000
# Network URL: http://YOUR_IP:5000
```

### **2. Accessing the Dashboard**
Open your browser and navigate to:
- **Local**: `http://localhost:5000`
- **Network**: `http://YOUR_IP:5000`

### **3. Testing Motion Detection**
1. Power on the ESP32 with PIR sensor
2. Wave your hand in front of the sensor
3. Check dashboard for real-time updates
4. View captured images and detection results

### **4. Dashboard Features**

#### **Status Panel:**
- ESP32 connection status
- Motion detection indicator
- Human detection confidence
- Camera status

#### **Camera Feed:**
- Live camera view
- Manual capture button
- Auto-refresh option
- Annotated images with bounding boxes

#### **Event Log:**
- Timeline of motion events
- Human detection results
- Confidence scores
- Timestamps

#### **Statistics:**
- Total motion events
- Human detection count
- False alarm rate
- System uptime

## 🔧 Configuration

### **ESP32 Configuration:**
Edit `esp32_code/config.py`:
```python
# WiFi Settings
WIFI_SSID = "YourNetwork"
WIFI_PASSWORD = "YourPassword"

# Server Settings
SERVER_IP = "192.168.1.100"  # Your desktop IP
SERVER_PORT = 5000

# Sensor Settings
PIR_PIN = 14
MOTION_COOLDOWN = 10000  # 10 seconds
```

### **Server Configuration:**
Edit `desktop_server/main.py`:
```python
# Camera Settings
CAMERA_INDEX = 0  # Default USB camera

# Detection Settings
MIN_CONFIDENCE = 0.3  # Detection threshold
CAPTURE_COOLDOWN = 0.5  # Minimum seconds between captures

# Storage Settings
MAX_EVENTS = 100  # Keep last 100 events
IMAGE_QUALITY = 85  # JPEG quality
```

### **Advanced Configuration:**
```python
# Enable/disable detection methods
USE_HOG_DETECTION = True
USE_FACE_DETECTION = True
USE_DEEP_LEARNING = False  # Requires TensorFlow

# Image processing
RESIZE_WIDTH = 800  # Resize images for processing
SAVE_RAW_IMAGES = True
SAVE_PROCESSED_IMAGES = True
```

## 🧠 Deep Learning Models

### **Available Detection Methods:**

#### **1. HOG Descriptor (Default)**
- Fast and efficient for human detection
- Works well for full-body detection
- Built into OpenCV

#### **2. Haar Cascades**
- Good for face detection
- Pre-trained models included
- Fast performance

#### **3. MobileNet SSD (Optional)**
- More accurate deep learning model
- Requires additional setup
- Slower but more accurate

### **Enable Deep Learning:**
```bash
# Install TensorFlow
pip install tensorflow

# Download MobileNet model files
cd desktop_server
wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt
wget https://drive.google.com/uc?id=0B3gersZ2cHIxVFI1Rjd5aDgwOG8 -O mobilenet_iter_73000.caffemodel
```

## 🌐 API Documentation

### **Endpoints:**

#### **1. Motion Event Submission (ESP32 → Server)**
```http
POST /api/motion
Content-Type: application/json

{
    "sensor_id": "esp32_pir_01",
    "motion": true,
    "timestamp": 1234567890,
    "location": "Room_1",
    "device_type": "ESP32"
}
```

#### **2. Get All Events**
```http
GET /api/events
Response: Array of motion events
```

#### **3. Get Latest Image**
```http
GET /api/image/latest
Response: JPEG image
```

#### **4. Camera Control**
```http
POST /api/camera/control
{
    "action": "start"  # or "stop"
}
```

#### **5. System Statistics**
```http
GET /api/system/stats
Response: System metrics
```

### **WebSocket Events:**
- `motion_event`: New motion detected
- `system_update`: System status update
- `heartbeat`: Periodic update (every 5s)
- `connection_response`: Connection established

## 🐛 Troubleshooting

### **Common Issues & Solutions:**

#### **1. ESP32 Not Connecting to WiFi**
```python
# Test WiFi connection
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Scanning networks:", wlan.scan())
```

#### **2. Server Connection Failed**
- Check ESP32 can ping the server IP
- Verify firewall allows port 5000
- Ensure server is running

#### **3. Camera Not Detected**
```python
# Test camera in Python
import cv2
cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())
cap.release()
```

#### **4. No Motion Detection**
- Check PIR sensor wiring
- Adjust PIR sensitivity (potentiometer on sensor)
- Ensure sensor is in correct mode (H or I)

#### **5. Memory Issues on ESP32**
```python
# Add garbage collection
import gc
gc.collect()
print("Free memory:", gc.mem_free())
```

### **Error Logs:**
- Check `data/logs/server.log` for server errors
- ESP32 errors appear in Thonny serial monitor
- Web console errors in browser Developer Tools

## 📈 Performance Optimization

### **ESP32 Optimizations:**
```python
# Reduce transmission frequency
MOTION_COOLDOWN = 10000  # 10 seconds

# Use deep sleep between detections
# esp32.deepsleep(10000)  # 10 seconds sleep
```

### **Server Optimizations:**
```python
# Reduce image resolution
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# Enable caching
CACHE_TIMEOUT = 60  # Cache images for 60 seconds

# Limit event history
MAX_EVENTS = 100
```

### **Detection Optimizations:**
```python
# Skip detection when confidence is low
if detection_result['confidence'] < 0.3:
    skip_saving_image = True

# Process every nth frame
PROCESS_EVERY_N_FRAMES = 3
```

## 🔒 Security Considerations

### **Network Security:**
1. Change default WiFi credentials
2. Use strong passwords
3. Enable WPA2/WPA3 encryption
4. Consider VPN for remote access

### **Application Security:**
```python
# Add API authentication (optional)
API_KEY = "your-secret-key"

# Enable CORS for specific domains only
CORS_ORIGINS = ["http://localhost:5000", "http://yourdomain.com"]

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 60
```

### **Data Privacy:**
- Images stored locally only
- Automatic cleanup of old images
- No cloud storage by default
- Optional encryption for sensitive data

## 🔄 Future Enhancements

### **Planned Features:**
- [ ] Multiple ESP32 support
- [ ] Mobile app (Flutter/React Native)
- [ ] Cloud integration (AWS/Azure)
- [ ] Email/SMS notifications
- [ ] Face recognition
- [ ] Object tracking
- [ ] Time-series analysis
- [ ] Power optimization (ESP32 deep sleep)

### **Experimental Features:**
- [ ] TensorFlow Lite on ESP32
- [ ] Edge TPU acceleration
- [ ] Custom YOLO models
- [ ] 3D camera support
- [ ] Audio detection

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Ways to Contribute:**
1. **Report Bugs**: Open an issue with detailed description
2. **Suggest Features**: Propose new features or improvements
3. **Submit Pull Requests**: Fix bugs or add features
4. **Improve Documentation**: Help make docs better
5. **Share Your Setup**: Tell us how you're using the project

### **Development Setup:**
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/esp32-motion-detection.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Submit pull request
```

### **Coding Standards:**
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write unit tests for new features
- Update documentation accordingly

## 📚 Learning Resources

### **ESP32 & MicroPython:**
- [ESP32 Official Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [MicroPython for ESP32](http://docs.micropython.org/en/latest/esp32/quickref.html)
- [Thonny IDE Guide](https://thonny.org/)

### **Computer Vision:**
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)
- [HOG Person Detection](https://learnopencv.com/histogram-of-oriented-gradients/)
- [Haar Cascades Guide](https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html)

### **Flask & Web Development:**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO Guide](https://flask-socketio.readthedocs.io/)
- [Bootstrap for Dashboard](https://getbootstrap.com/)

### **Project Inspiration:**
- [ESP32-CAM Projects](https://randomnerdtutorials.com/esp32-cam-projects/)
- [Home Security Systems](https://www.hackster.io/search?q=home%20security%20esp32)
- [IoT Motion Detection](https://www.instructables.com/ESP32-Motion-Detection/)


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🎯 Quick Start Cheatsheet

```bash
# 1. Clone repo
git clone https://github.com/yourusername/esp32-motion-detection.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Update ESP32 credentials
# Edit esp32_code/pir_esp32.py with your WiFi and server IP

# 4. Run server
python desktop_server/main.py

# 5. Upload to ESP32
# Open in Thonny and save to ESP32

# 6. Test
# Wave hand in front of PIR sensor
# Open http://localhost:5000 in browser
```

**Happy Building! 🚀**

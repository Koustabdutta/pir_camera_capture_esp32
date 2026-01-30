# main.py - Flask Server (Fixed for SocketIO)
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import os
import json
from datetime import datetime
import threading
import time
import logging

# First, create necessary directories
def create_directories():
    """Create all necessary directories for the project"""
    directories = [
        'data/captures/raw',
        'data/captures/processed',
        'data/logs',
        'static/css',
        'static/js',
        'static/images',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

# Create directories first
create_directories()

# Now configure logging
log_file = 'data/logs/server.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize SocketIO with async_mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
motion_events = []
start_time = time.time()

class CameraManager:
    def __init__(self):
        self.camera_index = 0
        self.is_active = False
        
    def start_camera(self):
        """Start the camera"""
        try:
            # Test camera
            cap = cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    self.is_active = True
                    logger.info("Camera started successfully")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def capture_frame(self):
        """Capture a frame from camera"""
        if not self.is_active:
            return None
            
        try:
            cap = cv2.VideoCapture(self.camera_index)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame
            return None
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def stop_camera(self):
        """Stop the camera"""
        self.is_active = False
        logger.info("Camera stopped")
    
    def is_camera_active(self):
        return self.is_active

class HumanDetector:
    def __init__(self):
        # Initialize HOG descriptor for human detection
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Initialize face cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        logger.info("Human detector initialized")
    
    def detect(self, frame):
        """Detect humans in frame"""
        result = {
            'has_human': False,
            'confidence': 0.0,
            'method': 'none',
            'people_count': 0,
            'processing_time': 0,
            'annotated_image': None
        }
        
        try:
            start_time = time.time()
            annotated = frame.copy()
            
            # Method 1: HOG for full body detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            boxes, weights = self.hog.detectMultiScale(
                gray,
                winStride=(4, 4),
                padding=(8, 8),
                scale=1.05
            )
            
            # Method 2: Face detection
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Combine detections
            all_boxes = []
            
            # Add HOG detections
            for i, (x, y, w, h) in enumerate(boxes):
                confidence = weights[i][0] if i < len(weights) else 0.5
                if confidence > 0.3:
                    all_boxes.append({
                        'box': (int(x), int(y), int(w), int(h)),
                        'confidence': float(confidence),
                        'method': 'body'
                    })
            
            # Add face detections
            for (x, y, w, h) in faces:
                all_boxes.append({
                    'box': (int(x), int(y), int(w), int(h)),
                    'confidence': 0.8,
                    'method': 'face'
                })
            
            # Draw boxes and update result
            people_count = 0
            max_confidence = 0.0
            
            for detection in all_boxes:
                x, y, w, h = detection['box']
                confidence = detection['confidence']
                method = detection['method']
                
                # Draw rectangle
                color = (0, 255, 0)  # Green
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                
                # Label
                label = f"{method}: {confidence:.2f}"
                cv2.putText(annotated, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                people_count += 1
                max_confidence = max(max_confidence, confidence)
            
            result['has_human'] = people_count > 0
            result['people_count'] = people_count
            result['confidence'] = max_confidence
            result['method'] = 'combined' if people_count > 0 else 'none'
            result['processing_time'] = time.time() - start_time
            result['annotated_image'] = annotated
            
            if result['has_human']:
                logger.info(f"Detected {people_count} human(s)")
            
        except Exception as e:
            logger.error(f"Error in human detection: {e}")
            result['annotated_image'] = frame.copy()
        
        return result

# Initialize components
camera_manager = CameraManager()
human_detector = HumanDetector()

@app.route('/')
def index():
    """Serve the main dashboard"""
    # Check if index.html exists, if not, create a simple one
    if not os.path.exists('templates/index.html'):
        return """
        <html>
            <head>
                <title>Motion Detection Dashboard</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
                    .status { padding: 10px; margin: 5px 0; border-radius: 3px; }
                    .online { background: #d4edda; color: #155724; }
                    .offline { background: #f8d7da; color: #721c24; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Motion Detection Dashboard</h1>
                    <div class="card">
                        <h2>Server Status</h2>
                        <div class="status online">Server is running</div>
                        <p>Local URL: <a href="http://localhost:5000">http://localhost:5000</a></p>
                        <p>Network URL: <a href="http://192.168.29.173:5000">http://192.168.29.173:5000</a></p>
                    </div>
                    <div class="card">
                        <h2>Endpoints</h2>
                        <ul>
                            <li><a href="/api/test">/api/test</a> - Test server connection</li>
                            <li><a href="/api/events">/api/events</a> - View all motion events</li>
                            <li><a href="/api/system/stats">/api/system/stats</a> - System statistics</li>
                        </ul>
                    </div>
                    <div class="card">
                        <h2>Camera Control</h2>
                        <button onclick="startCamera()">Start Camera</button>
                        <button onclick="stopCamera()">Stop Camera</button>
                        <button onclick="captureImage()">Capture Image</button>
                        <div id="cameraStatus">Camera is stopped</div>
                    </div>
                    <div class="card">
                        <h2>Recent Events</h2>
                        <div id="events"></div>
                    </div>
                </div>
                <script>
                    function startCamera() {
                        fetch('/api/camera/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({action: 'start'})
                        }).then(r => r.json()).then(data => {
                            document.getElementById('cameraStatus').textContent = 
                                'Camera started successfully';
                        });
                    }
                    
                    function stopCamera() {
                        fetch('/api/camera/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({action: 'stop'})
                        }).then(r => r.json()).then(data => {
                            document.getElementById('cameraStatus').textContent = 
                                'Camera stopped';
                        });
                    }
                    
                    function captureImage() {
                        fetch('/api/debug/capture', {method: 'POST'})
                        .then(r => r.json()).then(data => {
                            alert('Image captured: ' + data.path);
                        });
                    }
                    
                    // Load events
                    fetch('/api/events')
                        .then(r => r.json())
                        .then(data => {
                            let html = '<p>Total events: ' + data.length + '</p>';
                            data.slice(-5).reverse().forEach(event => {
                                html += '<div style="border:1px solid #ccc;padding:10px;margin:5px 0;">';
                                html += '<strong>Event ' + event.id + '</strong><br>';
                                html += 'Time: ' + event.server_time + '<br>';
                                html += 'Location: ' + event.location;
                                if (event.detection) {
                                    html += '<br>Human detected: ' + event.detection.has_human;
                                }
                                html += '</div>';
                            });
                            document.getElementById('events').innerHTML = html;
                        });
                </script>
            </body>
        </html>
        """
    return render_template('index.html')

@app.route('/api/motion', methods=['POST'])
def handle_motion():
    """Handle motion data from ESP32"""
    try:
        data = request.json
        logger.info(f"Motion detected from ESP32: {data}")
        
        # Add server timestamp
        data['server_time'] = datetime.now().isoformat()
        data['id'] = len(motion_events) + 1
        
        # Capture image from camera if active
        if camera_manager.is_camera_active():
            frame = camera_manager.capture_frame()
            if frame is not None:
                # Save raw image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                raw_path = f'data/captures/raw/motion_{timestamp}.jpg'
                cv2.imwrite(raw_path, frame)
                data['raw_image'] = raw_path
                
                # Detect humans
                detection_result = human_detector.detect(frame)
                data['detection'] = detection_result
                
                # Save processed image if human detected
                if detection_result['has_human']:
                    processed_path = f'data/captures/processed/human_{timestamp}.jpg'
                    cv2.imwrite(processed_path, detection_result['annotated_image'])
                    data['processed_image'] = processed_path
                
                # Emit real-time update via SocketIO
                socketio.emit('motion_event', {
                    'id': data['id'],
                    'time': data['server_time'],
                    'has_human': detection_result['has_human'],
                    'confidence': detection_result['confidence'],
                    'people_count': detection_result['people_count']
                })
        
        # Store event
        motion_events.append(data)
        
        # Keep only last 100 events
        if len(motion_events) > 100:
            motion_events.pop(0)
        
        return jsonify({
            'status': 'success',
            'message': 'Motion recorded',
            'event_id': data['id']
        })
        
    except Exception as e:
        logger.error(f"Error handling motion: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all motion events"""
    return jsonify(motion_events)

@app.route('/api/events/latest', methods=['GET'])
def get_latest_event():
    """Get latest motion event"""
    if motion_events:
        return jsonify(motion_events[-1])
    return jsonify({})

@app.route('/api/image/<image_type>', methods=['GET'])
def get_image(image_type):
    """Get latest image"""
    if not motion_events:
        return jsonify({'error': 'No events available'}), 404
    
    latest_event = motion_events[-1]
    
    if image_type == 'raw' and 'raw_image' in latest_event:
        return send_file(latest_event['raw_image'])
    elif image_type == 'processed' and 'processed_image' in latest_event:
        return send_file(latest_event['processed_image'])
    elif image_type == 'latest':
        # Return whichever image is available
        if 'processed_image' in latest_event:
            return send_file(latest_event['processed_image'])
        elif 'raw_image' in latest_event:
            return send_file(latest_event['raw_image'])
    
    # Return a placeholder image
    from flask import Response
    import numpy as np
    
    # Create a simple placeholder image
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, "No Image Available", (50, 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    _, buffer = cv2.imencode('.jpg', img)
    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/api/camera/control', methods=['POST'])
def camera_control():
    """Start/Stop camera"""
    data = request.json
    action = data.get('action', '')
    
    if action == 'start':
        success = camera_manager.start_camera()
        return jsonify({'status': 'success' if success else 'error'})
    elif action == 'stop':
        camera_manager.stop_camera()
        return jsonify({'status': 'success'})
    elif action == 'status':
        return jsonify({
            'active': camera_manager.is_camera_active(),
            'camera_index': camera_manager.camera_index
        })
    
    return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    human_detections = sum(1 for e in motion_events 
                          if e.get('detection', {}).get('has_human', False))
    
    stats = {
        'total_events': len(motion_events),
        'human_detections': human_detections,
        'camera_active': camera_manager.is_camera_active(),
        'server_uptime': int(time.time() - start_time),
        'detection_rate': round((human_detections / len(motion_events) * 100), 2) if motion_events else 0
    }
    
    if motion_events:
        stats['last_event'] = motion_events[-1].get('server_time')
    
    return jsonify(stats)

@app.route('/api/debug/capture', methods=['POST'])
def manual_capture():
    """Manually capture image for testing"""
    if camera_manager.is_camera_active():
        frame = camera_manager.capture_frame()
        if frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f'data/captures/manual_{timestamp}.jpg'
            cv2.imwrite(path, frame)
            
            # Also detect humans
            detection = human_detector.detect(frame)
            
            return jsonify({
                'status': 'success', 
                'path': path,
                'detection': detection
            })
    
    return jsonify({'status': 'error', 'message': 'Camera not active'}), 400

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'Server is running',
        'time': datetime.now().isoformat(),
        'events_count': len(motion_events),
        'uptime': int(time.time() - start_time),
        'camera_active': camera_manager.is_camera_active(),
        'ip_address': '192.168.29.173'  # Your IP
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected via WebSocket')
    emit('connection_response', {'status': 'connected', 'time': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Send current status to client"""
    latest_event = motion_events[-1] if motion_events else None
    emit('system_update', {
        'camera_active': camera_manager.is_camera_active(),
        'total_events': len(motion_events),
        'latest_event': latest_event,
        'server_time': datetime.now().isoformat()
    })

def background_task():
    """Background task for periodic updates"""
    while True:
        time.sleep(5)
        if motion_events:
            latest = motion_events[-1]
            socketio.emit('heartbeat', {
                'time': datetime.now().isoformat(),
                'last_motion': latest.get('server_time'),
                'human_detected': latest.get('detection', {}).get('has_human', False),
                'people_count': latest.get('detection', {}).get('people_count', 0)
            })

if __name__ == '__main__':
    # Start background thread
    bg_thread = threading.Thread(target=background_task, daemon=True)
    bg_thread.start()
    
    logger.info("="*50)
    logger.info("Motion Detection Server Starting...")
    logger.info("="*50)
    logger.info(f"Log file: {log_file}")
    logger.info("Local URL: http://localhost:5000")
    
    # Get local IP address
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        logger.info(f"Network URL: http://{local_ip}:5000")
    except Exception as e:
        logger.warning(f"Could not determine network IP: {e}")
    
    logger.info("="*50)
    
    # Start server with allow_unsafe_werkzeug=True
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=5000, 
                 debug=False, 
                 use_reloader=False,
                 allow_unsafe_werkzeug=True)  # This fixes the error
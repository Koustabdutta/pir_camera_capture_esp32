# camera_manager.py - Camera management
import cv2
import threading
import time
import logging

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self):
        self.camera = None
        self.camera_index = 0  # Default USB camera
        self.is_active = False
        self.lock = threading.Lock()
        self.last_capture_time = 0
        self.capture_cooldown = 0.5  # Minimum seconds between captures
    
    def start_camera(self, camera_index=0):
        """Initialize and start camera"""
        with self.lock:
            if self.is_active:
                logger.info("Camera already active")
                return True
            
            try:
                self.camera = cv2.VideoCapture(camera_index)
                self.camera_index = camera_index
                
                # Test camera
                if self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret:
                        self.is_active = True
                        logger.info(f"Camera {camera_index} started successfully")
                        # Release for now, will reopen when needed
                        self.camera.release()
                        self.camera = None
                        return True
                    else:
                        self.camera.release()
                        self.camera = None
                        logger.error(f"Camera {camera_index} test capture failed")
                        return False
                else:
                    logger.error(f"Failed to open camera {camera_index}")
                    return False
                    
            except Exception as e:
                logger.error(f"Error starting camera: {e}")
                if self.camera:
                    self.camera.release()
                    self.camera = None
                return False
    
    def capture_frame(self):
        """Capture a single frame from camera"""
        current_time = time.time()
        
        # Enforce cooldown
        if current_time - self.last_capture_time < self.capture_cooldown:
            return None
        
        with self.lock:
            try:
                # Open camera if not already open
                if not self.camera:
                    self.camera = cv2.VideoCapture(self.camera_index)
                    time.sleep(0.5)  # Warm-up time
                
                if self.camera and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    self.last_capture_time = current_time
                    
                    if ret:
                        # Release camera to free resources
                        self.camera.release()
                        self.camera = None
                        return frame
                    else:
                        logger.warning("Failed to capture frame")
                        self.camera.release()
                        self.camera = None
                        return None
                else:
                    logger.warning("Camera not available for capture")
                    return None
                    
            except Exception as e:
                logger.error(f"Error capturing frame: {e}")
                if self.camera:
                    self.camera.release()
                    self.camera = None
                return None
    
    def stop_camera(self):
        """Stop and release camera"""
        with self.lock:
            if self.camera:
                self.camera.release()
                self.camera = None
            self.is_active = False
            logger.info("Camera stopped")
    
    def is_camera_active(self):
        """Check if camera is active"""
        return self.is_active
    
    def list_available_cameras(self, max_test=5):
        """List all available cameras"""
        available = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
            else:
                cap.release()
        return available
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop_camera()
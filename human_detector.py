# human_detector.py - Human detection using deep learning
import cv2
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

class HumanDetector:
    def __init__(self, use_deep_learning=True):
        self.use_deep_learning = use_deep_learning
        
        # Initialize OpenCV HOG descriptor for human detection
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Initialize face cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Deep learning model paths (if using)
        self.dnn_model = None
        if use_deep_learning:
            self._initialize_dnn()
        
        logger.info("Human detector initialized")
    
    def _initialize_dnn(self):
        """Initialize deep learning model"""
        try:
            # MobileNet SSD for object detection
            prototxt = "models/MobileNetSSD_deploy.prototxt.txt"
            model = "models/MobileNetSSD_deploy.caffemodel"
            
            # Try to load pre-trained model
            self.dnn_model = cv2.dnn.readNetFromCaffe(prototxt, model)
            logger.info("Deep learning model loaded")
        except:
            logger.warning("Could not load deep learning model, using HOG only")
            self.use_deep_learning = False
    
    def detect(self, image):
        """Detect humans in image using multiple methods"""
        start_time = time.time()
        
        # Convert to RGB for display
        display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result_image = image.copy()
        
        # Initialize result
        result = {
            'has_human': False,
            'confidence': 0.0,
            'method': 'none',
            'bounding_boxes': [],
            'people_count': 0,
            'processing_time': 0,
            'annotated_image': None
        }
        
        # Method 1: HOG descriptor (fast and reliable for people)
        hog_boxes, hog_weights = self.hog.detectMultiScale(
            image,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.05
        )
        
        # Method 2: Face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_boxes = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Method 3: Deep learning (if available)
        dnn_boxes = []
        if self.use_deep_learning and self.dnn_model:
            dnn_boxes = self._detect_dnn(image)
        
        # Combine results
        all_boxes = []
        
        # Add HOG detections
        for i, (x, y, w, h) in enumerate(hog_boxes):
            confidence = hog_weights[i][0] if i < len(hog_weights) else 0.5
            if confidence > 0.3:  # Confidence threshold
                all_boxes.append({
                    'box': (int(x), int(y), int(w), int(h)),
                    'confidence': float(confidence),
                    'method': 'hog'
                })
        
        # Add face detections
        for (x, y, w, h) in face_boxes:
            all_boxes.append({
                'box': (int(x), int(y), int(w), int(h)),
                'confidence': 0.8,  # High confidence for faces
                'method': 'face'
            })
        
        # Add DNN detections
        for box in dnn_boxes:
            all_boxes.append(box)
        
        # Apply non-maximum suppression to remove overlapping boxes
        filtered_boxes = self._non_max_suppression(all_boxes)
        
        # Draw bounding boxes
        for detection in filtered_boxes:
            x, y, w, h = detection['box']
            confidence = detection['confidence']
            method = detection['method']
            
            # Draw rectangle
            color = (0, 255, 0)  # Green for human
            cv2.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
            
            # Label
            label = f"{method}: {confidence:.2f}"
            cv2.putText(result_image, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            result['has_human'] = True
            result['confidence'] = max(result['confidence'], confidence)
            result['bounding_boxes'].append(detection['box'])
        
        result['people_count'] = len(filtered_boxes)
        result['method'] = 'combined' if filtered_boxes else 'none'
        result['processing_time'] = time.time() - start_time
        result['annotated_image'] = result_image
        
        if result['has_human']:
            logger.info(f"Detected {result['people_count']} human(s) "
                       f"with confidence {result['confidence']:.2f}")
        
        return result
    
    def _detect_dnn(self, image):
        """Detect objects using DNN"""
        boxes = []
        
        try:
            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)),
                0.007843, (300, 300), 127.5
            )
            
            self.dnn_model.setInput(blob)
            detections = self.dnn_model.forward()
            
            # Class IDs for person in MobileNet SSD
            PERSON_CLASS_ID = 15
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > 0.5:  # Confidence threshold
                    class_id = int(detections[0, 0, i, 1])
                    
                    if class_id == PERSON_CLASS_ID:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        boxes.append({
                            'box': (startX, startY, endX - startX, endY - startY),
                            'confidence': float(confidence),
                            'method': 'dnn'
                        })
        
        except Exception as e:
            logger.error(f"DNN detection error: {e}")
        
        return boxes
    
    def _non_max_suppression(self, detections, threshold=0.5):
        """Apply non-maximum suppression to remove overlapping boxes"""
        if len(detections) == 0:
            return []
        
        # Extract boxes and confidences
        boxes = np.array([d['box'] for d in detections])
        confidences = np.array([d['confidence'] for d in detections])
        
        # Convert to (x1, y1, x2, y2) format
        boxes_xyxy = np.zeros((len(boxes), 4))
        boxes_xyxy[:, 0] = boxes[:, 0]  # x1
        boxes_xyxy[:, 1] = boxes[:, 1]  # y1
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]  # x2
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]  # y2
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            confidences.tolist(),
            0.3,  # Score threshold
            threshold  # NMS threshold
        )
        
        # Return filtered detections
        if len(indices) > 0:
            if hasattr(indices, 'shape'):
                indices = indices.flatten()
            return [detections[i] for i in indices]
        
        return []
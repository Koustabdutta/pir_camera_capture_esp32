# utils.py - Utility functions
import json
import os
from datetime import datetime
import cv2
import numpy as np

def save_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def get_timestamp():
    """Get current timestamp string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def resize_image(image, max_width=800):
    """Resize image maintaining aspect ratio"""
    if image is None:
        return None
    
    height, width = image.shape[:2]
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        return cv2.resize(image, (max_width, new_height))
    return image

def draw_stats_on_image(image, stats):
    """Draw statistics on image"""
    if image is None:
        return image
    
    result = image.copy()
    y_offset = 30
    line_height = 25
    
    # Background for text
    cv2.rectangle(result, (10, 10), (300, 120), (0, 0, 0), -1)
    
    # Draw text
    cv2.putText(result, f"Human Detected: {stats.get('has_human', False)}", 
               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.putText(result, f"Confidence: {stats.get('confidence', 0):.2f}", 
               (20, y_offset + line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.putText(result, f"People Count: {stats.get('people_count', 0)}", 
               (20, y_offset + 2*line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.putText(result, f"Method: {stats.get('method', 'none')}", 
               (20, y_offset + 3*line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(result, timestamp, (20, y_offset + 4*line_height), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return result
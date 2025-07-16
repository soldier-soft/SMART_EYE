# API Reference

## Google Maps API
- Endpoint: `https://maps.googleapis.com/maps/api/directions/json`
- Required Parameters:
  - `origin`: Starting location
  - `destination`: Target location
  - `mode`: Transportation mode (walking, driving, etc.)
  - `key`: API key

## Object Detection (YOLOv3)
- Input: 416x416 RGB image
- Output: List of detected objects with:
  - Label
  - Confidence
  - Bounding box coordinates

## Face Recognition
- Database Schema:
  - `id`: Integer (primary key)
  - `name`: Text
  - `image_path`: Text
  - `last_seen`: Timestamp

## Currency Recognition
- Supported Currencies:
  - 10 Rupee
  - 20 Rupee
  - 50 Rupee
  - 100 Rupee
  - 200 Rupee
  - 500 Rupee
  - 2000 Rupee
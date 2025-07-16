from core.object_detection.detector import ObjectDetector

detector = ObjectDetector(
    config_path="../data/models/yolov3.cfg",
    weights_path="../data/models/yolov3.weights",
    classes_path="../core/object_detection/labels.txt"
)

# Run on webcam
detector.detect_from_camera()

# OR run on a sample image
# detector.detect_from_image("../data/test_image.jpg")

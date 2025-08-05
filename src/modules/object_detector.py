from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_name='yolov8n.pt'):
        self.model = YOLO(model_name)

    def detect(self, frame, conf=0.5):
        results = self.model(frame, conf=conf)
        return results
from ultralytics import YOLO

class ObjectDetector:
    # Usiamo il modello intermedio 'yolov8m.pt'
    def __init__(self, model_name='yolov8m.pt'):
        self.model = YOLO(model_name)

    def track(self, frame, conf=0.2):
        # Filtriamo le classi che ci interessano (persona e palla)
        # La classe 'sports ball' è la 32 nel modello COCO
        # La classe 'person' è la 0
        results = self.model.track(frame, conf=conf, tracker="bytetrack.yaml", classes=[0, 32])
        return results
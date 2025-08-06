import os
import cv2
from modules.video_processor import VideoProcessor
from modules.object_detector import ObjectDetector
from modules.tracker import Tracker

def main():
    video_path = os.path.join("data", "raw", "match.mp4")

    try:
        processor = VideoProcessor(video_path)
    except FileNotFoundError as e:
        print(e)
        return

    detector = ObjectDetector()
    tracker = Tracker() # <-- Corretto qui

    print("Inizio l'analisi del video. Premi 'q' per uscire.")

    while True:
        ret, frame = processor.read_frame()
        if not ret:
            break

        results = detector.track(frame) # <-- Corretto qui
        processed_data = tracker.update(results, processor.fps, detector.model) # <-- Corretto qui

        for data in processed_data:
            x1, y1, x2, y2 = data['box']
            track_id = data['id']
            speed = data['speed']
            class_name = data['class_name']

            if class_name == 'person':
                color = (255, 0, 0)
                label = f"ID: {track_id} - Velocita: {speed:.2f}px/s"
            elif class_name == 'sports ball':
                color = (0, 0, 255)
                label = f"Palla ID: {track_id} - Velocita: {speed:.2f}px/s"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow('Analisi Partita', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    processor.release()
    tracker.print_metrics()
    print("Analisi completata. Rilasciate le risorse.")

if __name__ == "__main__":
    main()
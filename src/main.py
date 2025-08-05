import cv2
import os
from ultralytics import YOLO
import math

# Percorso del file video
video_path = os.path.join("data", "raw", "match.mp4")

# Controlla se il video esiste
if not os.path.exists(video_path):
    print(f"Errore: Il file video non è stato trovato a questo percorso: {video_path}")
    exit()

# Crea un oggetto VideoCapture per leggere il video
cap = cv2.VideoCapture(video_path)

# Controlla se il video è stato aperto correttamente
if not cap.isOpened():
    print("Errore: Impossibile aprire il file video.")
    exit()

# Ottieni i frame per secondo (FPS) del video per calcolare la velocità
fps = cap.get(cv2.CAP_PROP_FPS)

# Carica il modello YOLOv8
print("Caricamento del modello YOLOv8...")
model = YOLO('yolov8n.pt')
print("Modello caricato.")

# Dizionario per memorizzare i dati di tracciamento e le metriche per ogni giocatore
player_data = {}

print("Inizio l'analisi e il tracciamento del video. Premi 'q' per uscire.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fine del video.")
        break

    # Esegui il tracciamento sul frame corrente
    # Il parametro 'tracker' abilita il tracker di YOLO. 'bytetrack.yaml' è la configurazione predefinita.
    results = model.track(frame, conf=0.5, tracker="bytetrack.yaml")

    for result in results:
        # Estrai le bounding box e gli ID di tracciamento
        boxes = result.boxes
        
        for box in boxes:
            # Estrai le coordinate del rettangolo e l'ID di tracciamento
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            track_id = int(box.id[0].tolist())
            class_id = int(box.cls[0].tolist())
            confidence = float(box.conf[0].tolist())
            class_name = model.names[class_id]
            
            # Filtra per mostrare solo i giocatori
            if class_name == 'person':
                # Calcola il centro della bounding box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                # Se l'ID del giocatore non è ancora nel nostro dizionario, inizializzalo
                if track_id not in player_data:
                    player_data[track_id] = {
                        'positions': [],
                        'total_distance': 0.0,
                        'current_speed': 0.0
                    }

                # Calcola la distanza e la velocità
                if len(player_data[track_id]['positions']) > 0:
                    last_position = player_data[track_id]['positions'][-1]
                    # Distanza euclidea tra la posizione attuale e quella precedente
                    distance = math.sqrt((center_x - last_position[0])**2 + (center_y - last_position[1])**2)
                    # Aggiorna la distanza totale
                    player_data[track_id]['total_distance'] += distance
                    # Calcola la velocità (pixel al secondo)
                    player_data[track_id]['current_speed'] = (distance * fps)
                
                # Salva la posizione corrente
                player_data[track_id]['positions'].append((center_x, center_y))

                # Disegna il rettangolo e le metriche sul frame
                color = (255, 0, 0) # Blu per il tracciamento
                label = f"ID: {track_id} - Velocita: {player_data[track_id]['current_speed']:.2f}px/s"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Mostra il frame elaborato
    cv2.imshow('Analisi Partita', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia l'oggetto VideoCapture e chiudi tutte le finestre
cap.release()
cv2.destroyAllWindows()

# Stampa le metriche finali
print("\n--- Riepilogo delle metriche ---")
for track_id, data in player_data.items():
    print(f"Giocatore ID {track_id}:")
    print(f"  Distanza totale percorsa: {data['total_distance']:.2f} pixel")
    print(f"  Velocità media: {sum(p[1] for p in player_data[track_id]['positions']) / len(player_data[track_id]['positions']) if player_data[track_id]['positions'] else 0:.2f} px/s")
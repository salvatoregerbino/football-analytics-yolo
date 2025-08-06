import math

class Tracker:
    def __init__(self):
        self.player_data = {}
        self.ball_data = {
            'positions': [],
            'total_distance': 0.0,
            'current_speed': 0.0
        }

    def update(self, results, fps, model): # <-- Ripristinato il parametro 'model'
        processed_data = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                track_id = int(box.id[0].tolist()) if box.id is not None else None
                class_id = int(box.cls[0].tolist())
                confidence = float(box.conf[0].tolist())
                class_name = model.names[class_id] # <-- Corretto qui, usando il 'model' passato

                # Calcola il centro
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                if class_name == 'person' and track_id is not None:
                    # Logica per i giocatori
                    if track_id not in self.player_data:
                        self.player_data[track_id] = {
                            'positions': [],
                            'total_distance': 0.0,
                            'current_speed': 0.0
                        }
                    # ... resto della logica per il giocatore (che è corretta)
                    if len(self.player_data[track_id]['positions']) > 0:
                        last_position = self.player_data[track_id]['positions'][-1]
                        distance = math.sqrt((center_x - last_position[0])**2 + (center_y - last_position[1])**2)
                        self.player_data[track_id]['total_distance'] += distance
                        self.player_data[track_id]['current_speed'] = (distance * fps)

                    self.player_data[track_id]['positions'].append((center_x, center_y))

                    processed_data.append({
                        'id': track_id,
                        'box': (x1, y1, x2, y2),
                        'speed': self.player_data[track_id]['current_speed'],
                        'confidence': confidence,
                        'class_name': 'person'
                    })

                elif class_name == 'sports ball' and track_id is not None:
                    # Logica per la palla
                    if len(self.ball_data['positions']) > 0:
                        last_position = self.ball_data['positions'][-1]
                        distance = math.sqrt((center_x - last_position[0])**2 + (center_y - last_position[1])**2)
                        self.ball_data['total_distance'] += distance
                        self.ball_data['current_speed'] = (distance * fps)

                    self.ball_data['positions'].append((center_x, center_y))

                    processed_data.append({
                        'id': track_id,
                        'box': (x1, y1, x2, y2),
                        'speed': self.ball_data['current_speed'],
                        'confidence': confidence,
                        'class_name': 'sports ball'
                    })

        return processed_data

    def print_metrics(self):
        print("\n--- Riepilogo delle metriche ---")
        for track_id, data in self.player_data.items():
            print(f"Giocatore ID {track_id}:")
            print(f"  Distanza totale percorsa: {data['total_distance']:.2f} pixel")
            speeds = []
            for i in range(1, len(data['positions'])):
                p1 = data['positions'][i-1]
                p2 = data['positions'][i]
                distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                speeds.append(distance)

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                print(f"  Velocità media: {avg_speed:.2f} px/s")

        if len(self.ball_data['positions']) > 1:
            print("\n--- Palla ---")
            print(f"  Distanza totale percorsa: {self.ball_data['total_distance']:.2f} pixel")
            speeds = []
            for i in range(1, len(self.ball_data['positions'])):
                p1 = self.ball_data['positions'][i-1]
                p2 = self.ball_data['positions'][i]
                distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                speeds.append(distance)

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                print(f"  Velocità media: {avg_speed:.2f} px/s")
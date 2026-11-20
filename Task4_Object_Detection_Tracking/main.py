"""CodeAlpha - Task 4 : Object Detection and Tracking
Détection : YOLOv8 (pré-entraîné COCO)  |  Suivi : Deep SORT  |  Vidéo : OpenCV

Exemples :
    python main.py --source 0                          # webcam
    python main.py --source video.mp4                  # fichier vidéo
    python main.py --source video.mp4 --output out.mp4 # + sauvegarde du résultat
    python main.py --source 0 --classes person car     # seulement certaines classes
Touche  q  ou  Échap : quitter.
"""
import argparse
import sys
import time
from collections import defaultdict, deque

import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Détection et suivi d'objets (YOLOv8 + Deep SORT)")
    p.add_argument("--source", default="0", help="0 = webcam, ou chemin d'une vidéo")
    p.add_argument("--model", default="yolov8n.pt", help="yolov8n.pt (rapide) ... yolov8x.pt (précis)")
    p.add_argument("--conf", type=float, default=0.4, help="seuil de confiance de détection")
    p.add_argument("--classes", nargs="*", default=None, help="ex. person car (par défaut : toutes)")
    p.add_argument("--imgsz", type=int, default=640, help="taille d'analyse : 320 ou 416 = plus rapide")
    p.add_argument("--max-age", type=int, default=30, help="images pendant lesquelles un objet perdu est gardé")
    p.add_argument("--output", default=None, help="sauvegarder la vidéo annotée (ex. out.mp4)")
    p.add_argument("--no-show", action="store_true", help="ne pas ouvrir de fenêtre (serveur)")
    p.add_argument("--max-frames", type=int, default=0, help="arrêter après N images (0 = illimité)")
    return p.parse_args(argv)


def color_for_id(track_id: int):
    """Une couleur stable par identifiant."""
    rng = np.random.RandomState(int(track_id) * 7 + 3)
    return tuple(int(c) for c in rng.randint(60, 255, 3))


def open_source(source: str):
    """Ouvre un fichier vidéo ou une webcam (sous Windows : backend DirectShow, plus fiable)."""
    if not str(source).isdigit():
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise SystemExit(f"Impossible d'ouvrir la vidéo : {source}")
        return cap

    first = int(source)
    for index in [first] + [i for i in range(3) if i != first]:  # essaie 0, 1, 2
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY] if sys.platform == "win32" else [cv2.CAP_ANY]
        for backend in backends:
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened() and cap.read()[0]:
                print(f"Webcam ouverte (index {index}).")
                return cap
            cap.release()
    raise SystemExit(
        "Aucune webcam trouvée. Vérifiez : 1) la caméra est branchée/activée, 2) Paramètres Windows > "
        "Confidentialité > Caméra : autoriser les applications de bureau, 3) elle n'est pas utilisée "
        "par Zoom/Teams/le navigateur. Sinon utilisez une vidéo : python main.py --source video.mp4"
    )


def run(args) -> dict:
    model = YOLO(args.model)
    names = model.names  # {0: 'person', 1: 'bicycle', ...}

    class_ids = None
    if args.classes:
        wanted = {c.lower() for c in args.classes}
        class_ids = [i for i, n in names.items() if n.lower() in wanted]
        if not class_ids:
            raise SystemExit(f"Aucune classe reconnue dans {args.classes}. Exemples : person, car, dog")

    tracker = DeepSort(max_age=args.max_age, n_init=3, max_cosine_distance=0.3, nn_budget=100)

    cap = open_source(args.source)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25
    writer = None

    trails = defaultdict(lambda: deque(maxlen=30))  # trajectoire de chaque ID
    seen_ids = set()
    fps, frames = 0.0, 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            t0 = time.time()

            # 1) Détection
            result = model(frame, conf=args.conf, classes=class_ids, imgsz=args.imgsz, verbose=False)[0]
            detections = []
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(([x1, y1, x2 - x1, y2 - y1], float(box.conf[0]), names[int(box.cls[0])]))

            # 2) Suivi (Deep SORT attribue un ID stable à chaque objet)
            tracks = tracker.update_tracks(detections, frame=frame)

            # 3) Affichage
            active = 0
            for tr in tracks:
                if not tr.is_confirmed() or tr.time_since_update > 1:
                    continue
                active += 1
                tid = int(tr.track_id)
                seen_ids.add(tid)
                x1, y1, x2, y2 = map(int, tr.to_ltrb())
                label = f"{tr.get_det_class() or 'objet'} | ID {tid}"
                color = color_for_id(tid)

                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                trails[tid].append((cx, cy))
                pts = np.array(trails[tid], np.int32).reshape(-1, 1, 2)
                if len(pts) > 1:
                    cv2.polylines(frame, [pts], False, color, 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(frame, (x1, max(0, y1 - th - 8)), (x1 + tw + 6, y1), color, -1)
                cv2.putText(frame, label, (x1 + 3, max(th, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

            frames += 1
            inst = 1.0 / max(time.time() - t0, 1e-6)
            fps = inst if fps == 0 else 0.9 * fps + 0.1 * inst
            hud = f"FPS {fps:4.1f} | Objets suivis : {active} | IDs uniques : {len(seen_ids)}"
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 30), (0, 0, 0), -1)
            cv2.putText(frame, hud, (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if args.output:
                if writer is None:
                    h, w = frame.shape[:2]
                    writer = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*"mp4v"), src_fps, (w, h))
                writer.write(frame)

            if not args.no_show:
                cv2.imshow("CodeAlpha - Object Detection & Tracking", frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
            if args.max_frames and frames >= args.max_frames:
                break
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()

    summary = {"frames": frames, "unique_ids": len(seen_ids), "avg_fps": round(fps, 1)}
    print(f"Terminé : {summary}")
    return summary


if __name__ == "__main__":
    run(parse_args())
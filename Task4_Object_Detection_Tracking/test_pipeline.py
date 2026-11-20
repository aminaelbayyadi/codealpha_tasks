"""Auto-test : crée une courte vidéo à partir de l'image d'exemple d'Ultralytics (bus + piétons),
puis lance détection + suivi sans fenêtre. Lancer : python test_pipeline.py"""
from pathlib import Path

import cv2
import numpy as np
import ultralytics

from main import parse_args, run

img = cv2.imread(str(Path(ultralytics.__file__).parent / "assets" / "bus.jpg"))
h, w = img.shape[:2]
canvas_w, canvas_h = 640, 640
img = cv2.resize(img, (int(w * canvas_h / h), canvas_h))

# vidéo synthétique : l'image glisse lentement vers la gauche (les objets "bougent")
writer = cv2.VideoWriter("test_video.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 20, (canvas_w, canvas_h))
for i in range(40):
    M = np.float32([[1, 0, -3 * i], [0, 1, 0]])
    writer.write(cv2.warpAffine(img, M, (canvas_w, canvas_h)))
writer.release()

summary = run(parse_args(["--source", "test_video.mp4", "--no-show", "--output", "test_output.mp4"]))
assert summary["frames"] == 40, "toutes les images doivent être traitées"
assert summary["unique_ids"] >= 1, "au moins un objet doit être suivi"
assert Path("test_output.mp4").exists()
print("✅ Test réussi : détection + suivi fonctionnent. Vidéo annotée : test_output.mp4")

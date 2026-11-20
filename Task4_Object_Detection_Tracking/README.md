# 🎯 CodeAlpha_ObjectDetectionTracking

> **CodeAlpha AI Internship – Task 4: Object Detection and Tracking**

Real-time object detection and tracking from a webcam or a video file. Objects are detected with a pre-trained **YOLOv8** model and tracked across frames with **Deep SORT**, so each object keeps the same ID over time.

## ✨ Features

- Video input from a **webcam** or a **video file** (OpenCV)
- Detection with a **pre-trained YOLOv8** model (80 COCO classes: person, car, dog…)
- Multi-object tracking with **Deep SORT** (persistent IDs)
- Live display of **bounding boxes, class labels and tracking IDs**
- Movement **trails**, FPS counter, number of tracked objects and unique IDs
- Save the annotated video (`--output`) and filter classes (`--classes`)
- Speed control with `--imgsz` for computers without a GPU

## 🛠️ Tech Stack

| Purpose | Tool |
|---|---|
| Video capture & display | OpenCV |
| Object detection | Ultralytics YOLOv8 |
| Object tracking | Deep SORT (`deep-sort-realtime`) |
| Language | Python 3.9+ |

## 📁 Project Structure

```
CodeAlpha_ObjectDetectionTracking/
├── main.py             # Detection + tracking + display pipeline
├── test_pipeline.py    # Self-test on a generated video (no webcam needed)
├── requirements.txt
└── README.md
```

## 🚀 Installation & Usage

```bash
git clone https://github.com/<aminaelbayyadi>/CodeAlpha_ObjectDetectionTracking.git
cd CodeAlpha_ObjectDetectionTracking
pip install -r requirements.txt

python test_pipeline.py                                   # self-test
python main.py --source 0                                 # webcam
python main.py --source video.mp4 --output result.mp4     # video file + save
python main.py --source 0 --classes person car --imgsz 416
```

Press **`q`** or **`Esc`** to quit. The `yolov8n.pt` weights are downloaded automatically on the first run.

### Options

| Option | Description | Default |
|---|---|---|
| `--source` | `0` for webcam, or a video file path | `0` |
| `--model` | `yolov8n.pt` (fast) … `yolov8x.pt` (accurate) | `yolov8n.pt` |
| `--conf` | Detection confidence threshold | `0.4` |
| `--classes` | Keep only some classes, e.g. `person car` | all |
| `--imgsz` | Analysis size (320/416 = faster) | `640` |
| `--max-age` | Frames an object can be lost before its ID is dropped | `30` |
| `--output` | Save the annotated video | – |
| `--no-show` | Do not open a window (servers) | off |

## ⚙️ How It Works

```
Webcam / video → YOLOv8 detection → Deep SORT tracking → boxes + labels + IDs on screen
```

1. **Detection**: YOLOv8 finds objects in each frame (box, class, confidence).
2. **Tracking**: Deep SORT matches detections to existing tracks using motion (Kalman filter) and appearance (embeddings), and assigns a stable ID.
3. **Display**: each confirmed track is drawn with its label, ID and trail.

## 🩺 Troubleshooting

| Problem | Solution |
|---|---|
| `No module named 'pkg_resources'` | `pip install "setuptools<81"` |
| `pkg_resources is deprecated` warning | Harmless, can be ignored |
| `Camera index out of range` / no webcam found | Allow desktop apps to use the camera in Windows privacy settings, close Zoom/Teams, or use a video file |
| Low FPS on CPU | Use `--imgsz 320` or a shorter video |

## 👩‍💻 Author

**Amina ELBAYYADI** – Master’s Degree in Big Data & AI
LinkedIn: `<https://www.linkedin.com/in/amina-elbayyadi/>`

---
*Developed as part of the CodeAlpha Artificial Intelligence Internship.*
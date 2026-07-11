"""
wildnode_ai/vision_detection/webcam_detect.py
===============================================
PURPOSE: Run REAL YOLO detection on your built-in PC webcam or external camera.
         Streams live frames and shows bounding boxes in real time.

HOW TO RUN:
  python vision_detection/webcam_detect.py              # Default camera (index 0)
  python vision_detection/webcam_detect.py --camera 1   # Second camera

CONTROLS (in the popup window):
  Q or ESC → Quit

REQUIREMENTS:
  pip install ultralytics opencv-python
"""

import os
import sys
import argparse
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision_detection.wildlife_detector import (
    detect_agricultural_pests,
    draw_detections_on_frame
)


def run_webcam_detection(camera_index: int = 0,
                          conf_threshold: float = 0.40,
                          max_frames: int = None):
    """
    Run real-time YOLO detection from webcam using the centralized detector.

    Args:
        camera_index   : 0 = default webcam, 1 = second camera
        conf_threshold : Min confidence for showing detection
        max_frames     : Stop after N frames (None = run until Q pressed)
    """
    try:
        import cv2
    except ImportError:
        print("[ERROR] Missing dependencies! Run:\n  pip install opencv-python")
        return

    print(f"[INFO] Opening camera {camera_index}...")

    # Thread-safe fast video capturer to prevent frame lag
    class FastVideoCapture:
        def __init__(self, src):
            if isinstance(src, int) or str(src).isdigit():
                self.cap = cv2.VideoCapture(int(src), cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(src)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.ret = False
            self.frame = None
            self.running = True
            if self.cap.isOpened():
                self.ret, self.frame = self.cap.read()
                self.t = threading.Thread(target=self._update, daemon=True)
                self.t.start()

        def _update(self):
            while self.running:
                ret, frame = self.cap.read()
                self.ret = ret
                if ret:
                    self.frame = frame
                else:
                    break

        def read(self):
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

        def get(self, propId):
            return self.cap.get(propId)

        def isOpened(self):
            return self.cap.isOpened()

        def release(self):
            self.running = False
            self.cap.release()

    cap = FastVideoCapture(camera_index)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {camera_index}.")
        print("  Make sure your webcam is connected and not used by another app.")
        return

    # Get camera properties
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30
    print(f"[INFO] Camera: {width}x{height} @ {fps:.0f}fps")
    print("[INFO] Loading central YOLO/YOLO-World model...")
    print("[INFO] Press Q or ESC in the popup video window to quit\n")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame.")
            break

        frame_count += 1

        # Run centralized AI detection (handles custom, world, or coco maps)
        detections = detect_agricultural_pests(frame, conf_threshold=conf_threshold)

        # Draw detections on frame using central draw utility
        annotated = draw_detections_on_frame(frame, detections)

        # Overlay: WildNode header bar
        overlay = annotated.copy()
        cv2.rectangle(overlay, (0, 0), (width, 36), (10, 20, 40), -1)
        annotated = cv2.addWeighted(overlay, 0.7, annotated, 0.3, 0)
        
        wildlife_found = [d["class"] for d in detections]
        status = f"  WildNode AI | Frame #{frame_count} | Threats: {', '.join(wildlife_found) or 'None'}"
        cv2.putText(annotated, status, (6, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 220, 255), 1)

        cv2.imshow("WildNode AI – Live Detection (Q to quit)", annotated)

        # Print console output for detected wildlife
        if detections:
            print(f"[Frame {frame_count:04d}] 🚨 PESTS DETECTED: {wildlife_found}")

        # Exit on Q or ESC
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break

        if max_frames and frame_count >= max_frames:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[✓] Webcam session ended. Total frames processed: {frame_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WildNode AI – Webcam Real-Time Detector")
    parser.add_argument("--camera", type=int,   default=0,    help="Camera index (default: 0)")
    parser.add_argument("--conf",   type=float, default=0.40, help="Confidence threshold")
    args = parser.parse_args()

    run_webcam_detection(camera_index=args.camera, conf_threshold=args.conf)

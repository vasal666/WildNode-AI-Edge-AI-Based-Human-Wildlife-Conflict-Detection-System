"""
wildnode_ai/vision_detection/image_detect.py
============================================
PURPOSE: Run REAL YOLO detection on a single image file using the centralized
         multi-model wildlife_detector wrapper.

HOW TO RUN:
  python vision_detection/image_detect.py --image path/to/image.jpg
  python vision_detection/image_detect.py --image path/to/photo.jpg --show

REQUIREMENTS:
  pip install ultralytics opencv-python pillow
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision_detection.wildlife_detector import (
    detect_agricultural_pests,
    draw_detections_on_frame
)


def run_real_detection(image_path: str,
                       save_output: bool = True,
                       conf_threshold: float = 0.35) -> list:
    """
    Run real YOLO inference on an image file using wildlife_detector.py.

    Args:
        image_path     : Path to image (.jpg / .png / .webp)
        save_output    : Save annotated image with bounding boxes
        conf_threshold : Minimum confidence to show a detection

    Returns:
        detections : List of standardized detection dicts
    """
    try:
        import cv2
    except ImportError:
        print("[ERROR] Missing dependencies! Run:\n  pip install opencv-python")
        return []

    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return []

    print(f"[INFO] Running Centralized AI Detector on: {image_path}")
    print(f"[INFO] Confidence threshold: {conf_threshold}")

    # Run central model inference (handles custom model, YOLO-World, or COCO fallbacks)
    detections = detect_agricultural_pests(image_path, conf_threshold=conf_threshold)

    # If detections found, print and optionally draw/save
    if not detections:
        print("\n[RESULT] No agricultural threats detected in this image.")
        return []

    print(f"\n[RESULT] Found {len(detections)} object(s):\n")

    # Read frame to draw boxes on it
    frame = cv2.imread(image_path)

    for det in detections:
        label = det["label"]
        confidence = det["confidence"]
        bbox = det["bbox"]
        threat = det["threat_level"]
        damage = det["crop_damage"]
        action = det["action"]

        print(f"  {'🚨' if threat in ('CRITICAL', 'HIGH') else '📡'} {label}")
        print(f"     Confidence   : {confidence*100:.1f}%")
        print(f"     Threat Level : {threat}")
        print(f"     Crop Damage  : {damage}")
        print(f"     Action       : {action}")
        print(f"     Bounding box : {bbox}")
        print()

    # Draw boxes and save
    if save_output and frame is not None:
        annotated = draw_detections_on_frame(frame, detections)
        out_path = image_path.rsplit(".", 1)[0] + "_detected.jpg"
        cv2.imwrite(out_path, annotated)
        print(f"[✓] Annotated image saved: {out_path}")

    return detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WildNode AI – Real Image Detector")
    parser.add_argument("--image", required=True, help="Path to image file")
    parser.add_argument("--conf",  type=float, default=0.35, help="Confidence threshold")
    parser.add_argument("--show",  action="store_true", help="Display image window")
    parser.add_argument("--no-save", action="store_true", help="Don't save annotated image")
    args = parser.parse_args()

    detections = run_real_detection(
        args.image,
        save_output=not args.no_save,
        conf_threshold=args.conf
    )

    if args.show and detections:
        try:
            import cv2
            img = cv2.imread(args.image)
            # If we saved it, load the annotated one to show
            out_path = args.image.rsplit(".", 1)[0] + "_detected.jpg"
            if not args.no_save and os.path.exists(out_path):
                img = cv2.imread(out_path)

            cv2.imshow("WildNode AI – Detection", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"[WARN] Cannot show image: {e}")

"""
wildnode_ai/vision_detection/wildlife_detector.py
===================================================
PURPOSE: Agricultural pest wildlife detector using YOLO-World open-vocabulary model.

YOLO-World lets you define ANY class names as text prompts — no retraining needed.
We use this to detect 14 agricultural pest animals that affect crops in India/Africa.

DETECTED CLASSES (Agricultural Pest Focus):
  HIGH THREAT (Crop Destroyers):
    - elephant       → Destroys crops, breaks fences, kills people
    - wild boar      → Destroys roots, burrows under crops
    - nilgai         → Blue Bull, major crop pest in India
    - deer           → Spotted/Sambar deer, grazes crops
    - monkey         → Langur/Macaque, raids fruit crops

  MEDIUM THREAT (Livestock/Boundary Risk):
    - leopard        → Attacks livestock
    - bear           → Raids orchards, honeybee farms
    - wolf           → Attacks livestock
    - hyena          → Attacks livestock, scavenges

  MONITOR (Wildlife Presence):
    - peacock        → Grazes crops
    - rabbit         → Grazes crops
    - fox            → Attacks poultry
    - zebra          → Grazes (Africa)
    - giraffe        → Grazes (Africa)

FALLBACK: If YOLO-World is unavailable, falls back to improved COCO-based YOLO11m
          with corrected class mappings (no more cat=tiger nonsense).

REQUIREMENTS:
  pip install ultralytics
"""

import os
import sys
import random
import warnings
warnings.filterwarnings("ignore")

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Agricultural Pest Animal Definitions ────────────────────────────────────
# These are the EXACT text prompts sent to YOLO-World
AGRICULTURAL_PEST_CLASSES = [
    # HIGH THREAT — Crop Destroyers
    "elephant",
    "wild boar",
    "nilgai",
    "deer",
    "monkey",
    "tiger",
    "lion",
    # MEDIUM THREAT — Livestock/Boundary Risk
    "leopard",
    "bear",
    "wolf",
    "hyena",
    # MONITOR — Wildlife Presence
    "peacock",
    "rabbit",
    "fox",
    "zebra",
    "giraffe",
]

# ─── Per-Animal Metadata ──────────────────────────────────────────────────────
ANIMAL_METADATA = {
    "elephant": {
        "emoji": "🐘", "threat_level": "CRITICAL",
        "crop_damage": "Tramples and eats entire crop fields, breaks irrigation systems",
        "action": "IMMEDIATE: Alert rangers. Deploy heavy deterrents. Evacuate area.",
        "agricultural_impact": 1.00,
        "coco_fallback": None,   # Native COCO class
        "color_bgr": (0, 80, 255),  # Orange-red
    },
    "wild boar": {
        "emoji": "🐗", "threat_level": "HIGH",
        "crop_damage": "Uproots tubers, rice, maize. Damages irrigation channels",
        "action": "Deploy sound deterrents. Reinforce fence perimeter.",
        "agricultural_impact": 0.85,
        "coco_fallback": "cow",   # rough fallback
        "color_bgr": (100, 0, 200),  # Purple
    },
    "nilgai": {
        "emoji": "🦌", "threat_level": "HIGH",
        "crop_damage": "Major pest in India — grazes wheat, paddy, sugarcane extensively",
        "action": "Install fence barriers. Contact forest department.",
        "agricultural_impact": 0.80,
        "coco_fallback": "horse",  # rough fallback by size
        "color_bgr": (0, 180, 255),  # Yellow
    },
    "deer": {
        "emoji": "🦌", "threat_level": "MEDIUM",
        "crop_damage": "Grazes wheat, vegetables, fruits. Antler damage to young trees",
        "action": "Increase patrol frequency. Install motion lights.",
        "agricultural_impact": 0.60,
        "coco_fallback": None,
        "color_bgr": (0, 160, 120),  # Teal
    },
    "monkey": {
        "emoji": "🐒", "threat_level": "MEDIUM",
        "crop_damage": "Raids mango, banana, coconut orchards. Damages stored grain",
        "action": "Sound alarms. Contact primate management team.",
        "agricultural_impact": 0.55,
        "coco_fallback": None,
        "color_bgr": (200, 120, 0),  # Blue
    },
    "tiger": {
        "emoji": "🐅", "threat_level": "CRITICAL",
        "crop_damage": "Direct predator threat to humans and livestock in the area",
        "action": "IMMEDIATE: Safe shelter. Alert forest department. Deploy light flares.",
        "agricultural_impact": 0.95,
        "coco_fallback": "cat",
        "color_bgr": (0, 100, 255),
    },
    "lion": {
        "emoji": "🦁", "threat_level": "CRITICAL",
        "crop_damage": "Direct predator threat to humans and livestock",
        "action": "IMMEDIATE: Secure livestock. Call emergency rangers. Avoid open areas.",
        "agricultural_impact": 0.98,
        "coco_fallback": "cat",
        "color_bgr": (0, 60, 255),
    },
    "leopard": {
        "emoji": "🐆", "threat_level": "HIGH",
        "crop_damage": "Attacks livestock (cattle, goats, dogs)",
        "action": "Secure livestock immediately. Alert forest rangers.",
        "agricultural_impact": 0.75,
        "coco_fallback": "cat",  # rough fallback
        "color_bgr": (0, 40, 255),  # Red
    },
    "bear": {
        "emoji": "🐻", "threat_level": "HIGH",
        "crop_damage": "Raids orchards, beehives, maize fields",
        "action": "Do not approach. Deploy electric fence. Call rangers.",
        "agricultural_impact": 0.72,
        "coco_fallback": "bear",  # Native COCO
        "color_bgr": (0, 0, 200),  # Dark red
    },
    "wolf": {
        "emoji": "🐺", "threat_level": "MEDIUM",
        "crop_damage": "Attacks sheep, goats, calves. Significant livestock loss",
        "action": "Secure livestock. Guard dogs recommended. Alert rangers.",
        "agricultural_impact": 0.65,
        "coco_fallback": "dog",  # rough fallback
        "color_bgr": (100, 100, 150),  # Gray-blue
    },
    "hyena": {
        "emoji": "🦡", "threat_level": "MEDIUM",
        "crop_damage": "Attacks livestock at night. Scavenges farm animals",
        "action": "Secure pens at dusk. Motion-activated lights advised.",
        "agricultural_impact": 0.60,
        "coco_fallback": "dog",
        "color_bgr": (80, 80, 80),  # Gray
    },
    "peacock": {
        "emoji": "🦚", "threat_level": "LOW",
        "crop_damage": "Grazes grain crops. Can damage young plants",
        "action": "Log and monitor. Net covers for vulnerable crops.",
        "agricultural_impact": 0.25,
        "coco_fallback": "bird",
        "color_bgr": (200, 180, 0),  # Teal-blue
    },
    "rabbit": {
        "emoji": "🐰", "threat_level": "LOW",
        "crop_damage": "Burrows, grazes vegetables, root crops",
        "action": "Install wire mesh. Monitor population.",
        "agricultural_impact": 0.20,
        "coco_fallback": None,
        "color_bgr": (180, 180, 180),  # Light gray
    },
    "fox": {
        "emoji": "🦊", "threat_level": "LOW",
        "crop_damage": "Attacks poultry. Steals eggs and small animals",
        "action": "Secure poultry coops. Check for burrows.",
        "agricultural_impact": 0.30,
        "coco_fallback": "dog",
        "color_bgr": (0, 100, 220),  # Orange
    },
    "zebra": {
        "emoji": "🦓", "threat_level": "LOW",
        "crop_damage": "Grazes open farmland (common in Africa)",
        "action": "Monitor and log. Ensure safe wildlife corridor.",
        "agricultural_impact": 0.35,
        "coco_fallback": "zebra",  # Native COCO
        "color_bgr": (220, 220, 220),
    },
    "giraffe": {
        "emoji": "🦒", "threat_level": "LOW",
        "crop_damage": "Browses tree crops, can topple power lines",
        "action": "Monitor and log. Prevent traffic collision.",
        "agricultural_impact": 0.20,
        "coco_fallback": "giraffe",  # Native COCO
        "color_bgr": (0, 200, 255),
    },
}

# Threat level grouping
HIGH_THREAT_ANIMALS  = {"elephant", "wild boar", "nilgai", "leopard", "bear", "tiger", "lion"}
MEDIUM_THREAT_ANIMALS = {"deer", "monkey", "wolf", "hyena"}
LOW_THREAT_ANIMALS   = {"peacock", "rabbit", "fox", "zebra", "giraffe"}

# ─── COCO Fallback Mappings (improved — no more cat=tiger nonsense) ───────────
# Maps COCO class names → our agricultural pest class (only where reasonable)
COCO_FALLBACK_MAP = {
    "elephant" : "elephant",   # Direct match
    "bear"     : "bear",       # Direct match
    "zebra"    : "zebra",      # Direct match
    "giraffe"  : "giraffe",    # Direct match
    "cow"      : "wild boar",  # Size-similar farm animal (flagged as approximate)
    "horse"    : "nilgai",     # Size-similar (flagged as approximate)
    "dog"      : "wolf",       # Canid family (flagged as approximate)
    "sheep"    : "deer",       # Small grazer (flagged as approximate)
    "bird"     : "peacock",    # Large bird (flagged as approximate)
    # cat and other non-wildlife COCO classes are intentionally EXCLUDED
}

# Classes that are approximate mappings (lower confidence applied)
APPROXIMATE_COCO_CLASSES = {"cow", "horse", "dog", "sheep", "bird"}

# ─────────────────────────────────────────────────────────────────────────────
# Model Cache
_yolo_world_model  = None
_yolo_coco_model   = None
_yolo_custom_model = None
_use_world_model   = None   # Cached decision on which model to use
_use_custom_model  = None   # Cached decision on whether to use custom model


def _try_load_yolo_world(model_name: str = "yolov8s-world.pt"):
    """
    Try to load YOLO-World model with agricultural pest class prompts.
    Returns (model, True) on success, (None, False) on failure.
    """
    global _yolo_world_model
    if _yolo_world_model is not None:
        return _yolo_world_model, True

    try:
        from ultralytics import YOLO
        print(f"[INFO] Loading YOLO-World model: {model_name}")
        model = YOLO(model_name)
        # Set agricultural pest classes as detection vocabulary
        model.set_classes(AGRICULTURAL_PEST_CLASSES)
        _yolo_world_model = model
        print(f"[✓] YOLO-World loaded! Detecting: {AGRICULTURAL_PEST_CLASSES}")
        return model, True
    except Exception as e:
        print(f"[WARN] YOLO-World unavailable: {e}. Using improved COCO fallback.")
        return None, False


def _try_load_coco_model(model_name: str = "yolo11m.pt"):
    """
    Load standard YOLOv8 COCO model as fallback.
    Uses the yolov8m.pt already downloaded in the project root.
    """
    global _yolo_coco_model
    if _yolo_coco_model is not None:
        return _yolo_coco_model

    try:
        from ultralytics import YOLO
        # Prefer the already-downloaded yolo11m.pt in project root
        root_model = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "yolo11m.pt"
        )
        path = root_model if os.path.exists(root_model) else model_name
        print(f"[INFO] Loading COCO fallback model: {path}")
        _yolo_coco_model = YOLO(path)
        print("[✓] COCO YOLO11m fallback model loaded.")
        return _yolo_coco_model
    except Exception as e:
        print(f"[ERROR] Cannot load any model: {e}")
        return None


def _try_load_custom_model():
    """
    Try to load the fine-tuned custom YOLO11 model.
    Looks for 'best.pt' in the root directory first, then in the training runs output.
    Returns (model, True) on success, (None, False) on failure.
    """
    global _yolo_custom_model
    if _yolo_custom_model is not None:
        return _yolo_custom_model, True

    try:
        from ultralytics import YOLO
        # Root path to best.pt
        root_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "best.pt"
        )
        # Fallback path in training runs
        runs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "training_pipeline", "runs", "detect", "wildnode_custom", "weights", "best.pt"
        )

        model_path = None
        if os.path.exists(root_path):
            model_path = root_path
        elif os.path.exists(runs_path):
            model_path = runs_path

        if model_path is None:
            return None, False

        print(f"[INFO] Loading custom fine-tuned YOLO model: {model_path}")
        _yolo_custom_model = YOLO(model_path)
        print("[✓] Custom YOLO model loaded successfully!")
        return _yolo_custom_model, True
    except Exception as e:
        print(f"[WARN] Custom YOLO model load failed: {e}")
        return None, False


def detect_agricultural_pests(
    source,
    conf_threshold: float = 0.35,
    prefer_world_model: bool = True,
) -> list:
    """
    Detect agricultural pest wildlife in an image/video frame.

    Automatically uses custom fine-tuned YOLO model if best.pt is available,
    otherwise uses YOLO-World (open-vocabulary) if available,
    falls back to improved COCO YOLO11m mapping if not.

    Args:
        source            : Image path (str), numpy array (BGR), or webcam index (int)
        conf_threshold    : Minimum confidence to include a detection (0.0–1.0)
        prefer_world_model: Use YOLO-World if custom model is not available (recommended)

    Returns:
        detections : List of dicts:
            {
              "class"             : "elephant",
              "label"             : "🐘 ELEPHANT (94.2%)",
              "confidence"        : 0.942,
              "bbox"              : [x1, y1, x2, y2],
              "threat_level"      : "CRITICAL",
              "agricultural_impact": 1.0,
              "crop_damage"       : "...",
              "action"            : "...",
              "model_type"        : "custom-yolo" | "yolo-world" | "coco-fallback",
              "is_approximate"    : False,
            }
    """
    global _use_custom_model, _use_world_model

    # Check if custom model is available and can be loaded
    if _use_custom_model is None:
        # Check if the custom model weights file exists
        root_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "best.pt"
        )
        runs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "training_pipeline", "runs", "detect", "wildnode_custom", "weights", "best.pt"
        )
        if os.path.exists(root_path) or os.path.exists(runs_path):
            _, custom_ok = _try_load_custom_model()
            _use_custom_model = custom_ok
        else:
            _use_custom_model = False

    if _use_custom_model:
        return _detect_with_custom_model(source, conf_threshold)

    # Determine which fallback model to use (cached after first call)
    if _use_world_model is None:
        if prefer_world_model:
            _, world_ok = _try_load_yolo_world()
            _use_world_model = world_ok
        else:
            _use_world_model = False

    if _use_world_model:
        return _detect_with_world_model(source, conf_threshold)
    else:
        return _detect_with_coco_fallback(source, conf_threshold)


def _detect_with_custom_model(source, conf_threshold: float) -> list:
    """Run detection using the fine-tuned custom YOLO model."""
    model, ok = _try_load_custom_model()
    if not ok or model is None:
        # Fallback if custom model couldn't be loaded or failed
        if _use_world_model:
            return _detect_with_world_model(source, conf_threshold)
        else:
            return _detect_with_coco_fallback(source, conf_threshold)

    try:
        results = model(source, conf=conf_threshold, verbose=False)
        detections = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id   = int(box.cls[0])
                class_name = result.names[class_id].lower()
                confidence = float(box.conf[0])
                bbox       = [int(v) for v in box.xyxy[0].tolist()]

                # Standardize 'wild_boar' to 'wild boar' to match ANIMAL_METADATA keys
                if class_name == "wild_boar":
                    class_name = "wild boar"

                # Match to our agricultural pest definitions
                meta = ANIMAL_METADATA.get(class_name)
                if meta is None:
                    continue

                detections.append(_build_detection(
                    class_name, confidence, bbox, meta,
                    model_type="custom-yolo", is_approximate=False
                ))

        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    except Exception as e:
        print(f"[ERROR] Custom YOLO model inference failed: {e}. Switching to world/fallback.")
        global _use_custom_model
        _use_custom_model = False
        if _use_world_model:
            return _detect_with_world_model(source, conf_threshold)
        else:
            return _detect_with_coco_fallback(source, conf_threshold)



def _detect_with_world_model(source, conf_threshold: float) -> list:
    """Run detection using YOLO-World with agricultural pest vocabulary."""
    model, ok = _try_load_yolo_world()
    if not ok or model is None:
        return _detect_with_coco_fallback(source, conf_threshold)

    try:
        results = model(source, conf=conf_threshold, verbose=False)
        detections = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id   = int(box.cls[0])
                class_name = result.names[class_id].lower()
                confidence = float(box.conf[0])
                bbox       = [int(v) for v in box.xyxy[0].tolist()]

                # Match to our agricultural pest definitions
                meta = ANIMAL_METADATA.get(class_name)
                if meta is None:
                    continue

                detections.append(_build_detection(
                    class_name, confidence, bbox, meta,
                    model_type="yolo-world", is_approximate=False
                ))

        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    except Exception as e:
        print(f"[ERROR] YOLO-World inference failed: {e}. Switching to fallback.")
        global _use_world_model
        _use_world_model = False
        return _detect_with_coco_fallback(source, conf_threshold)


def _detect_with_coco_fallback(source, conf_threshold: float) -> list:
    """Run detection using COCO YOLO11m with improved class mappings."""
    model = _try_load_coco_model()
    if model is None:
        return []

    # Use a slightly lower threshold for COCO since mappings are approximate
    effective_conf = max(0.45, conf_threshold)

    try:
        results = model(source, conf=effective_conf, verbose=False)
        detections = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id   = int(box.cls[0])
                coco_name  = result.names[class_id].lower()
                confidence = float(box.conf[0])
                bbox       = [int(v) for v in box.xyxy[0].tolist()]

                if coco_name not in COCO_FALLBACK_MAP:
                    continue

                wildlife_class = COCO_FALLBACK_MAP[coco_name]
                meta = ANIMAL_METADATA.get(wildlife_class)
                if meta is None:
                    continue

                is_approx = coco_name in APPROXIMATE_COCO_CLASSES
                # Penalise confidence for approximate mappings (less certain)
                adj_conf = confidence * 0.75 if is_approx else confidence

                detections.append(_build_detection(
                    wildlife_class, adj_conf, bbox, meta,
                    model_type="coco-fallback", is_approximate=is_approx
                ))

        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    except Exception as e:
        print(f"[ERROR] COCO fallback inference failed: {e}")
        return []


def _build_detection(class_name, confidence, bbox, meta,
                     model_type="yolo-world", is_approximate=False) -> dict:
    """Build a standardised detection dict."""
    emoji = meta["emoji"]
    approx_tag = " (approx)" if is_approximate else ""
    label = f"{emoji} {class_name.upper()}{approx_tag} ({confidence*100:.1f}%)"

    return {
        "class"              : class_name,
        "label"              : label,
        "confidence"         : round(confidence, 3),
        "bbox"               : bbox,
        "threat_level"       : meta["threat_level"],
        "agricultural_impact": meta["agricultural_impact"],
        "crop_damage"        : meta["crop_damage"],
        "action"             : meta["action"],
        "emoji"              : emoji,
        "color_bgr"          : meta["color_bgr"],
        "model_type"         : model_type,
        "is_approximate"     : is_approximate,
        # Legacy fields for compatibility with existing decision engine
        "class"              : class_name,
        "priority"           : meta["threat_level"],
    }


def draw_detections_on_frame(frame, detections: list) -> any:
    """
    Draw agricultural pest detection boxes on a CV2 frame.
    Uses color-coded boxes based on threat level.

    Args:
        frame      : BGR numpy array
        detections : List from detect_agricultural_pests()

    Returns:
        frame      : Annotated BGR numpy array
    """
    try:
        import cv2
    except ImportError:
        return frame

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        color = det.get("color_bgr", (0, 255, 0))
        label = det["label"]
        threat = det.get("threat_level", "LOW")

        # Box thickness by threat level
        thickness = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 2, "LOW": 1}.get(threat, 1)

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        # Label background
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
        cv2.putText(frame, label, (x1 + 3, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Threat badge in bottom-right of box
        threat_badge = f"[{threat}]"
        cv2.putText(frame, threat_badge, (x1 + 3, y2 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (255, 255, 255), 1, cv2.LINE_AA)

    return frame


# ─── Simulation (for dashboard when no camera/model available) ────────────────

def simulate_wildlife_detection(weights: dict = None) -> list:
    """
    Generate realistic simulated agricultural pest detection.
    Weighted toward the most common crop-damaging animals.

    Args:
        weights : Optional dict {class_name: weight} to bias simulation

    Returns:
        detections : List in same format as detect_agricultural_pests()
    """
    default_weights = {
        "elephant" : 15,   # High chance — biggest threat
        "wild boar": 20,   # Most common crop pest
        "nilgai"   : 15,   # Very common in India
        "deer"     : 12,
        "monkey"   : 12,
        "leopard"  : 5,
        "bear"     : 5,
        "wolf"     : 4,
        "peacock"  : 8,
        "rabbit"   : 4,
    }
    w = weights or default_weights
    classes  = list(w.keys())
    wts      = list(w.values())

    # 35% no detection, 45% one animal, 20% two animals
    n_det = random.choices([0, 1, 2], weights=[35, 45, 20])[0]
    if n_det == 0:
        return []

    chosen = random.choices(classes, weights=wts, k=n_det)
    chosen = list(dict.fromkeys(chosen))   # deduplicate

    detections = []
    for cls in chosen:
        meta = ANIMAL_METADATA.get(cls)
        if meta is None:
            continue
        confidence = round(random.uniform(0.55, 0.96), 3)
        x1, y1 = random.randint(30, 280), random.randint(30, 180)
        x2 = x1 + random.randint(100, 250)
        y2 = y1 + random.randint(80, 200)
        detections.append(_build_detection(
            cls, confidence, [x1, y1, x2, y2], meta,
            model_type="simulation", is_approximate=False
        ))

    return detections


# ─── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  WildNode AI – Agricultural Pest Wildlife Detector")
    print("=" * 60)
    print(f"\n  Model: YOLO-World (open vocabulary)")
    print(f"  Monitoring {len(AGRICULTURAL_PEST_CLASSES)} agricultural pest classes:")
    for cls in AGRICULTURAL_PEST_CLASSES:
        meta = ANIMAL_METADATA[cls]
        print(f"    {meta['emoji']} {cls:<12} | Threat: {meta['threat_level']:<8} | "
              f"Impact: {meta['agricultural_impact']:.0%}")

    print("\n  Running simulation test...")
    results = simulate_wildlife_detection()
    if results:
        for r in results:
            print(f"\n  ✓ {r['label']}")
            print(f"    Threat  : {r['threat_level']}")
            print(f"    Damage  : {r['crop_damage']}")
            print(f"    Action  : {r['action']}")
    else:
        print("  ✓ No wildlife detected (clear field)")
    print("=" * 60)

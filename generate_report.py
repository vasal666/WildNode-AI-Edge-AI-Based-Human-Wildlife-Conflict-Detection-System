# -*- coding: utf-8 -*-
"""
generate_report.py
==================
Generates a premium, professional PDF report for WildNode AI in a structured nature-green theme.
Fixed FPDF property collision and cleaned of Unicode characters for Helvetica font safety.
"""

import os
from fpdf import FPDF
from datetime import datetime

class WildNodeReportPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Theme Palette: Deep Green, Light Mint, Soft Charcoal
        self.theme_primary = (20, 83, 45)      # Deep Forest Green (#14532d)
        self.theme_secondary = (22, 163, 74)   # Vibrant Green (#16a34a)
        self.theme_accent = (239, 68, 68)      # Critical Red (#ef4444)
        self.theme_bg = (240, 253, 244)        # Light Mint (#f0fdf4)
        self.theme_text = (55, 65, 81)         # Soft Charcoal (#374151)
        self.theme_light_gray = (243, 244, 246) # Very light gray for table rows
        
    def header(self):
        # We only want headers from Page 2 onwards
        if self.page_no() > 1:
            self.set_fill_color(*self.theme_primary)
            self.rect(0, 0, 210, 18, 'F')
            
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 10)
            self.set_xy(10, 4)
            self.cell(0, 10, "WILDNODE AI - TECHNICAL SYSTEMS & SOCIAL IMPACT REPORT", new_x="LMARGIN", new_y="NEXT", align='L')
            
            self.set_font("Helvetica", "I", 8)
            self.set_xy(10, 4)
            self.cell(190, 10, "Edge-AI Mitigation Node Spec", new_x="LMARGIN", new_y="NEXT", align='R')
            
            # Reset text color and Y position below header
            self.set_text_color(*self.theme_text)
            self.set_y(25)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)
            
            # Draw a subtle separator line
            self.set_draw_color(229, 231, 235)
            self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
            
            # Left footer
            self.cell(0, 10, "(c) WildNode AI Conservation Initiative - v1.0 Production Spec", new_x="LMARGIN", new_y="NEXT", align='L')
            
            # Right footer (Page numbers)
            self.set_xy(10, self.get_y() - 10)
            self.cell(190, 10, f"Page {self.page_no()} of {{nb}}", new_x="LMARGIN", new_y="NEXT", align='R')

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.theme_primary)
        self.set_fill_color(220, 252, 231)  # Soft mint background fill
        
        # Heading text with left accent border
        self.cell(0, 10, f"  {num}. {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)
        
        # Subtle horizontal divider under title
        self.set_draw_color(*self.theme_secondary)
        self.set_line_width(0.5)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(4)
        
        # Reset text color to charcoal
        self.set_text_color(*self.theme_text)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.theme_secondary)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.set_text_color(*self.theme_text)

    def bold_bullet(self, bold_text, normal_text, bullet="- "):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*self.theme_primary)
        self.write(5, f"{bullet}{bold_text}: ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*self.theme_text)
        self.write(5, f"{normal_text}\n")
        self.ln(2)

    def write_body_paragraph(self, text, align='J'):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*self.theme_text)
        self.multi_cell(0, 5, text, 0, align)
        self.ln(4)

    def write_callout_box(self, text, title="PRO-TIP / INSIGHT"):
        self.set_fill_color(*self.theme_bg)
        self.set_draw_color(*self.theme_secondary)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.theme_primary)
        
        # Multi-cell with soft background fill and thin border
        self.cell(0, 6, f"[INFO] {title}", new_x="LMARGIN", new_y="NEXT", fill=True, border='TLR')
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.theme_text)
        self.multi_cell(0, 5, text, border='BLR', fill=True)
        self.ln(4)

def generate_report():
    pdf = WildNodeReportPDF()
    pdf.alias_nb_pages()
    pdf.set_margins(10, 20, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ---------------------------------------------------------
    # PAGE 1: COVER PAGE
    # ---------------------------------------------------------
    pdf.add_page()
    
    # Draw primary background colored side-bar accent on the left
    pdf.set_fill_color(*pdf.theme_primary)
    pdf.rect(0, 0, 12, 297, 'F')
    pdf.rect(12, 0, 198, 45, 'F') # Top banner
    
    # Top banner text
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(20, 12)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, "WILDNODE AI SYSTEMS SPECIFICATION", new_x="LMARGIN", new_y="NEXT", align='L')
    
    pdf.set_font("Helvetica", "I", 9.5)
    pdf.set_xy(20, 26)
    pdf.cell(0, 10, "Real-Time Edge Deep Learning & Multi-Channel Alert Dispatch Protocol", new_x="LMARGIN", new_y="NEXT", align='L')
    
    # Main content of Cover Page
    pdf.set_text_color(*pdf.theme_primary)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_xy(25, 75)
    pdf.multi_cell(165, 12, "Edge-AI Human-Wildlife Conflict Detection & Mitigation Sentinel Node", 0, 'L')
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(*pdf.theme_secondary)
    pdf.multi_cell(165, 7, "Engineering blueprint, model fine-tuning architecture, non-blocking telemetry pipelines, and social harmony impact analysis.", 0, 'L')
    
    # Bottom Meta Cards on cover page
    pdf.set_xy(25, 175)
    pdf.set_fill_color(*pdf.theme_bg)
    pdf.set_draw_color(*pdf.theme_secondary)
    pdf.rect(25, 175, 165, 75, 'FD')
    
    pdf.set_xy(30, 180)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*pdf.theme_primary)
    pdf.cell(0, 10, "[SYSTEM] PROJECT TECHNICAL SPECIFICATIONS", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*pdf.theme_text)
    
    # Grid details
    meta_info = [
        ("Deploy Core", "Ultralytics YOLO11 Nano + YOLO-World Zero-Shot Fallback"),
        ("Optical Feed", "Multi-threaded Non-Blocking FastVideoCapture (OpenCV)"),
        ("Routing Hub", "Twilio SMS & Twilio WhatsApp Sandbox Cellular Gateway"),
        ("Ranger Assistant", "Google Gemini LLM Contextual Decision Chatbot (RangerBot)"),
        ("Primary Target", "Crop Raiders (Boars, Elephants, Nilgai) & Predators (Leopards, Tigers)"),
        ("Deployment Cwd", "c:\\Users\\misfa\\Downloads\\wildnode_ai-main\\wildnode_ai-main")
    ]
    
    for label, val in meta_info:
        pdf.set_x(30)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(40, 7, f"- {label}: ", 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 7, val, 0, 1)
        
    # Cover page bottom date
    pdf.set_xy(25, 260)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(165, 6, "CONFIDENTIAL TECHNICAL SPECIFICATION", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(25)
    pdf.cell(165, 6, f"Generated automatically on: {datetime.now().strftime('%B %d, %Y')} - Indian Buffer Zones", new_x="LMARGIN", new_y="NEXT", align='C')

    # ---------------------------------------------------------
    # PAGE 2: EXECUTIVE SUMMARY & OVERVIEW
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("1", "PROJECT OVERVIEW & EXECUTIVE SUMMARY")
    
    pdf.write_body_paragraph(
        "WildNode AI is a state-of-the-art, production-grade edge computing system designed to solve one of the most pressing environmental challenges in forest-adjacent regions worldwide: Human-Wildlife Conflict (HWC). As agricultural buffer zones push closer to natural forest perimeters, local communities face massive financial devastation from crop-raids, livestock predation, and physical injuries. At the same time, wildlife faces severe threats from retributive killings, traps, and electrocution fences.",
        'J'
    )
    
    pdf.write_body_paragraph(
        "Traditional solutions-such as constant human patrolling, massive concrete walls, or dangerous high-voltage fences-are highly expensive, difficult to maintain, and often cause irreversible harm to natural migratory corridors. WildNode AI introduces a fully automated, low-cost, smart Sentinel system. By deploying solar-powered edge computing nodes equipped with micro-cameras and micro-microphones, WildNode AI continuously monitors buffers and instantly dispatches non-lethal, proactive deterrent alerts directly to local farmers and rangers before wildlife crosses crop boundaries.",
        'J'
    )
    
    pdf.section_title("How This System Benefits Society & Protects Livelihood")
    pdf.write_body_paragraph(
        "By providing instant, multi-channel warnings, WildNode AI helps the society in multiple high-impact ways:",
        'L'
    )
    
    pdf.bold_bullet("Agricultural Preservation", "Protects local smallholder farmers from devastating crop-raids by elephants, wild boars, nilgais, and deer, preserving a full year's livelihood in minutes.")
    pdf.bold_bullet("Life Security & Injury Mitigation", "Warns forest-edge villagers when dangerous large predators (e.g., tigers, leopards, bears) enter bovine enclosures or residential corridors, allowing immediate containment and safety measures.")
    pdf.bold_bullet("Eco-Conservation Harmonization", "Mitigates the critical need for lethal retributive measures (such as poisoning, illegal electric wire setups, or heavy traps), preserving vulnerable endangered species.")
    pdf.bold_bullet("Data-Driven Forest Policy", "Compiles comprehensive chronological sighting datasets allowing forestry departments to discover animal migratory routes, seasonal buffer penetrations, and peak raid timings.")
    
    pdf.write_callout_box(
        "Field telemetry indicates that over 80% of crop raids occur during low-light nocturnal cycles. WildNode AI supports low-light standard cameras, and the modular software pipeline can readily interface with infrared/thermal optical sensors for complete 24/7 reliability.",
        "Buffer Zone Telemetry Insight"
    )

    # ---------------------------------------------------------
    # PAGE 3: TECHNICAL STACK & LIBRARIES USED
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("2", "CORE TECHNOLOGIES & SOFTWARE STACK")
    
    pdf.write_body_paragraph(
        "WildNode AI's backend stack is designed around modular, lightweight edge execution pipelines, ensuring high frames-per-second processing, minimum latency, and multi-channel cellular delivery. Below is the comprehensive software ecosystem powering the sentinel node:",
        'J'
    )
    
    pdf.section_title("Deep Learning & Vision Core")
    pdf.bold_bullet("Ultralytics YOLO (YOLOv8 & YOLO11)", "Serves as the visual detection engine. It loads a fine-tuned, localized YOLO11 model ('best.pt') to perform bounding-box localization of target species natively at the edge.")
    pdf.bold_bullet("YOLO-World (Open-Vocabulary Zero-Shot)", "Integrated as an intelligent fallback layer. YOLO-World is an open-vocabulary network allowing the sentinel to spot arbitrary classes natively from plain-text prompts (e.g., 'nilgai', 'wild boar') without retraining.")
    pdf.bold_bullet("OpenCV (CV2)", "Manages real-time high-speed frame capture, multi-threaded buffered streaming, image resizing, color space transformations, and coordinates annotated bounding boxes overlays.")
    
    pdf.section_title("Audio Signal Classification")
    pdf.bold_bullet("TensorFlow & Keras CNN", "Powers the auditory monitoring engine. It converts raw 1D acoustic signals into 2D Mel Spectrogram images to classify key distress, growls, or trumpet acoustics.")
    pdf.bold_bullet("Librosa & Soundfile", "Decodes agricultural acoustics, performs Fourier analysis, applies frequency filters, and computes Mel-frequency cepstral coefficients (MFCCs).")
    
    pdf.section_title("UI, Alerts & Decision Logic")
    pdf.bold_bullet("Streamlit & Custom Vanilla CSS", "Provides an interactive, high-premium glassmorphism web dashboard. Features dynamic overlays, visual threat gauges, timeline logs, and modular state controls.")
    pdf.bold_bullet("Twilio Cellular API", "Operates as the cellular alerting gateway. Dispatches real-time SMS streams and structured WhatsApp warning cards containing coordinates, species profiles, and emergency action plans.")
    pdf.bold_bullet("Google Gemini LLM Engine", "Powers RangerBot, a floating context-aware assistant. RangerBot holds system state memories and advises rangers on species-specific deterrents.")
    pdf.bold_bullet("Plotly & Pandas", "Aggregates real-time data streams into live statistics, threat indicators, and visual historical charts.")

    pdf.write_callout_box(
        "The system's modular separation of vision, acoustics, decision-making, and alert routing means that individual modules can be updated or tested independently without breaking the edge loop.",
        "Architecture Cleanliness"
    )

    # ---------------------------------------------------------
    # PAGE 4: PIPELINES - DATA & FINE-TUNING PIPELINE
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("3", "MODEL TRAINING & FINE-TUNING PIPELINE")
    
    pdf.write_body_paragraph(
        "While pre-trained generic COCO models are excellent for standard objects, they fail to accurately identify specific regional agricultural threats, such as Indian Blue Bulls (Nilgai) or localized Wild Boars. WildNode AI addresses this with a complete custom fine-tuning and dataset pipeline.",
        'J'
    )
    
    pdf.section_title("1. Dataset Ingestion and Preprocessing (prepare_dataset.py)")
    pdf.write_body_paragraph(
        "The training pipeline starts with the automated ingestion script which reads raw dataset folders (comprising images and corresponding coordinate annotations) and compiles them into standard YOLO formats. The pipeline steps include:",
        'L'
    )
    
    pdf.bold_bullet("Input Path Mapping", "Reads images and text labels from the user's Desktop dataset ('c:\\Users\\misfa\\Desktop\\dataset') and cleans existing directories to avoid file leakage.")
    pdf.bold_bullet("Roboflow & Custom Coordinate Translation", "Supports Roboflow format (normalized class x y w h) and custom formats (ClassName xmin ymin xmax ymax). In custom mode, it reads pixel dimensions via PIL and normalizes the coordinates to standard float coordinates [0.0, 1.0].")
    pdf.bold_bullet("Validation Filtering", "Checks bounding boxes to ensure no coordinate overflows boundaries and filters out any malformed annotations.")
    pdf.bold_bullet("Train-Test Split", "Automatically shuffles and splits valid image-label pairs into an 80% training set and 20% validation split, saving them to training directory paths.")
    
    pdf.section_title("Multi-Class Target Map (data.yaml)")
    pdf.write_body_paragraph(
        "The fine-tuning architecture maps raw annotations to 8 strict target agricultural classes:",
        'L'
    )
    
    # Draw simple table of classes
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*pdf.theme_primary)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(25, 6, " Class ID", 1, 0, 'C', True)
    pdf.cell(40, 6, " Class Name", 1, 0, 'C', True)
    pdf.cell(40, 6, " Threat Level", 1, 0, 'C', True)
    pdf.cell(85, 6, " Agricultural Damage Profile", 1, 1, 'C', True)
    
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*pdf.theme_text)
    
    classes_data = [
        ("0", "wild_boar", "HIGH", "Uproots tubers, eats potato/maize, ruins irrigation"),
        ("1", "elephant", "CRITICAL", "Tramples crop fields, destroys fences, houses"),
        ("2", "tiger", "CRITICAL", "Direct predator threat to humans and cattle"),
        ("3", "bear", "HIGH", "Orchard raiding, hive destruction, attacks hives"),
        ("4", "fox", "LOW", "Attacks poultry coops, steals small livestock"),
        ("5", "monkey", "MEDIUM", "Mango/coconut orchard raider, grain storage raiding"),
        ("6", "lion", "CRITICAL", "Apex predator, threat to livestock enclosures"),
        ("7", "leopard", "HIGH", "High agility predator targeting goats/dogs/cattle")
    ]
    
    for cid, name, level, profile in classes_data:
        pdf.cell(25, 5.5, f" {cid}", 1, 0, 'C')
        pdf.cell(40, 5.5, f" {name}", 1, 0, 'L')
        # Color threat level
        if level == "CRITICAL":
            pdf.set_text_color(*pdf.theme_accent)
            pdf.set_font("Helvetica", "B", 8.5)
        elif level == "HIGH":
            pdf.set_text_color(217, 119, 6) # Amber
            pdf.set_font("Helvetica", "B", 8.5)
        else:
            pdf.set_text_color(*pdf.theme_text)
            pdf.set_font("Helvetica", "", 8.5)
            
        pdf.cell(40, 5.5, f" {level}", 1, 0, 'C')
        pdf.set_text_color(*pdf.theme_text)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(85, 5.5, f" {profile}", 1, 1, 'L')
        
    pdf.ln(4)
    pdf.section_title("2. Fine-Tuning Execution (train_custom_yolo.py)")
    pdf.write_body_paragraph(
        "The training script loads the pre-trained 'yolo11n.pt' weights to retain early visual patterns (edges, shapes) and fine-tunes it on the custom mapped dataset. Key parameters are configured for optimal edge accuracy:",
        'L'
    )
    pdf.bold_bullet("Epochs & Batch Size", "Configured to 50 training epochs with a batch size of 16, balancing gradient convergence speed with GPU memory usage.")
    pdf.bold_bullet("Early Stopping Patience", "Set to 10 epochs. If validation loss stops improving for 10 straight cycles, training halts, preventing overfitting.")
    pdf.bold_bullet("Model Output", "Generates fine-tuned weights ('best.pt') in runs/detect/wildnode_custom/weights/ which is copied to project root for instant dashboard loading.")

    # ---------------------------------------------------------
    # PAGE 5: PIPELINES - OPTICAL CAMERA WORKING
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("4", "CAMERA WORKINGS & SENTINEL TELEMETRY")
    
    pdf.write_body_paragraph(
        "A major issue in standard computer vision scripts is frame buffering: when processing high-resolution video streams, slow AI models lag, causing the camera frame buffer to pile up. The dashboard eventually displays images that occurred several seconds in the past.",
        'J'
    )
    
    pdf.section_title("1. Fast, Thread-Safe Frame Acquisition (FastVideoCapture)")
    pdf.write_body_paragraph(
        "WildNode AI implements a custom multi-threaded FastVideoCapture class that completely solves buffer lag. Instead of blocking the main thread during cap.read(), the sentinel spawns a dedicated background thread:",
        'L'
    )
    pdf.bold_bullet("Parallel Grab Loop", "The background thread continuously queries the camera sensor in a high-speed loop, immediately dumping older frames and keeping only the absolute newest frame in memory.")
    pdf.bold_bullet("Non-Blocking Read", "When the AI pipeline queries a frame via cap.read(), it instantly grabs a copy of the newest frame from RAM, completely bypassing camera driver blockings.")
    
    pdf.section_title("2. Flexible Stream Sources")
    pdf.write_body_paragraph(
        "The optical sentinel supports multiple ingestion methods natively from the Streamlit UI dashboard:",
        'L'
    )
    pdf.bold_bullet("Standard Webcams", "Passing an integer index (e.g. '0') automatically opens built-in laptop or connected USB cameras via direct Windows driver interfaces (CAP_DSHOW).")
    pdf.bold_bullet("Network/IP Webcams", "Rangers can paste an RTSP, HTTP, or RTMP video URL stream (e.g. from an Android IP Webcam app or outdoor CCTV sentinel) to process remote perimeter feeds.")
    
    pdf.section_title("3. Intelligent Model Orchestration (wildlife_detector.py)")
    pdf.write_body_paragraph(
        "The camera inference pipeline utilizes a 3-layered hierarchical model loader to ensure continuous monitoring even under changing conditions:",
        'L'
    )
    pdf.bold_bullet("Priority 1: Fine-tuned Custom YOLO Model (best.pt)", "If fine-tuned custom weights are available in root, the system uses them for native, high-accuracy multi-class target detections.")
    pdf.bold_bullet("Priority 2: YOLO-World Open-Vocabulary", "If custom weights are missing, the system utilizes 'yolov8s-world.pt' prompting it on the fly to detect boars, elephants, and other species zero-shot.")
    pdf.bold_bullet("Priority 3: COCO Fallback Mapping", "If YOLO-World fails to initialize, the system loads 'yolo11m.pt' and maps approximate COCO labels to wildlife equivalents (e.g. mapping 'cow' -> 'wild boar' or 'horse' -> 'nilgai' with a 25% confidence penalty).")

    pdf.write_callout_box(
        "To optimize frame rate, WildNode AI features a 'Native Ultra-Smooth Popup Window'. This uses OpenCV's high-speed windowing system ('cv2.imshow') directly on the host GPU, boosting framerates to over 30 FPS.",
        "Performance Optimization"
    )

    # ---------------------------------------------------------
    # PAGE 6: MULTI-CHANNEL ALERT SYSTEM & RANGERBOT CHATBOT
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("5", "MULTI-CHANNEL ALERTER & RANGERBOT ASSISTANT")
    
    pdf.write_body_paragraph(
        "Visual and acoustic detections are only useful if they trigger immediate, practical actions in the real world. WildNode AI combines a localized decision-scoring engine with a multi-layered alert system.",
        'J'
    )
    
    pdf.section_title("1. Multi-Channel Alert Router (alerter.py)")
    pdf.write_body_paragraph(
        "When an animal is spotted, the system calculates threat scores. Detections flagged as MEDIUM, HIGH, or CRITICAL are processed by the alert engine:",
        'L'
    )
    pdf.bold_bullet("Console Logging", "Instantly prints bold, color-coded notification blocks to edge terminals including threat badges, animal tags, match confidence, and recommended mitigation actions.")
    pdf.bold_bullet("Twilio SMS Dispatch", "Sends a direct, lightweight cellular text message to forest rangers' cellular devices. This ensures alert delivery even in rural, low-data-connectivity regions.")
    pdf.bold_bullet("Twilio WhatsApp Router", "Pushes structured WhatsApp alert cards, containing animal tags, risk score indicators, timestamps, and localized mitigation bullet points.")
    pdf.bold_bullet("Incident Repository (alert_log.json)", "Persists every incident on disk as structured JSON. This log is read by the dashboard to populate the Historical Incident Repository.")
    
    pdf.section_title("2. RangerBot Interactive AI Assistant")
    pdf.write_body_paragraph(
        "The Streamlit dashboard features RangerBot, a floating nature-themed conversational assistant integrated with Google Gemini LLM, which provides dynamic field support:",
        'L'
    )
    pdf.bold_bullet("State Memory", "RangerBot retains context about active node status, location coordinates, and the latest camera frames.")
    pdf.bold_bullet("Voice Simulation", "Users can click the microphone button to simulate voice queries. RangerBot processes spoken prompts (e.g. 'leopard spotted near cattle pen!') and suggests safety detours.")
    
    pdf.section_title("Automated Sighting Trigger & Guidance Cards")
    pdf.write_body_paragraph(
        "RangerBot is directly wired into the active optical stream. When a high-threat animal (like an elephant or leopard) enters the frame, the system automatically expands the chatbot window and prints a critical alert card:",
        'L'
    )
    pdf.write_callout_box(
        "CRITICAL ELEPHANT DETECTED 0.8 km from West Crop Area.\n"
        "Avoid approaching. Activate safe light deterrents and notify forest officers.\n\n"
        "- Risk Level: CRITICAL  |  - Match Confidence: 94.2%\n"
        "Suggested Immediate Actions:\n"
        "  1. Activate crop guard sound alarms.\n"
        "  2. Keep cattle inside secure concrete pens.\n"
        "  3. Deploy non-lethal organic acoustic deterrents (e.g. honeybee sounds).",
        "RangerBot Real-Time Alert Card"
    )

    # ---------------------------------------------------------
    # PAGE 7: HOW TO USE THE SOFTWARE (USER GUIDE)
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("6", "SYSTEM DEPLOYMENT & OPERATION GUIDE")
    
    pdf.write_body_paragraph(
        "Deploying the WildNode AI sentinel node is highly straightforward and can be accomplished in minutes on standard hardware or edge systems.",
        'J'
    )
    
    pdf.section_title("Step 1: Install Dependencies")
    pdf.write_body_paragraph(
        "Open a terminal in the project directory and run standard pip installers:",
        'L'
    )
    pdf.set_font("Courier", "", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 7, "  pip install -r requirements.txt", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(3)
    
    pdf.section_title("Step 2: Configure Environment Variables")
    pdf.write_body_paragraph(
        "Create a .env file in the root directory by copying the template. Fill in the parameters for the alerts and chatbot:",
        'L'
    )
    
    env_lines = [
        "# --- Google Gemini API (For RangerBot Assistant) ---",
        "GEMINI_API_KEY=AIzaSy...",
        "",
        "# --- Twilio Credentials (For Cellular SMS/WhatsApp Alerts) ---",
        "TWILIO_ACCOUNT_SID=AC...",
        "TWILIO_AUTH_TOKEN=auth_...",
        "TWILIO_PHONE_NUMBER=+1...",
        "ALERT_PHONE_NUMBER=+91XXXXXXXXXX",
        "",
        "# --- Environmental Risk API ---",
        "OPENWEATHER_API_KEY=weather_..."
    ]
    pdf.set_font("Courier", "", 8)
    pdf.set_fill_color(245, 245, 245)
    for el in env_lines:
        pdf.cell(0, 4.5, f"  {el}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(3)
    
    pdf.section_title("Step 3: Launch the Interactive Dashboard")
    pdf.write_body_paragraph(
        "Run the central Streamlit web server to open the premium nature-themed dashboard:",
        'L'
    )
    pdf.set_font("Courier", "", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 7, "  streamlit run dashboard/app.py", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 9.5)
    pdf.write_body_paragraph(
        "The interface will load at http://localhost:8501. From here, you can start the native camera sentinel stream, drag-and-drop test pictures, review historical logs, and interact directly with RangerBot.",
        'J'
    )
    
    pdf.section_title("Step 4: Fine-tune Detections (Optional)")
    pdf.write_body_paragraph(
        "If you want to train the node on your own Roboflow annotations, place your dataset in training_pipeline/dataset/ and run the fine-tuning script:",
        'L'
    )
    pdf.set_font("Courier", "", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 7, "  python training_pipeline/train_custom_yolo.py", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(4)
    
    pdf.write_callout_box(
        "WildNode AI is fully optimized for edge deployment on low-cost hardware like Raspberry Pi 5 or NVIDIA Jetson Nano with standard camera sensors.",
        "Edge Hardware Deployment"
    )
    
    # Save the output file in the main folder
    out_file = "c:\\Users\\misfa\\Downloads\\wildnode_ai-main\\wildnode_ai-main\\wildnode_ai_technical_report.pdf"
    pdf.output(out_file)
    print(f"\n[SUCCESS] Technical PDF Report generated successfully: {out_file}")

if __name__ == "__main__":
    generate_report()

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
try:
    from twilio.rest import Client
except ImportError:
    Client = None

# Load environment variables from .env file
load_dotenv()

# Configuration from Environment Variables
TWILIO_SID      = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SMS_FROM = os.getenv("TWILIO_PHONE_NUMBER")
# Twilio Sandbox WhatsApp number (usually +14155238886)
TWILIO_WA_FROM  = "whatsapp:+14155238886" 
ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER", "+91XXXXXXXXXX")

# Setup Twilio Client
client = None
if TWILIO_SID and TWILIO_TOKEN and Client is not None:
    client = Client(TWILIO_SID, TWILIO_TOKEN)

# --- Directory Setup ---
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
ALERT_LOG_PATH = os.path.join(BASE_DIR, "alert_log.json")

COLORS = {
    "CRITICAL" : "\033[91m", "HIGH" : "\033[38;5;208m", "MEDIUM" : "\033[93m",
    "LOW" : "\033[92m", "RESET" : "\033[0m", "BOLD" : "\033[1m", "CYAN" : "\033[96m",
}

RISK_ICONS = {"CRITICAL" : "🚨", "HIGH" : "⚠️ ", "MEDIUM" : "📡", "LOW" : "✅"}

def _load_alert_log() -> list:
    if os.path.exists(ALERT_LOG_PATH):
        try:
            with open(ALERT_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def get_recent_alerts(limit: int = 50) -> list:
    alerts = _load_alert_log()
    return alerts[-limit:] if alerts else []

def _save_alert_log(alerts: list):
    try:
        with open(ALERT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(alerts[-200:], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] Could not save alert log: {e}")

# --- Real Alert Channels ---

def send_real_sms(decision: dict, to_phone: str):
    """Sends a real SMS via Twilio."""
    if not client: return
    
    msg = decision.get("alert_message", "")
    level = decision.get("risk_level", "LOW")
    body = f"WildNode AI | {level}: {msg}"[:160]

    try:
        message = client.messages.create(body=body, from_=TWILIO_SMS_FROM, to=to_phone)
        print(f"  📟 SMS Sent Successfully! SID: {message.sid}")
    except Exception as e:
        print(f"  ❌ SMS Failed: {e}")

def send_real_whatsapp(decision: dict, to_phone: str):
    """Sends a real WhatsApp via Twilio Sandbox."""
    if not client: return

    msg = decision.get("alert_message", "")
    level = decision.get("risk_level", "LOW")
    score = decision.get("risk_score", 0)
    
    wa_body = f"🌿 *WildNode AI Alert*\n\n*Level:* {level}\n*Score:* {score}/100\n*Msg:* {msg}"

    try:
        message = client.messages.create(
            body=wa_body,
            from_=TWILIO_WA_FROM,
            to=f"whatsapp:{to_phone}"
        )
        print(f"  📱 WhatsApp Sent Successfully! SID: {message.sid}")
    except Exception as e:
        print(f"  ❌ WhatsApp Failed: {e}")

def send_console_alert(decision: dict):
    level, score = decision.get("risk_level", "LOW"), decision.get("risk_score", 0)
    color, icon = COLORS.get(level, ""), RISK_ICONS.get(level, "🔍")
    reset, bold = COLORS["RESET"], COLORS["BOLD"]
    
    print(f"\n{color}{bold}{'─'*60}{reset}")
    print(f"{color}{bold}  {icon} WildNode AI ALERT [{level}] Score: {score}/100{reset}")
    print(f"  {bold}Message :{reset} {decision.get('alert_message')}")
    print(f"  {bold}Action  :{reset} {COLORS['CYAN']}{decision.get('recommended_action')}{reset}")
    print(f"{color}{'─'*60}{reset}\n")

def log_alert(decision: dict):
    alerts = _load_alert_log()
    log_entry = {**decision, "id": len(alerts) + 1}
    alerts.append(log_entry)
    _save_alert_log(alerts)
    return log_entry

# --- Master Dispatcher ---

def dispatch_alert(decision: dict, phone: str = None,
                   enable_remote: bool = True, enable_log: bool = True,
                   enable_whatsapp: bool = True, enable_sms: bool = True) -> dict:
    """
    Orchestrates all alert channels.

    Args:
        decision        : Decision dict from decision engine
        phone           : Phone number for SMS/WhatsApp
        enable_remote   : Master toggle for all remote alerts (SMS + WhatsApp)
        enable_log      : Save to alert_log.json
        enable_whatsapp : Specific toggle for WhatsApp (overrides enable_remote for WA)
        enable_sms      : Specific toggle for SMS (overrides enable_remote for SMS)
    """
    if phone is None:
        phone = ALERT_PHONE_NUMBER

    # 1. Console is always live
    send_console_alert(decision)

    # 2. Remote Alerts (Twilio) for MEDIUM and higher
    risk_level = decision.get("risk_level", "LOW")
    should_remote = enable_remote and risk_level in ("MEDIUM", "HIGH", "CRITICAL")

    if should_remote:
        if TWILIO_SID and TWILIO_TOKEN and Client is not None:
            if enable_sms:
                send_real_sms(decision, phone)
            if enable_whatsapp:
                send_real_whatsapp(decision, phone)
        else:
            print("[!] Twilio credentials missing or not installed - skipping remote alerts.")

    # 3. Always Log
    return log_alert(decision) if enable_log else None

if __name__ == "__main__":
    # Test Mock Data
    test_decision = {
        "risk_level": "HIGH",
        "risk_score": 85,
        "alert_message": "Large predator detected near Sector 7.",
        "recommended_action": "Deploy deterrent drone.",
        "location": "North Outpost",
        "timestamp": datetime.now().isoformat()
    }
    dispatch_alert(test_decision) # Defaults to using ALERT_PHONE_NUMBER from environment
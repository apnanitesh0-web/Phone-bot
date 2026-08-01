#!/usr/bin/env python3
"""
Stylish Phone Info Bot with NumVerify API
- Handles /start with custom keyboard
- Formats NumVerify response with emojis and bold text
- Uses only requests, json, time
"""

import json
import time
import requests

# =========================== CONFIGURATION ===========================
BOT_TOKEN = "8967548495:AAGt5iQEjHhidU8uBroFGJ_dT9J7r6L2Bws"   # <-- YOUR BOT TOKEN
EXTERNAL_API_URL = "EXTERNAL_API_URL = "http://apilayer.net/api/validate?access_key=98bb927ae27c27c92ad2962de05ea087&num=""  # <-- NumVerify URL: http://apilayer.net/api/validate?access_key=KEY&num=

# =========================== TELEGRAM API ===========================
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None, timeout=30):
    url = f"{BASE_URL}/getUpdates"
    params = {'timeout': timeout, 'allowed_updates': ['message']}
    if offset:
        params['offset'] = offset
    try:
        r = requests.get(url, params=params, timeout=timeout+5)
        return r.json()
    except:
        return {'ok': False, 'result': []}

def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"{BASE_URL}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        return requests.post(url, json=payload, timeout=10).json()
    except:
        return {'ok': False}

# =========================== KEYBOARD ===========================
def get_keyboard():
    return {
        'keyboard': [[{'text': '📱 Phone Lookup'}]],
        'resize_keyboard': True
    }

# =========================== STYLISH FORMATTING ===========================
def format_numverify(data: dict) -> str:
    """NumVerify JSON को Stylish Message में बदलें"""
    if not data.get('valid'):
        return "❌ *Invalid phone number.*"
    
    # Extract fields with defaults
    number = data.get('number', 'N/A')
    country = data.get('country_name', 'N/A')
    location = data.get('location', 'N/A')
    carrier = data.get('carrier', 'N/A')
    line_type = data.get('line_type', 'N/A')
    country_code = data.get('country_code', 'N/A')
    international = data.get('international_format', 'N/A')
    
    # Build stylish output
    output = f"""╔{'═'*45}╗
║  📞  PHONE INTELLIGENCE  
╚{'═'*45}╝
║
├─ 📱 *Number*       : `{international}`
├─ 🌍 *Country*      : `{country} ({country_code})`
├─ 📍 *Location*     : `{location}`
├─ 📶 *Carrier*      : `{carrier}`
├─ 📊 *Line Type*    : `{line_type}`
├─ ✅ *Valid*        : `✅ Yes`
║
{'━'*47}
🔹 *Powered by NumVerify*"""
    return output

# =========================== BOT HANDLERS ===========================
def handle_start(chat_id):
    text = "👋 *Welcome to Stylish Phone Bot!*\n\nClick the button below to look up a number."
    send_message(chat_id, text, reply_markup=get_keyboard(), parse_mode='Markdown')

def handle_lookup(chat_id):
    text = "📞 *Send 10-digit mobile number:*"
    send_message(chat_id, text, reply_markup=get_keyboard(), parse_mode='Markdown')

def handle_number(chat_id, number):
    # Show processing
    send_message(chat_id, f"⏳ *Fetching details for* `{number}` ...", parse_mode='Markdown')
    
    # Call NumVerify API
    try:
        url = f"{EXTERNAL_API_URL}{number}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # Format stylishly
        if data.get('valid'):
            formatted = format_numverify(data)
        else:
            formatted = "❌ Invalid phone number."
    except Exception as e:
        formatted = f"❌ Error: `{str(e)}`"
    
    send_message(chat_id, formatted, reply_markup=get_keyboard(), parse_mode='Markdown')

def process_update(update):
    msg = update.get('message')
    if not msg:
        return
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    
    if text == '/start':
        handle_start(chat_id)
    elif text == '📱 Phone Lookup':
        handle_lookup(chat_id)
    elif text.isdigit() and len(text) == 10:
        handle_number(chat_id, text)
    else:
        send_message(chat_id, "⚠️ *Invalid input!* Use the button below.", reply_markup=get_keyboard(), parse_mode='Markdown')

# =========================== MAIN LOOP ===========================
def main():
    print("🚀 Stylish Bot started.")
    last_id = 0
    while True:
        try:
            updates = get_updates(offset=last_id + 1)
            if updates.get('ok'):
                for u in updates.get('result', []):
                    last_id = u['update_id']
                    process_update(u)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
    else:
        main()

#!/usr/bin/env python3
"""
Simple Telegram Bot with Long Polling (Manual API calls)
- Only uses requests, json, time
- No external libraries except requests
- Handles /start, custom keyboard, phone lookup
- Shows RAW API response inside <pre> tags
"""

import json
import time
import requests

# =========================== CONFIGURATION ===========================
# 🔑 Replace with your bot token from @BotFather
BOT_TOKEN = "8967548495:AAGt5iQEjHhidU8uBroFGJ_dT9J7r6L2Bws"   # <-- PUT YOUR TOKEN HERE

# 🌐 External API endpoint (leave blank if not needed)
EXTERNAL_API_URL = ""  # <-- PUT YOUR API URL HERE
# Example: "https://anishexploits.site/anish-exploits/api.php?key=demo-testing&num="

# =========================== TELEGRAM API ENDPOINTS ===========================
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset=None, timeout=30):
    """Fetch new updates from Telegram."""
    url = f"{BASE_URL}/getUpdates"
    params = {
        'timeout': timeout,
        'allowed_updates': ['message']
    }
    if offset is not None:
        params['offset'] = offset
    try:
        response = requests.get(url, params=params, timeout=timeout + 5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] get_updates failed: {e}")
        return {'ok': False, 'result': []}

def send_message(chat_id, text, reply_markup=None, parse_mode='HTML'):
    """Send a text message to a chat."""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERROR] send_message failed: {e}")
        return {'ok': False}

# =========================== KEYBOARD ===========================
def get_main_keyboard():
    """Return custom reply keyboard."""
    return {
        'keyboard': [
            [{'text': '📱 Phone Lookup'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }

# =========================== BOT LOGIC ===========================
def handle_start(chat_id):
    """Handle /start command."""
    text = (
        "👋 *Welcome to the Phone Info Bot!*\n\n"
        "Click the button below to look up a phone number."
    )
    send_message(chat_id, text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

def handle_phone_lookup(chat_id):
    """Ask user for 10-digit mobile number."""
    text = "📞 *Send 10 digit mobile number:*"
    send_message(chat_id, text, reply_markup=get_main_keyboard(), parse_mode='Markdown')

def handle_phone_number(chat_id, phone_number):
    """
    Process the phone number: call external API and show RAW JSON response.
    """
    # Show "processing" message
    send_message(chat_id, f"⏳ *Fetching details for* `{phone_number}` ...", parse_mode='Markdown')

    # Call external API
    try:
        if EXTERNAL_API_URL:
            url = f"{EXTERNAL_API_URL}{phone_number}"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Format response with <pre> tags (RAW JSON)
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            response_text = f"<b>📊 API Response:</b>\n<pre>{formatted_json}</pre>"
        else:
            response_text = "⚠️ External API URL is not configured."
    except Exception as e:
        response_text = f"❌ Error calling external API:\n<pre>{str(e)}</pre>"

    # Send the formatted response
    send_message(chat_id, response_text, reply_markup=get_main_keyboard(), parse_mode='HTML')

def process_update(update):
    """Process a single update."""
    message = update.get('message')
    if not message:
        return

    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    # -------------------- Command: /start --------------------
    if text == '/start':
        handle_start(chat_id)
        return

    # -------------------- Button: Phone Lookup --------------------
    if text == '📱 Phone Lookup':
        handle_phone_lookup(chat_id)
        return

    # -------------------- Phone Number Input (10 digits) --------------------
    if text.isdigit() and len(text) == 10:
        handle_phone_number(chat_id, text)
        return

    # -------------------- Invalid input --------------------
    error_msg = (
        "⚠️ *Invalid input!*\n\n"
        "Please use the button below to look up a phone number."
    )
    send_message(chat_id, error_msg, reply_markup=get_main_keyboard(), parse_mode='Markdown')

# =========================== MAIN POLLING LOOP ===========================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is not set. Please fill in your bot token.")
        return
    if not EXTERNAL_API_URL:
        print("⚠️ EXTERNAL_API_URL is not set. The bot will still run, but API calls will fail.")

    print("🚀 Bot started. Polling for updates...")
    last_update_id = 0

    while True:
        try:
            # Fetch updates with offset = last_update_id + 1
            updates = get_updates(offset=last_update_id + 1)

            if not updates.get('ok'):
                print(f"[WARN] getUpdates not ok: {updates}")
                time.sleep(2)
                continue

            for update in updates.get('result', []):
                # Update offset to this update ID
                if update['update_id'] > last_update_id:
                    last_update_id = update['update_id']

                # Process the update
                process_update(update)

            # Small pause to avoid CPU spin
            time.sleep(1)

        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user.")
            break
        except Exception as e:
            print(f"[ERROR] Main loop exception: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()

import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse

TOKEN = "8771883804:AAHv_F_z5LS15vDX6V2MVBXZRZEFADXyoZE"
ADMIN_ID = 8393302659
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
CHANNEL_FILE = "channel_info.txt"

def api_call(method, data=None):
    url = BASE_URL + method
    req_data = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=req_data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(e)
        return None

def send_voice_tts(chat_id, text):
    try:
        q = urllib.parse.quote(text)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=fa&client=tw-ob"
        req = urllib.request.Request(tts_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            audio_data = resp.read()
        
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="voice"; filename="mamzi.ogg"\r\n'
            f"Content-Type: audio/ogg\r\n\r\n"
        ).encode("utf-8") + audio_data + f"\r\n--{boundary}--\r\n".encode("utf-8")
        
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        req2 = urllib.request.Request(BASE_URL + "sendVoice", data=body, headers=headers)
        urllib.request.urlopen(req2, timeout=25)
    except Exception as e:
        api_call("sendMessage", {"chat_id": chat_id, "text": f"🗣 {text}"})

def smart_reply(text, first_name):
    t = text.strip()
    if any(w in t for w in ["عاشق کیه", "عاشق چه کسی", "دوسش کیه", "دوست دختر"]):
        return "ممزی عاشق دینا است! ❤️"
    elif any(w in t for w in ["زن ممزی", "همسر ممزی", "خانوم ممزی", "زن mamzi", "همسر mamzi"]):
        return "زن mamzi (ممزی)، دینا است! 💍❤️"
    elif any(w in t for w in ["سلام", "درود", "هلو", "سلامم"]):
        return f"سلام {first_name} عزیز! 🌹 خوش اومدی، چطور می‌تونم کمکت کنم؟"
    elif any(w in t for w in ["خوبی", "چطوری", "چه خبر", "احوالت"]):
        return "مرسی قربانت، منم عالی‌ام! آماده انجام دستورات آقا mamzi 😎"
    elif any(w in t for w in ["اسمت چیه", "کی هستی", "تو کی هستی", "معرفی"]):
        return "من ربات هوشمند و دستیار اختصاصی mamzi هستم! 🤖👑"
    elif any(w in t for w in ["سازنده", "کی ساختت", "مدیرت کیه", "mamzi", "ممزی"]):
        return "رئیس و سازنده من mamzi هستن 👑"
    elif any(w in t for w in ["مرسی", "ممنون", "دمت گرم", "عشقی", "تشکر"]):
        return "خواهش می‌کنم، کاری نکردم! ❤️"
    elif any(w in t for w in ["خداحافظ", "فعلا", "بای"]):
        return "خدانگهدار! باز هم به ما سر بزن 👋🌹"
    return None

def save_channel(chat_id, username=None):
    with open(CHANNEL_FILE, "w", encoding="utf-8") as f:
        f.write(f"{chat_id}\n{username or ''}")

def load_channel():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if lines:
                chat_id = int(lines[0]) if lines[0].lstrip('-').isdigit() else lines[0]
                username = lines[1] if len(lines) > 1 and lines[1] else None
                return chat_id, username
    return None, None

def get_signature(channel_username=None):
    if channel_username:
        return f"\n\n━━━━━━━━━━━━━━\n✍️ mamzi\n🆔 @{channel_username}"
    return "\n\n━━━━━━━━━━━━━━\n✍️ mamzi"

def get_buttons(channel_username=None, bot_username=""):
    row = [{"text": "💬 ارتباط با mamzi", "url": f"https://t.me/{bot_username}"}]
    if channel_username:
        row.append({"text": "📢 عضویت در کانال", "url": f"https://t.me/{channel_username}"})
    return {"inline_keyboard": [row]}

def handle_channel_post(post, bot_username):
    chat = post.get("chat", {})
    chat_id = chat.get("id")
    username = chat.get("username")
    msg_id = post.get("message_id")
    save_channel(chat_id, username)
    sig = get_signature(username)
    buttons = get_buttons(username, bot_username)

    if "text" in post:
        text = post["text"]
        if "mamzi" not in text:
            api_call("editMessageText", {
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": text + sig,
                "reply_markup": buttons
            })
    elif any(k in post for k in ("photo", "video", "document", "audio", "voice")):
        caption = post.get("caption", "")
        if "mamzi" not in caption:
            api_call("editMessageCaption", {
                "chat_id": chat_id,
                "message_id": msg_id,
                "caption": caption + sig,
                "reply_markup": buttons
            })

def handle_private_message(msg, bot_username):
    chat_id = msg["chat"]["id"]
    user = msg.get("from", {})
    user_id = user.get("id")
    first_name = user.get("first_name", "دوست")
    text = msg.get("text", "")

    if text == "/start":
        if user_id == ADMIN_ID:
            reply_kb = {
                "keyboard": [
                    [{"text": "🗣 تست صدای بات"}, {"text": "📊 وضعیت و آمار کانال"}],
                    [{"text": "📝 راهنمای پنل mamzi"}]
                ],
                "resize_keyboard": True
            }
            api_call("sendMessage", {
                "chat_id": chat_id,
                "text": "سلام mamzi عزیز! 👑\nمن روشنم و آماده صحبت و مدیریت کانالم.",
                "reply_markup": reply_kb
            })
        else:
            api_call("sendMessage", {
                "chat_id": chat_id,
                "text": f"سلام {first_name} عزیز! 🌹\nمن ربات هوشمند mamzi هستم. باهام حرف بزن یا پیامت رو بذار تا به دست mamzi برسونم:"
            })
        return

    if text.startswith("/say "):
        phrase = text.replace("/say ", "", 1).strip()
        if phrase:
            send_voice_tts(chat_id, phrase)
        return

    chat_answer = smart_reply(text, first_name)
    if chat_answer:
        api_call("sendMessage", {"chat_id": chat_id, "text": chat_answer})
        return

    if user_id == ADMIN_ID:
        channel_id, channel_username = load_channel()

        if text == "🗣 تست صدای بات":
            send_voice_tts(chat_id, "سلام مَمزی عزیز، من ربات اختصاصی تو هستم و الان می‌تونم صحبت کنم.")
            return

        if text == "📊 وضعیت و آمار کانال":
            if not channel_id:
                api_call("sendMessage", {"chat_id": chat_id, "text": "⚠️ هنوز کانالی وصل نشده است."})
            else:
                res = api_call("getChatMemberCount", {"chat_id": channel_id})
                if res and res.get("ok"):
                    count = res["result"]
                    api_call("sendMessage", {"chat_id": chat_id, "text": f"👥 تعداد اعضای کانال: {count} نفر"})
                else:
                    api_call("sendMessage", {"chat_id": chat_id, "text": "❌ خطا در دریافت آمار کانال."})
            return

        if text == "📝 راهنمای پنل mamzi":
            api_call("sendMessage", {
                "chat_id": chat_id,
                "text": "۱. با بات چت کن (سلام، زن ممزی کیه؟ عاشق کیه و...) تا جوابت رو بده.\n۲. برای اینکه بات ویس بفرسته بنویس: /say متن\n۳. هر پستی بفرستی با امضای mamzi منتشر میشه."
            })
            return

        if "reply_to_message" in msg and "forward_from" in msg["reply_to_message"]:
            target_id = msg["reply_to_message"]["forward_from"]["id"]
            api_call("sendMessage", {"chat_id": target_id, "text": f"📩 پاسخ از طرف mamzi:\n\n{text}"})
            api_call("sendMessage", {"chat_id": chat_id, "text": "✅ پاسخ ارسال شد."})
            return

        target_chat = channel_id if channel_id else chat_id
        sig = get_signature(channel_username)
        buttons = get_buttons(channel_username, bot_username)
        caption = msg.get("caption", "") + sig
        res = None

        if "text" in msg:
            res = api_call("sendMessage", {"chat_id": target_chat, "text": text + sig, "reply_markup": buttons})
        elif "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]
            res = api_call("sendPhoto", {"chat_id": target_chat, "photo": file_id, "caption": caption, "reply_markup": buttons})
        elif "video" in msg:
            file_id = msg["video"]["file_id"]
            res = api_call("sendVideo", {"chat_id": target_chat, "video": file_id, "caption": caption, "reply_markup": buttons})
        elif "document" in msg:
            file_id = msg["document"]["file_id"]
            res = api_call("sendDocument", {"chat_id": target_chat, "document": file_id, "caption": caption, "reply_markup": buttons})
        elif "audio" in msg:
            file_id = msg["audio"]["file_id"]
            res = api_call("sendAudio", {"chat_id": target_chat, "audio": file_id, "caption": caption, "reply_markup": buttons})
        elif "voice" in msg:
            file_id = msg["voice"]["file_id"]
            res = api_call("sendVoice", {"chat_id": target_chat, "voice": file_id, "caption": caption, "reply_markup": buttons})

        if channel_id and res and res.get("ok"):
            api_call("sendMessage", {"chat_id": chat_id, "text": "✅ در کانال منتشر شد."})

    else:
        api_call("forwardMessage", {
            "chat_id": ADMIN_ID,
            "from_chat_id": chat_id,
            "message_id": msg["message_id"]
        })
        api_call("sendMessage", {
            "chat_id": chat_id,
            "text": f"پیامت رو مستقیم برای mamzi فرستادم {first_name} عزیز! ✅"
        })

def main():
    me = api_call("getMe")
    if not me or not me.get("ok"):
        print("Error: Turn on your VPN.")
        return
    bot_username = me["result"]["username"]
    print("Bot is running and ready to talk...")
    offset = 0
    while True:
        updates = api_call("getUpdates", {"offset": offset, "timeout": 15})
        if updates and updates.get("ok"):
            for item in updates["result"]:
                offset = item["update_id"] + 1
                if "channel_post" in item:
                    handle_channel_post(item["channel_post"], bot_username)
                elif "message" in item and item["message"].get("chat", {}).get("type") == "private":
                    handle_private_message(item["message"], bot_username)
        else:
            time.sleep(1)

if __name__ == "__main__":
    main()

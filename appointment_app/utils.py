def format_whatsapp_phone(phone):
    digits = ''.join(filter(str.isdigit, str(phone)))
    if not digits:
        return ''
    if len(digits) == 10:
        return f"+91{digits}"
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    return f"+{digits}"


def send_whatsapp_message(phone, message, wait_time=15):
    try:
        import time
        import webbrowser
        from urllib.parse import quote

        import pyautogui

        phone = format_whatsapp_phone(phone)
        if not phone:
            print("Failed to send WhatsApp message: missing customer phone number.")
            return False

        wait_time = max(wait_time, 12)
        print(f"Sending WhatsApp message to {phone}...")
        webbrowser.open(f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}")
        time.sleep(wait_time)
        width, height = pyautogui.size()
        pyautogui.click(width / 2, height - 90)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(3)
        pyautogui.hotkey("ctrl", "w")
        print("WhatsApp send command completed.")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False

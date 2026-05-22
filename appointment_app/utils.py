def send_whatsapp_message(phone, message):
    try:
        import pywhatkit

        print(f"Sending WhatsApp message to {phone}...")
        pywhatkit.sendwhatmsg_instantly(
            phone,
            message,
            wait_time=20,  # Increased from 15 to allow WhatsApp Web to fully load
            tab_close=True,
            close_time=10  # Increased from 5 to allow message to actually send before closing
        )
        print("WhatsApp message sent successfully.")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

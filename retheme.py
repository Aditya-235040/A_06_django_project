import os

def replace_theme(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace colors
    content = content.replace('indigo-', 'emerald-')
    content = content.replace('violet-', 'teal-')
    content = content.replace('brand-indigo', 'brand-emerald')
    content = content.replace('brand-violet', 'brand-teal')
    
    # Replace background image to WhatsApp pattern
    content = content.replace(
        'https://images.unsplash.com/photo-1550439062-609e1531270e?q=80&w=2670&auto=format&fit=crop',
        'https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'
    )
    content = content.replace(
        'https://images.unsplash.com/photo-1557682250-33bd709cbe85?q=80&w=2629&auto=format&fit=crop',
        'https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

base_dir = r"c:\Users\adity\Downloads\A06_mid_project\whatsapp_appointment_os\appointment_app\templates"

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.html'):
            replace_theme(os.path.join(root, file))

print("Theme updated successfully.")

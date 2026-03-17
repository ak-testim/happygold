import requests
import base64
import os
import time
import json

API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OUTPUT_DIR = "/Users/andrejkrasnolobodskij/Downloads/happygold/cards"
os.makedirs(OUTPUT_DIR, exist_ok=True)

cards = [
    {
        "filename": "birthday_v1_premium",
        "prompt": "Product photo of a premium gift card with an embedded small 1-gram gold bar (999 fine gold). STYLE: luxury minimalist. Black matte background on the card, gold foil accents, clean typography. Elegant golden calligraphic text 'С Днём Рождения!' on the card surface. The small rectangular gold bar is embedded in the card. Very clean, no clutter — just black, gold, and white. Small 'Happy Gold' logo in the corner. The card is photographed on a dark surface with soft studio lighting. Premium, expensive feel."
    },
    {
        "filename": "birthday_v2_classic",
        "prompt": "Product photo of a premium gift card with an embedded small 1-gram gold bar (999 fine gold). STYLE: classic celebration. Warm golden background with golden and white balloons, confetti, festive ribbons. Elegant calligraphic text 'С Днём Рождения!' in dark ink. The small rectangular gold bar is embedded in the center of the card. Cheerful but elegant, similar to high-end greeting cards. Small 'Happy Gold' logo in the corner. The card is photographed on a dark surface with soft studio lighting."
    },
    {
        "filename": "birthday_v3_bright",
        "prompt": "Product photo of a premium gift card with an embedded small 1-gram gold bar (999 fine gold). STYLE: bold and vibrant modern design. Rich gradient background mixing deep purple, magenta and gold. Geometric shapes, modern typography, dynamic composition. Bold text 'С Днём Рождения!' in white with gold outline. The small rectangular gold bar is embedded in the card. Eye-catching, contemporary, Instagram-worthy aesthetic. Small 'Happy Gold' logo in the corner. The card is photographed on a dark surface with soft studio lighting."
    },
]

def generate_image(card, index):
    print(f"\n[{index+1}/12] Генерирую: {card['filename']}...")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-5-image",
            "messages": [
                {
                    "role": "user",
                    "content": card["prompt"]
                }
            ],
        },
        timeout=120,
    )

    if response.status_code != 200:
        print(f"  ОШИБКА {response.status_code}: {response.text[:300]}")
        return False

    data = response.json()

    # Extract image from response
    choices = data.get("choices", [])
    if not choices:
        print(f"  ОШИБКА: Нет результата. Ответ: {json.dumps(data, ensure_ascii=False)[:300]}")
        return False

    message = choices[0].get("message", {})
    content = message.get("content", "")

    # Check if content is a list (multimodal response)
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                image_data = part["image_url"]["url"]
                if image_data.startswith("data:"):
                    # base64 encoded
                    header, b64data = image_data.split(",", 1)
                    img_bytes = base64.b64decode(b64data)
                    filepath = os.path.join(OUTPUT_DIR, f"{card['filename']}.png")
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                    print(f"  Сохранено: {filepath}")
                    return True

    # Maybe the content itself is base64 or URL
    if isinstance(content, str):
        if content.startswith("data:"):
            header, b64data = content.split(",", 1)
            img_bytes = base64.b64decode(b64data)
            filepath = os.path.join(OUTPUT_DIR, f"{card['filename']}.png")
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            print(f"  Сохранено: {filepath}")
            return True

    # Debug: show what we got
    print(f"  Неожиданный формат ответа. Сохраняю в JSON для анализа...")
    debug_path = os.path.join(OUTPUT_DIR, f"{card['filename']}_debug.json")
    with open(debug_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Debug: {debug_path}")
    return False


# Generate all 12 cards
success = 0
for i, card in enumerate(cards):
    if generate_image(card, i):
        success += 1
    time.sleep(2)  # small delay between requests

print(f"\n{'='*40}")
print(f"Готово! Успешно сгенерировано: {success}/{len(cards)}")
print(f"Папка с результатами: {OUTPUT_DIR}")

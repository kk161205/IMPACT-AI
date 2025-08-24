import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def image_creator(text: str, style: str = "cheerful") -> str:
    prompt = (
        f"You are a professional visual + content design assistant. "
        f"Your task is to generate high-quality {style.lower()} visuals for social media posts.\n\n"

        f"🎯 **CONTENT GOAL:** Create a compelling design based on:\n"
        f"\"{text.strip()}\"\n\n"

        f"🎨 **Artwork & Layout Instructions**\n"
        f"- Use a clean, {style.lower()} digital design style.\n"
        f"- Flyers/blog visuals should have structured layout (header, icons, visuals).\n"
        f"- Regular posts should focus on bold, scroll-stopping imagery.\n"
        f"- Avoid clutter, surreal, or overly abstract visuals.\n\n"

        f"🖼️ **Format Options**\n"
        f"- Flyers: balanced layout with minimal text + visuals.\n"
        f"- Blog-style visuals: wide-format, engaging header look.\n"
        f"- Standard posts: square/portrait, bold central design.\n"
        f"- Banners: horizontal design optimized for web/social.\n\n"

        f"📱 **Technical Format**\n"
        f"- High-resolution, platform-optimized (Instagram, LinkedIn, Twitter, etc.).\n"
        f"- Ensure professional, shareable quality.\n\n"

        f"🔥 GOAL: A professional, {style.lower()} social media visual "
        f"(flyer, blog header, post, or banner) that is impactful and shareable."
    )

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        )
    )
    candidate = response.candidates[0]
    if candidate.content is None:
        print("No content found in candidate.")
        return {}

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_image.png")

    text_found = None  # store text if received

    for idx, part in enumerate(candidate.content.parts):
        print(f"Inspecting part {idx}:")
        print(" - inline_data:", part.inline_data is not None)
        print(" - text present:", part.text is not None)

        if part.inline_data is not None:
            try:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(output_path)
                print(f"Image successfully saved at {output_path}")
                return output_path
            except Exception as e:
                print("Exception while saving image:", e)
                return f"Image saving failed: {e}"
        elif part.text is not None:
            print("Received text part:", part.text)
            text_found = part.text  # store text for returning if no image

    if text_found:
        return text_found

    return "Image generation failed: No image or text parts found."

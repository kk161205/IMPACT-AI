from google.adk import Agent
from tools import image_creator, image_checker
from google import genai
import re
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

class ImageGenerationAgent(Agent):
    async def _run_async_impl(self, ctx):
        print("🎨 Inside ImageGenerationAgent")
        last_chunk = None

        # Step 1: Run image creation and validation
        async for chunk in super()._run_async_impl(ctx):
            last_chunk = chunk
            yield chunk

        image_path = None
        max_retries = 3
        retries = 0

        while last_chunk is not None and retries < max_retries:
            content_obj = getattr(last_chunk, "content", None)
            if content_obj and hasattr(content_obj, "parts"):
                for part in content_obj.parts:
                    text = getattr(part, "text", "").strip()
                    if not text:
                        continue

                    matches = re.findall(
                        r"(https?://\S+?\.(?:png|jpg))|([\w./\\-]+\.(?:png|jpg))",
                        text,
                        re.IGNORECASE,
                    )

                    if matches:
                        for url_match, path_match in matches:
                            candidate = url_match or path_match
                            if candidate:
                                image_path = candidate
                                ctx.session.state["final_image"] = image_path
                                print("✅ Saved final_image:", image_path)
                                break
                    if image_path:
                        break

            if image_path:
                break
            else:
                print(f"⚠️ Image not valid, retrying {retries + 1}/{max_retries}")
                retries += 1
                # Optionally call image_creator again for retry here
                # last_chunk = await self.generate_image_again(ctx)

image_generation_agent = ImageGenerationAgent(
    name="image_generation_agent",
    model="gemini-2.5-flash",
    description=(
        "An agent that generates visuals for social media posts. "
        "It returns the path to the saved image file."
    ),
    instruction=(
        "1. Read the social media post configuration from {problem_config}.\n"
        "2. Extract the core text/content to be visually represented.\n"
        "3. Use `image_creator` to generate an image.\n"
        "4. Validate the image using `image_checker`.\n"
        "5. Return the local filepath to the saved image.\n"
        "6. Retry generation if validation fails, up to 3 times.\n"
        '7. return an object {\"generated_image\": True} only.\n'
        "DO NOT write anything else, not even ```JSON```"
    ),
    tools=[image_creator, image_checker]
)

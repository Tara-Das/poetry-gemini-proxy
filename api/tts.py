import base64
import google.generativeai as genai
from fastapi import FastAPI, Request

app = FastAPI()

genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Will be set in Vercel environment variables

@app.post("/api/tts")
async def generate_tts(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {"error": "Text is required"}

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": f"Read aloud in a warm, welcoming tone\nSpeaker 1: {text}"}
                ]
            }
        ]
        generation_config = {
            "temperature": 1,
            "response_mime_type": "audio/wav"
        }

        response = model.generate_content(
            contents,
            generation_config=generation_config
        )
        if not response.parts or not hasattr(response.parts[0], 'inline_data'):
            return {"error": "Failed to generate audio"}

        audio_data = response.parts[0].inline_data.data
        audio_base64 = audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return {"audioBase64": audio_base64}
    except Exception as e:
        return {"error": f"Failed to generate speech: {str(e)}"}

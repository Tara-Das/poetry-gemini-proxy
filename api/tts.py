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
        model = "gemini-2.5-flash-preview-tts"
        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": text}
                ]
            }
        ]
        generate_content_config = {
            "temperature": 1,
            "response_modalities": ["audio"],
            "speech_config": {
                "multi_speaker_voice_config": {
                    "speaker_voice_configs": [
                        {
                            "speaker": "Speaker 1",
                            "voice_config": {
                                "prebuilt_voice_config": {"voice_name": "Zephyr"}
                            }
                        }
                    ]
                }
            }
        }

        audio_data = b""
        response = genai.GenerativeModel(model).generate_content_stream(
            contents=contents,
            generation_config=generate_content_config
        )
        for chunk in response:
            if (
                chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
                and chunk.candidates[0].content.parts[0].inline_data
            ):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                audio_data += inline_data.data

        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return {"audioBase64": audio_base64}
    except Exception as e:
        return {"error": f"Failed to generate speech: {str(e)}"}

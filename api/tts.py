import base64
from google import genai
from google.genai import types
from fastapi import FastAPI, Request

app = FastAPI()

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")  # Will be set in Vercel environment variables

@app.post("/api/tts")
async def generate_tts(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {"error": "Text is required"}

    model = "gemini-2.5-flash-preview-tts"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Zephyr"
                            )
                        ),
                    ),
                ]
            ),
        ),
    )

    audio_data = b""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            audio_data += inline_data.data

    # Convert to base64 for browser playback
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    return {"audioBase64": audio_base64}

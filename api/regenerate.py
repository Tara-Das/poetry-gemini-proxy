from google import genai
from fastapi import FastAPI, Request

app = FastAPI()

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")  # Will be set in Vercel environment variables

@app.post("/api/regenerate")
async def regenerate_poem(request: Request):
    data = await request.json()
    poem_text = data.get("poemText", "")
    style = data.get("style", "")
    if not poem_text or not style:
        return {"error": "Poem text and style are required"}

    model = "gemini-1.5-flash"
    prompt = f"Rewrite this poem in {style}:\n{poem_text}"
    contents = [
        {
            "role": "user",
            "parts": [{"text": prompt}]
        }
    ]
    response = await client.models.generate_content_async(model=model, contents=contents)
    if not response.candidates or not response.candidates[0].content:
        return {"error": "Failed to generate response"}

    remixed_poem = response.candidates[0].content.parts[0].text
    return {"remixedPoem": remixed_poem}

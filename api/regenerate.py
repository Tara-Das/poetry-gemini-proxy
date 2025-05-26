import google.generativeai as genai
from fastapi import FastAPI, Request

app = FastAPI()

genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Will be set in Vercel environment variables

@app.post("/api/regenerate")
async def regenerate_poem(request: Request):
    data = await request.json()
    poem_text = data.get("poemText", "")
    style = data.get("style", "")
    if not poem_text or not style:
        return {"error": "Poem text and style are required"}

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Rewrite this poem in {style}:\n{poem_text}"
        response = model.generate_content(prompt)
        if not response.text:
            return {"error": "Failed to generate response"}

        remixed_poem = response.text
        return {"remixedPoem": remixed_poem}
    except Exception as e:
        return {"error": f"Failed to regenerate poem: {str(e)}"}

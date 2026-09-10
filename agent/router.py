import requests
import json

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
BACKEND_URL = "http://127.0.0.1:5000/api"

def query_agent(prompt: str) -> str:
    """Interprets natural language questions using local Qwen model and calls backend tools."""
    
    system_prompt = """
    You are a Dofus Rétro assistant. Answer briefly using database context when needed.
    If the user asks for ingredients/crafting requirements, identify the target item name.
    """

    # 1. First pass - extract target entity via local LLM or simple fuzzy check
    res = requests.post(OLLAMA_URL, json={
        "model": "qwen2.5:latest",
        "prompt": f"{system_prompt}\nUser query: {prompt}\nExtract only the item name mentioned if any, otherwise return 'NONE'.",
        "stream": False
    })
    
    extracted_item = res.json().get("response", "").strip().replace('"', '')

    if extracted_item and extracted_item != "NONE":
        # Search item in Flask API
        search_res = requests.get(f"{BACKEND_URL}/search", params={"q": extracted_item}).json()
        if search_res:
            target_id = search_res[0]["id"]
            breakdown = requests.get(f"{BACKEND_URL}/recipes/breakdown/{target_id}").json()
            
            # Format clean answer
            materials = breakdown.get("raw_materials", [])
            mat_text = ", ".join([f"{m['quantity']}x {m['name']}" for m in materials])
            return f"To craft {breakdown['item']['name']}, you need: {mat_text}."

    return "Could not determine the recipe or item from local data."

if __name__ == "__main__":
    print(query_agent("What do I need to craft a Gelano?"))

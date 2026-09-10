import re

def route_query(user_input: str):
    """
    V1 Router: Parses natural language into API calls.
    Future: Replace with local Qwen function-calling agent.
    """
    user_input = user_input.lower()
    
    # Pattern: "What do I need to craft X?" or "Recipe for X"
    craft_match = re.search(r'(craft|make|create|recipe for)\s+(?:a\s+)?(.+?)(?:\?|$)', user_input)
    if craft_match:
        item_name = craft_match.group(2).strip().title()
        return {
            "action": "get_recipe_tree",
            "params": {"item_name": item_name}
        }
        
    # Pattern: "Where do I find X?"
    drop_match = re.search(r'(find|drop|farm|get)\s+(?:a\s+)?(.+?)(?:\?|$)', user_input)
    if drop_match:
        item_name = drop_match.group(2).strip().title()
        return {
            "action": "get_drops",
            "params": {"item_name": item_name}
        }

    return {"action": "search", "params": {"query": user_input}}
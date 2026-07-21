import json
import sys

def compile_prompt(catalog_path):
    try:
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"Error reading catalog: {e}")
        return None
        
    prompt = "Here is the available A2UI catalog:\n\n"
    
    # Check if catalog is schema-like or simple dict
    components = catalog.get("components", {})
    if not components and "definitions" in catalog:
        components = catalog["definitions"]
        
    for comp_name, comp_details in components.items():
        desc = comp_details.get("description", "No description")
        prompt += f"- **{comp_name}**: {desc}\n"
        props = comp_details.get("properties", {})
        if props:
            prompt += "  Properties:\n"
            for p_name, p_details in props.items():
                p_type = p_details.get("type", "unknown") if isinstance(p_details, dict) else str(p_details)
                prompt += f"    * {p_name} ({p_type})\n"
    
    return prompt

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compile_catalog_prompt.py <path_to_catalog_json>")
        sys.exit(1)
        
    prompt = compile_prompt(sys.argv[1])
    if prompt:
        print(prompt)
        sys.exit(0)
    else:
        sys.exit(1)

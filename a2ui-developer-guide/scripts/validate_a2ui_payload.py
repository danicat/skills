import json
import sys

def validate(payload_path):
    try:
        with open(payload_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    if not isinstance(data, list):
        print("Payload should be a list of A2UI messages.")
        return False
        
    for msg in data:
        if "updateComponents" not in msg and "dataModelUpdate" not in msg and "userAction" not in msg:
            print("Message missing valid A2UI key (updateComponents, dataModelUpdate, userAction).")
            return False
            
    print("Payload looks like a valid A2UI message sequence.")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_a2ui_payload.py <path_to_json>")
        sys.exit(1)
    if validate(sys.argv[1]):
        sys.exit(0)
    else:
        sys.exit(1)

import json
import os
import glob

def convert_cards():
    input_dir = r"o:\ANTIGRAVITY WORKSPACES\one-piece-tcg-data\cards\en"
    output_file = r"o:\ANTIGRAVITY WORKSPACES\tcgarena\CardList.json"

    all_cards = {}

    # Iterate through all json files in the input directory
    for filepath in glob.glob(os.path.join(input_dir, "*.json")):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                cards_data = json.load(f)
                
                for card in cards_data:
                    # we only process if there is a card ID
                    if "id" not in card or "code" not in card:
                        continue
                        
                    card_id = card["id"]
                    
                    # Sometimes there are multiple variations (aa, sp) with _p1, _p2, etc. in the ID
                    # We will use the base code for the ID if we are grouping them, or just keep them unique.
                    # TCG Arena expects the ID to match exactly what is in the decklist/Game file, 
                    # usually the base set code like ST29-001.
                    # For simplicity, if we see _p, maybe we skip alternative arts to avoid duplicates for now,
                    # or just overwrite the base. Let's just keep the base ones for the main CardList.
                    if "_p" in card_id:
                        continue
                        
                    # Extract the colors (some cards might have multiple colors separated by '/')
                    colors = []
                    if "color" in card and card["color"]:
                        colors = card["color"].split('/')
                        
                    # Extract the subtype (family)
                    subtypes = []
                    if "family" in card and card["family"]:
                        subtypes = card["family"].split('/')
                        
                    # Extract the attributes
                    attributes = []
                    if "attribute" in card and "name" in card["attribute"] and card["attribute"]["name"]:
                        attributes = [card["attribute"]["name"]]
                        
                    # Some cards like Events don't have cost/power but the schema says cost/power should be there
                    cost = card.get("cost", 0) if card.get("cost") is not None else 0
                    power = card.get("power", 0) if card.get("power") is not None else 0
                    
                    card_type = card.get("type", "Character").capitalize()
                    
                    name_with_id = f"{card.get('name', 'Unknown')} {card_id}"
                    
                    # Construct the object
                    tcg_card = {
                        "id": card_id,
                        "face": {
                            "front": {
                                "name": name_with_id,
                                "type": card_type,
                                "cost": cost,
                                "image": card.get("images", {}).get("large", "")
                            }
                        },
                        "name": name_with_id,
                        "type": card_type,
                        "cost": cost,
                        "power": power,
                        "colors": colors,
                        "subtype": subtypes,
                        "attributes": attributes
                    }
                    
                    all_cards[card_id] = tcg_card
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(all_cards, out_f, indent=2, ensure_ascii=False)
        
    print(f"Successfully converted {len(all_cards)} cards to {output_file}")

if __name__ == "__main__":
    convert_cards()

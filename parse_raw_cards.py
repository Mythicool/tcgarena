import re
import json

def parse_limitless_text(filepath):
    """Parses a text file with data pasted from Limitless TCG into a dictionary of TCG Arena cards."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    cards = {}
    id_pattern = r"(OP\d+-\d+|EB\d+-\d+|PRB\d+-\d+|ST\d+-\d+|P-\d+)"
    matches = list(re.finditer(id_pattern, content))
    
    for i in range(len(matches)):
        start_idx = matches[i].start()
        name_start = start_idx
        while name_start > 0:
            if content[name_start-2:name_start] == '\n\n':
                break
            name_start -= 1
            
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        if i > 0:
            prev_end_idx = matches[i-1].end()
            if name_start < prev_end_idx:
                name_start = prev_end_idx + 1
        
        block = content[name_start:end_idx].strip()
        
        if not block:
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if len(lines) < 3:
            continue
            
        card_id = lines[1]
        if not re.match(id_pattern, card_id):
            continue
            
        # Avoid duplicate alternative arts (they have the same ID usually in these lists, but let's just use the first match)
        if card_id in cards:
            continue
            
        # Extract basic info
        name = lines[0]
        type_line = lines[2]
        type_parts = type_line.split('•')
        
        card_type = "Character"
        if len(type_parts) >= 1:
            card_type = type_parts[0].strip()
            
        colors = []
        if len(type_parts) >= 2:
            colors = type_parts[1].strip().split('/')
            
        cost = 0
        if len(type_parts) >= 3:
            cost_str = type_parts[2].strip()
            if "Cost" in cost_str:
                try:
                    cost = int(cost_str.replace(" Cost", ""))
                except ValueError:
                    cost = 0
        
        power = 0
        attributes = []
        
        if len(lines) > 3:
            power_line = lines[3]
            if "Power" in power_line:
                power_parts = power_line.split('•')
                if len(power_parts) >= 1:
                    power_str = power_parts[0].strip().replace(" Power", "")
                    try:
                        power = int(power_str)
                    except ValueError:
                        pass
                if len(power_parts) >= 2:
                    attributes = power_parts[1].strip().split('/')

        subtypes = []
        illus_idx = -1
        for j, line in enumerate(lines):
            if line.startswith("Illustrated by"):
                illus_idx = j
                break
                
        if illus_idx > 0:
            family_line = lines[illus_idx - 1]
            if family_line and not family_line.startswith("[") and not "Power" in family_line:
                 subtypes = family_line.split('/')
                 
        # Build image URL. Format example: https://en.onepiece-cardgame.com/images/cardlist/card/OP13-001.png
        # Adding a cache bust parameter just in case
        image_url = f"https://en.onepiece-cardgame.com/images/cardlist/card/{card_id}.png?240419"
        
        # Build TCG Arena format
        tcg_card = {
            "id": card_id,
            "face": {
                "front": {
                    "name": name,
                    "type": card_type,
                    "cost": cost,
                    "image": image_url
                }
            },
            "name": name,
            "type": card_type,
            "cost": cost,
            "power": power,
            "colors": colors,
            "subtype": subtypes,
            "attributes": attributes
        }
        
        cards[card_id] = tcg_card
        
    return cards

def main():
    existing_file = r"o:\ANTIGRAVITY WORKSPACES\tcgarena\CardList.json"
    
    # Load existing cards
    with open(existing_file, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
        
    start_len = len(all_cards)
    
    # Parse OP13
    op13_cards = parse_limitless_text(r"o:\ANTIGRAVITY WORKSPACES\tcgarena\OP13")
    print(f"Adding {len(op13_cards)} unique cards from OP13.")
    all_cards.update(op13_cards)
    
    # Parse OP14
    op14_cards = parse_limitless_text(r"o:\ANTIGRAVITY WORKSPACES\tcgarena\OP14")
    print(f"Adding {len(op14_cards)} unique cards from OP14.")
    all_cards.update(op14_cards)
    
    end_len = len(all_cards)
    print(f"Total cards increased from {start_len} to {end_len} (+{end_len - start_len})")
    
    # Save back
    with open(existing_file, 'w', encoding='utf-8') as out_f:
        json.dump(all_cards, out_f, indent=2, ensure_ascii=False)
        
    print("Database updated!")

if __name__ == "__main__":
    main()

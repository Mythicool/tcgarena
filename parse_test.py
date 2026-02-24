import re
import json
import os

def parse_limitless_text(filepath):
    """Parses a text file with data pasted from Limitless TCG into a list of dictionaries."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the text into sections by checking the card ID pattern (like OP13-001)
    # The split point will usually be the card ID itself, but we can look for blocks.
    
    # Let's try to extract blocks by looking at the structure.
    # Typically:
    # Character Name
    # ID
    # 
    # [Type] • [Colors] • [Cost/Life]
    # 
    # [Power] Power • [Strike/Slash/Special/Wisdom/Ranged] (• +[Counter] Counter)?
    
    cards = []
    
    # We can split by card ID pattern
    id_pattern = r"(OP\d+-\d+|EB\d+-\d+|PRB\d+-\d+|ST\d+-\d+|P-\d+)"
    
    # Find all IDs and their positions
    matches = list(re.finditer(id_pattern, content))
    
    for i in range(len(matches)):
        start_idx = matches[i].start()
        # Find the start of the line before the ID (which should be the card name)
        # Scan backward from start_idx until we hit two newlines or the start
        name_start = start_idx
        while name_start > 0:
            if content[name_start-2:name_start] == '\n\n':
                break
            name_start -= 1
            
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        # Ensure we don't grab too much from the previous block
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
            
        card = {}
        
        # Name
        card['name'] = lines[0]
        
        # ID
        card['id'] = lines[1]
        
        # Make sure it's a real ID match
        if not re.match(id_pattern, card['id']):
            continue
            
        # Parse Type, Color, Cost/Life
        type_line = lines[2]
        type_parts = type_line.split('•')
        if len(type_parts) >= 2:
            card['type'] = type_parts[0].strip()
            card['colors'] = type_parts[1].strip().split('/')
            
            if len(type_parts) >= 3:
                cost_part = type_parts[2].strip()
                if "Cost" in cost_part:
                    card['cost'] = int(cost_part.replace(" Cost", ""))
                elif "Life" in cost_part:
                    card['life'] = int(cost_part.replace(" Life", ""))
        
        # Parse Power, Attribute, Counter
        if len(lines) > 3:
            power_line = lines[3]
            if "Power" in power_line:
                power_parts = power_line.split('•')
                if len(power_parts) >= 1:
                    power_str = power_parts[0].strip().replace(" Power", "")
                    try:
                        card['power'] = int(power_str)
                    except ValueError:
                        pass
                
                if len(power_parts) >= 2:
                    card['attributes'] = power_parts[1].strip().split('/')
                    
                if len(power_parts) >= 3:
                    counter_str = power_parts[2].strip().replace("+", "").replace(" Counter", "")
                    try:
                        card['counter'] = int(counter_str)
                    except ValueError:
                        pass

        # Text and Family/Subtypes are usually further down
        # We need to extract the family line and the effect text
        # This is tricky because effect text can be multiple lines.
        # We look for the "Illustrated by" line backwards.
        
        illus_idx = -1
        for j, line in enumerate(lines):
            if line.startswith("Illustrated by"):
                illus_idx = j
                break
                
        if illus_idx > 0:
            # The line before "Illustrated by" is usually the family/subtypes
            family_line = lines[illus_idx - 1]
            if family_line and not family_line.startswith("[") and not "Power" in family_line:
                 card['subtype'] = family_line.split('/')
                 
            # Text is everything between the stats and the family
            # But the line index for stats might vary (Leader vs Character vs Event)
            # Event cards don't have power lines
            stat_end_idx = 2
            if "Power" in power_line:  
                stat_end_idx = 3
                
            text_lines = []
            for j in range(stat_end_idx + 1, illus_idx - 1):
                text_lines.append(lines[j])
                
            card['text'] = '\n'.join(text_lines)

        cards.append(card)
        
    return cards

# Test parser on OP13
if __name__ == '__main__':
    cards = parse_limitless_text(r'o:\ANTIGRAVITY WORKSPACES\tcgarena\OP13')
    print(f"Parsed {len(cards)} cards from OP13.")
    if cards:
        print(json.dumps(cards[0], indent=2))
        print("========")
        print(json.dumps(cards[1], indent=2))

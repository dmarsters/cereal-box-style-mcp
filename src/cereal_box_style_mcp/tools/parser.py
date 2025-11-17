"""Prompt parsing utilities - extract semantic components from natural language."""

import re
from typing import Dict, List, Optional


def parse_prompt_components(prompt: str, transformation_maps: Dict) -> Dict:
    """Parse user prompt into structured components."""
    
    return {
        'subject': extract_subject(prompt, transformation_maps),
        'action': extract_action(prompt),
        'setting': extract_setting(prompt),
        'objects': extract_objects(prompt),
        'colors': extract_colors(prompt),
        'mood': extract_mood(prompt)
    }


def extract_subject(prompt: str, transformation_maps: Dict) -> Dict:
    """Identify primary subject with attributes."""
    
    # Common subject patterns
    subjects = {
        'human': r'\b(person|people|man|woman|child|kid|adult|teenager|boy|girl|chef|doctor|firefighter|teacher|artist|musician|pilot|detective|scientist|astronaut|athlete|dancer|singer|wizard|warrior|knight|pirate|ninja|superhero)\b',
        'animal': r'\b(cat|dog|bird|fish|horse|lion|tiger|bear|elephant|dragon|phoenix|unicorn|griffin|kitten|puppy)\b',
        'object': r'\b(car|boat|plane|bicycle|train|rocket|sword|hammer|book|computer|phone|camera|chair|table)\b',
        'food': r'\b(pizza|burger|sandwich|taco|pasta|apple|banana|strawberry|cake|cookie|donut)\b'
    }
    
    for subject_type, pattern in subjects.items():
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            subject_name = match.group(0)
            
            # Extract attributes (adjectives before the subject)
            attr_pattern = rf'\b(\w+)\s+{subject_name}\b'
            attr_match = re.search(attr_pattern, prompt, re.IGNORECASE)
            attributes = [attr_match.group(1)] if attr_match else []
            
            # Extract profession/role if human
            profession = None
            if subject_type == 'human':
                profession_map = transformation_maps.get('profession_to_icon_props', {})
                if subject_name.lower() in profession_map:
                    profession = subject_name.lower()
            
            # Count (two dogs, three cats, etc.)
            count = 1
            count_pattern = r'\b(two|three|four|five|six|2|3|4|5|6)\s+' + subject_name
            count_match = re.search(count_pattern, prompt, re.IGNORECASE)
            if count_match:
                count_word = count_match.group(1).lower()
                count_map = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
                count = count_map.get(count_word, int(count_word) if count_word.isdigit() else 1)
            
            return {
                'type': subject_type,
                'name': subject_name,
                'attributes': attributes,
                'profession': profession,
                'count': count
            }
    
    return {'type': 'abstract', 'name': None, 'attributes': [], 'profession': None, 'count': 0}


def extract_action(prompt: str) -> Dict:
    """Identify action/verb with energy level."""
    
    # Action patterns
    actions = {
        'high_energy': ['running', 'jumping', 'flying', 'racing', 'sprinting', 'leaping', 'dashing'],
        'medium_energy': ['walking', 'swimming', 'climbing', 'dancing', 'playing', 'working', 'cooking'],
        'low_energy': ['sitting', 'standing', 'lying', 'resting', 'reading', 'thinking', 'meditating']
    }
    
    for energy_level, verbs in actions.items():
        for verb in verbs:
            if verb in prompt.lower():
                # Look for object of action
                obj_pattern = rf'{verb}\s+(a|an|the)?\s*(\w+)'
                obj_match = re.search(obj_pattern, prompt, re.IGNORECASE)
                action_object = obj_match.group(2) if obj_match else None
                
                # Check for intensity modifiers
                intensity_modifiers = ['violently', 'intensely', 'quickly', 'slowly', 'gently', 'carefully']
                modifier = None
                for mod in intensity_modifiers:
                    if mod in prompt.lower():
                        modifier = mod
                        break
                
                return {
                    'verb': verb,
                    'energy_level': energy_level.replace('_energy', ''),
                    'object': action_object,
                    'modifier': modifier,
                    'progressive': 'ing' in prompt.lower()  # "is running" vs "runs"
                }
    
    return {'verb': None, 'energy_level': 'low', 'object': None, 'modifier': None, 'progressive': False}


def extract_setting(prompt: str) -> Dict:
    """Identify setting/environment."""
    
    settings = {
        'indoor_specific': r'\b(kitchen|bedroom|office|classroom|library|lab|studio|garage|bathroom|hallway)\b',
        'indoor_generic': r'\b(inside|indoors|room|building|house)\b',
        'outdoor_natural': r'\b(forest|mountain|beach|desert|jungle|field|river|lake|ocean|park|garden)\b',
        'outdoor_urban': r'\b(street|city|downtown|alley|plaza|rooftop|sidewalk)\b',
        'fantasy': r'\b(castle|dungeon|spaceship|alien planet|magical realm|dimension)\b'
    }
    
    for setting_type, pattern in settings.items():
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            location = match.group(0)
            
            # Extract atmosphere attributes
            attributes = []
            atmosphere_words = ['busy', 'quiet', 'dark', 'bright', 'crowded', 'empty', 'chaotic', 'peaceful']
            for word in atmosphere_words:
                if word in prompt.lower():
                    attributes.append(word)
            
            # Time of day
            time_pattern = r'\b(dawn|sunrise|morning|noon|afternoon|sunset|dusk|evening|night|midnight)\b'
            time_match = re.search(time_pattern, prompt, re.IGNORECASE)
            time = time_match.group(0) if time_match else None
            
            return {
                'type': setting_type,
                'location': location,
                'attributes': attributes,
                'time': time
            }
    
    return {'type': 'abstract', 'location': None, 'attributes': [], 'time': None}


def extract_objects(prompt: str) -> List[str]:
    """Extract secondary objects/props."""
    
    # Common props
    objects = []
    prop_pattern = r'\b(with|holding|carrying|near|beside)\s+(a|an|the)?\s*(\w+)\b'
    matches = re.finditer(prop_pattern, prompt, re.IGNORECASE)
    
    for match in matches:
        objects.append(match.group(3))
    
    return objects


def extract_colors(prompt: str) -> List[str]:
    """Extract color keywords."""
    
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 
              'white', 'brown', 'gray', 'cyan', 'magenta', 'teal', 'gold', 'silver']
    
    found_colors = []
    for color in colors:
        if color in prompt.lower():
            found_colors.append(color)
    
    return found_colors


def extract_mood(prompt: str) -> Dict:
    """Identify emotional tone."""
    
    emotions = {
        'positive': ['happy', 'joyful', 'excited', 'proud', 'confident', 'cheerful', 'delighted'],
        'negative': ['sad', 'angry', 'afraid', 'worried', 'frustrated', 'tired', 'exhausted', 'lonely'],
        'neutral': ['calm', 'peaceful', 'focused', 'curious', 'contemplative']
    }
    
    for valence, emotion_list in emotions.items():
        for emotion in emotion_list:
            if emotion in prompt.lower():
                # Determine intensity
                intensity = 'medium'
                if 'very' in prompt.lower() or 'extremely' in prompt.lower():
                    intensity = 'high'
                elif 'slightly' in prompt.lower() or 'a bit' in prompt.lower():
                    intensity = 'low'
                
                return {
                    'emotion': emotion,
                    'valence': valence,
                    'intensity': intensity
                }
    
    return {'emotion': None, 'valence': 'neutral', 'intensity': 'medium'}

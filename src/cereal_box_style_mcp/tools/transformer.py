"""Component transformation logic - apply category rules to parsed components."""

from typing import Dict, Optional


def apply_category_transformation(
    components: Dict,
    rules: Dict,
    transformation_maps: Dict,
    params: Dict
) -> Dict:
    """Apply category-specific transformations to all components."""
    
    category = rules.get('name', 'unknown')
    
    return {
        'subject': transform_subject(components['subject'], rules, transformation_maps, params),
        'action': transform_action(components['action'], rules, transformation_maps, params),
        'setting': transform_setting(components['setting'], rules, params),
        'colors': transform_colors(components['colors'], rules, params),
        'effects': transform_effects(category, components, params),
        'style_markers': rules.get('mandatory_markers', []),
        'typography': transform_typography(components['subject'], category, params) if category in ['mascot_theater', 'kid_chaos', 'nostalgia_revival'] else None
    }


def transform_subject(subject: Dict, rules: Dict, maps: Dict, params: Dict) -> str:
    """Transform subject based on category rules."""
    
    subject_type = subject.get('type', 'abstract')
    subject_name = subject.get('name', 'character')
    
    if subject_type not in rules.get('subject_rules', {}):
        return f"{subject_name}"
    
    subject_rule = rules['subject_rules'][subject_type]
    treatment = subject_rule.get('treatment', 'standard')
    features = subject_rule.get('features', [])
    attributes = subject_rule.get('attributes', [])
    
    # Start building description
    parts = [treatment.replace('_', ' '), subject_name]
    
    # Add profession-specific props if applicable
    if subject.get('profession'):
        prof_map = maps.get('profession_to_icon_props', {})
        if subject['profession'] in prof_map:
            parts.append(f"with {prof_map[subject['profession']]}")
    
    # Add features
    if features:
        parts.extend(features)
    
    # Add attributes
    if attributes:
        parts.extend(attributes)
    
    # Add original attributes from prompt
    if subject.get('attributes'):
        # Map emotions to visual expressions
        emotion_map = maps.get('emotion_to_mascot_face', {})
        for attr in subject['attributes']:
            if attr in emotion_map:
                parts.append(emotion_map[attr])
            else:
                parts.append(f"{attr} appearance")
    
    return ', '.join(parts)


def transform_action(action: Dict, rules: Dict, maps: Dict, params: Dict) -> str:
    """Transform action based on category rules and energy level."""
    
    verb = action.get('verb')
    if not verb:
        return "in neutral pose"
    
    energy_level = action.get('energy_level', 'medium')
    
    # Get action rules for this energy level
    action_rules = rules.get('action_rules', {})
    if energy_level not in action_rules:
        energy_level = 'low_energy'
    
    action_rule = action_rules[energy_level]
    treatment = action_rule.get('treatment', '')
    features = action_rule.get('features', [])
    effects = action_rule.get('effects', [])
    
    # Apply energy multiplier from params
    energy_multiplier = params.get('energy_level', 1.0)
    if energy_multiplier > 1.0 and effects:
        effects = [e + " intensified" for e in effects]
    
    parts = [f"{verb} with {treatment}"]
    parts.extend(features)
    
    # Add action object if present
    if action.get('object'):
        obj = action['object']
        category = rules.get('name', '')
        if 'mascot' in category or 'kid_chaos' in category:
            parts.append(f"with comically oversized {obj}")
        else:
            parts.append(f"with {obj}")
    
    # Add effects
    if effects:
        parts.append(', '.join(effects))
    
    return ', '.join(parts)


def transform_setting(setting: Dict, rules: Dict, params: Dict) -> str:
    """Transform setting based on category rules."""
    
    setting_type = setting.get('type', 'abstract')
    location = setting.get('location', 'background')
    
    setting_rules = rules.get('setting_rules', {})
    
    # Map setting type to rule
    rule_key = setting_type
    if rule_key not in setting_rules:
        # Try generic fallback
        if 'indoor' in setting_type:
            rule_key = 'indoor'
        elif 'outdoor' in setting_type:
            rule_key = 'outdoor'
        else:
            rule_key = 'abstract'
    
    if rule_key not in setting_rules:
        return f"{location} background"
    
    setting_rule = setting_rules[rule_key]
    treatment = setting_rule.get('treatment', '')
    elements = setting_rule.get('elements', '')
    background = setting_rule.get('background', '')
    
    parts = [f"{location} {treatment}"]
    if elements:
        parts.append(f"with {elements}")
    if background:
        parts.append(background)
    
    # Add time of day if present
    if setting.get('time'):
        parts.append(f"at {setting['time']}")
    
    return ', '.join(parts)


def transform_colors(colors: list[str], rules: Dict, params: Dict) -> str:
    """Transform colors based on category rules."""
    
    color_rules = rules.get('color_rules', {})
    mappings = color_rules.get('mappings', {})
    saturation = params.get('color_saturation', color_rules.get('saturation', 'medium'))
    
    if not colors:
        # Use category default
        default = color_rules.get('default_palette', 'natural balanced colors')
        return f"{default}, {saturation} saturation"
    
    # Transform each color
    transformed = []
    for color in colors:
        if color in mappings:
            if isinstance(mappings[color], str):
                transformed.append(mappings[color])
            else:
                # Multiple options, pick first
                transformed.append(mappings[color])
        else:
            transformed.append(color)
    
    # Add complementary if rule says so
    if color_rules.get('always_add') == 'complementary accent color':
        transformed.append('with complementary accent')
    
    palette_desc = ', '.join(transformed[:3])  # Limit to 3 colors
    
    # Add saturation and other properties
    result = [f"color palette of {palette_desc}"]
    result.append(f"{saturation} saturation")
    
    if not color_rules.get('gradients', True):
        result.append("flat colors with no gradients")
    
    max_colors = color_rules.get('max_colors')
    if max_colors:
        result.append(f"limited to {max_colors} colors maximum")
    
    return ', '.join(result)


def transform_effects(category: str, components: Dict, params: Dict) -> str:
    """Add category-specific effects and finishing touches."""
    
    effects_map = {
        'mascot_theater': [
            'white starburst highlights on curved surfaces',
            'radial sunburst background lines',
            'scattered floating sparkle effects',
            'thick drop shadows for depth'
        ],
        'health_halo': [
            'soft lens bokeh in background',
            'natural dust particles visible in light beam',
            'subtle vignette framing',
            'shallow depth of field'
        ],
        'nostalgia_revival': [
            'visible halftone dot pattern',
            'slight paper texture and grain',
            'intentional registration offset for vintage print feel',
            'limited spot color separation'
        ],
        'premium_disruptor': [
            'gold foil catching single light source',
            'extreme rim lighting creating halo',
            'selective focus with razor-thin depth of field',
            'dramatic shadows in 90% of composition'
        ],
        'kid_chaos': [
            'speed lines radiating from all edges',
            'explosive starburst effects in multiple neon colors',
            'lightning bolts and electricity crackling',
            'holographic rainbow gradient overlays',
            'motion blur trails showing energy'
        ],
        'transparent_honest': [
            'crisp sharp focus throughout with no artistic blur',
            'even clinical lighting eliminating shadows',
            'grid overlay with measurements visible',
            'labeled components and specifications'
        ],
        'adventure_fantasy': [
            'volumetric god rays breaking through atmosphere',
            'magical particle effects floating in air',
            'dramatic rim lighting with colored gels',
            'ethereal glow on mystical elements',
            'cinematic lens flare'
        ]
    }
    
    effects = effects_map.get(category, [])
    
    # Adjust based on params
    density = params.get('composition_density', 0.7)
    if density < 0.5:
        effects = effects[:2]  # Fewer effects for minimal
    elif density > 0.8:
        # All effects
        pass
    else:
        effects = effects[:3]  # Medium amount
    
    return ', '.join(effects)


def transform_typography(subject: Dict, category: str, params: Dict) -> Optional[str]:
    """Add typography element if category uses it."""
    
    subject_name = subject.get('name', 'AWESOME')
    profession = subject.get('profession', subject_name)
    
    if category == 'mascot_theater':
        text = f"{profession.upper()} CRUNCH"
        return f"bubbly curved typography spelling '{text}' arcing over scene, thick inline and outline effects"
    
    elif category == 'kid_chaos':
        text = f"{profession.upper()} BLAST"
        return f"chrome metallic text spelling '{text}' with lightning bolt letters, extreme 3D extrusion, neon glow"
    
    elif category == 'nostalgia_revival':
        era = params.get('era', '1970s')
        text = f"{profession.upper()} - SINCE {era[:4]}"
        return f"hand-lettered {era} typography reading '{text}', distressed letterpress texture, slab serif style"
    
    return None

"""
Cereal Box Style MCP Server

Transforms user image prompts through 7 cereal box design aesthetics:
- Mascot Theater: Cartoon characters, bright colors, dynamic energy
- Health Halo: Minimalist natural photography, muted tones
- Nostalgia Revival: Vintage screen print aesthetic, limited palettes
- Premium Disruptor: Black backgrounds, metallics, luxury minimal
- Kid Chaos: Neon explosion, maximum density, extreme angles
- Transparent Honest: Clinical infographics, labeled components
- Adventure Fantasy: Cinematic epic scale, magical effects
"""

from fastmcp import FastMCP
from pathlib import Path
import json
from typing import Dict, List, Optional

from .tools.parser import parse_prompt_components
from .tools.transformer import apply_category_transformation
from .tools.utils import (
    calculate_semantic_weights,
    order_by_importance,
    generate_negative_prompt
)

# Initialize FastMCP
mcp = FastMCP("Cereal Box Style Transformer")

# Load data files
DATA_DIR = Path(__file__).parent / "data"
CATEGORIES = json.loads((DATA_DIR / "categories.json").read_text())
TRANSFORMATION_MAPS = json.loads((DATA_DIR / "transformation_maps.json").read_text())
TEMPLATES = json.loads((DATA_DIR / "templates.json").read_text())


@mcp.tool()
def parse_prompt(user_prompt: str) -> Dict:
    """
    Parse user's natural language prompt into semantic components.
    
    Extracts:
    - subject: Primary focus (type, attributes, profession, count)
    - action: What they're doing (verb, energy_level, object)
    - setting: Where it's happening (type, location, atmosphere)
    - objects: Secondary props mentioned
    - colors: Color keywords found
    - mood: Emotional tone (emotion, intensity)
    - semantic_weights: Importance scores for each component
    
    Example:
        Input: "a tired chef tasting soup in a busy kitchen"
        Output: {
            'subject': {'type': 'human', 'profession': 'chef', 'attributes': ['tired']},
            'action': {'verb': 'tasting', 'object': 'soup', 'energy_level': 'low'},
            'setting': {'type': 'indoor_specific', 'location': 'kitchen', 'attributes': ['busy']},
            'semantic_weights': {'subject': 35, 'action': 30, 'setting': 25, ...}
        }
    """
    
    components = parse_prompt_components(user_prompt, TRANSFORMATION_MAPS)
    components['semantic_weights'] = calculate_semantic_weights(components)
    
    return components


@mcp.tool()
def get_available_categories() -> Dict:
    """
    List all available cereal box categories with descriptions.
    
    Returns dictionary of category names and their visual DNA.
    Use this to show users what styles are available or to help
    them choose which aesthetic fits their vision.
    
    Returns:
        {
            'mascot_theater': {
                'description': '...',
                'visual_dna': ['cartoon character', 'bold outlines', ...]
            },
            ...
        }
    """
    
    return {
        name: {
            'description': cat['description'],
            'visual_dna': cat['visual_dna'],
            'ideal_for': cat.get('ideal_subjects', []),
            'mood_match': cat.get('compatible_moods', [])
        }
        for name, cat in CATEGORIES.items()
    }


@mcp.tool()
def suggest_category(parsed_components: Dict) -> Dict:
    """
    Suggest best category based on parsed prompt components.
    
    Analyzes the parsed prompt and scores each category based on:
    - Subject type compatibility
    - Mood alignment
    - Keyword triggers
    - Energy level match
    
    Args:
        parsed_components: Output from parse_prompt tool
    
    Returns:
        {
            'primary_suggestion': 'mascot_theater',
            'alternatives': ['kid_chaos', 'nostalgia_revival'],
            'scores': {'mascot_theater': 8, 'kid_chaos': 6, ...},
            'reasoning': 'Playful subject with high energy matches...'
        }
    """
    
    scores = {}
    
    for category, rules in CATEGORIES.items():
        score = 0
        reasons = []
        
        # Score based on subject type
        subject_type = parsed_components.get('subject', {}).get('type')
        if subject_type in rules.get('ideal_subjects', []):
            score += 3
            reasons.append(f"Subject type '{subject_type}' is ideal for this category")
        
        # Score based on mood
        mood = parsed_components.get('mood', {}).get('emotion')
        if mood in rules.get('compatible_moods', []):
            score += 2
            reasons.append(f"Mood '{mood}' aligns with category aesthetic")
        
        # Score based on energy level
        action_energy = parsed_components.get('action', {}).get('energy_level', 'medium')
        if category in ['kid_chaos', 'mascot_theater'] and action_energy in ['high', 'extreme']:
            score += 2
            reasons.append("High energy matches dynamic category")
        elif category in ['health_halo', 'premium_disruptor'] and action_energy == 'low':
            score += 2
            reasons.append("Low energy suits minimalist aesthetic")
        
        # Score based on keyword triggers
        prompt_text = str(parsed_components).lower()
        for keyword in rules.get('trigger_keywords', []):
            if keyword in prompt_text:
                score += 1
        
        scores[category] = {'score': score, 'reasons': reasons}
    
    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    return {
        'primary_suggestion': ranked[0][0],
        'alternatives': [cat for cat, _ in ranked[1:3]],
        'scores': {cat: data['score'] for cat, data in scores.items()},
        'reasoning': '; '.join(ranked[0][1]['reasons']) if ranked[0][1]['reasons'] else 'General compatibility'
    }


@mcp.tool()
def get_category_rules(category: str) -> Dict:
    """
    Retrieve transformation rules for a specific cereal box category.
    
    Args:
        category: One of: mascot_theater, health_halo, nostalgia_revival,
                 premium_disruptor, kid_chaos, transparent_honest, adventure_fantasy
    
    Returns:
        Complete rule set including:
        - visual_dna: Core aesthetic markers
        - subject_rules: How to transform different subject types
        - action_rules: How to visualize different energy levels
        - setting_rules: Background treatment
        - color_rules: Color transformation mappings
        - mandatory_markers: Required style keywords
        - negative_prompts: Things to avoid
    
    Raises:
        ValueError: If category not found
    """
    
    if category not in CATEGORIES:
        available = list(CATEGORIES.keys())
        raise ValueError(f"Unknown category: {category}. Available: {available}")
    
    return CATEGORIES[category]


@mcp.tool()
def apply_transformations(
    parsed_components: Dict,
    category: str,
    style_params: Optional[Dict] = None
) -> Dict:
    """
    Apply category-specific transformations to parsed components.
    
    This is the deterministic mapping layer - converts parsed elements
    into category-appropriate visual descriptions.
    
    Args:
        parsed_components: Output from parse_prompt
        category: Cereal box category name
        style_params: Optional adjustments:
            - energy_level: 0.0-1.0 (intensity multiplier)
            - color_saturation: 'pastel', 'bright', 'neon'
            - era: '1960s', '1970s', '1980s', '1990s' (for nostalgia_revival)
            - metallic_accent: 'gold', 'silver', 'copper' (for premium_disruptor)
            - outline_weight: 'thin', 'medium', 'thick' (for mascot_theater)
    
    Returns:
        Transformed components ready for prompt assembly:
        {
            'subject': 'cartoon chef character with oversized white hat...',
            'action': 'holding comically oversized soup spoon...',
            'setting': 'simplified kitchen background...',
            'colors': 'bright primary colors with high saturation...',
            'effects': 'white starbursts, motion lines...',
            'style_markers': ['cartoon character', 'bold outlines', ...],
            'typography': 'bubbly curved typography...' (if applicable)
        }
    """
    
    if category not in CATEGORIES:
        raise ValueError(f"Unknown category: {category}")
    
    rules = CATEGORIES[category]
    params = style_params or {}
    
    transformed = apply_category_transformation(
        parsed_components,
        rules,
        TRANSFORMATION_MAPS,
        params
    )
    
    return transformed


@mcp.tool()
def build_prompt_skeleton(
    transformed_components: Dict,
    category: str,
    semantic_weights: Dict
) -> Dict:
    """
    Assemble transformed components into structured prompt skeleton.
    
    Creates the prompt structure with proper ordering and emphasis,
    ready for LLM creative synthesis.
    
    Args:
        transformed_components: Output from apply_transformations
        category: Category name (for template selection)
        semantic_weights: Component importance scores
    
    Returns:
        {
            'sections': Ordered dict of prompt sections,
            'emphasis': Weight adjustments for each section,
            'template': Category template structure,
            'negative_prompt': Generated negative prompt,
            'metadata': {
                'category': category name,
                'estimated_tokens': rough token count,
                'ready_for_synthesis': True
            }
        }
    """
    
    template = TEMPLATES[category]
    
    # Order sections by importance
    ordered_sections = order_by_importance(
        transformed_components,
        semantic_weights,
        template['emphasis_order']
    )
    
    # Calculate emphasis weights for prompt syntax
    emphasis = {}
    for component, weight in semantic_weights.items():
        if weight > 60:
            emphasis[component] = 1.3  # Strong emphasis
        elif weight > 40:
            emphasis[component] = 1.15  # Medium emphasis
        elif weight > 20:
            emphasis[component] = 1.0  # Normal
        else:
            emphasis[component] = 0.85  # De-emphasize
    
    # Generate negative prompt
    negative = generate_negative_prompt(category, CATEGORIES)
    
    # Estimate tokens (rough: 1 token ≈ 4 characters)
    estimated_tokens = sum(len(str(v)) for v in ordered_sections.values()) // 4
    
    skeleton = {
        'sections': ordered_sections,
        'emphasis': emphasis,
        'template': template,
        'negative_prompt': negative,
        'metadata': {
            'category': category,
            'estimated_tokens': estimated_tokens,
            'ready_for_synthesis': True
        }
    }
    
    return skeleton


@mcp.tool()
def refine_component(
    skeleton: Dict,
    component_name: str,
    new_value: str
) -> Dict:
    """
    Modify a specific component without regenerating everything.
    
    Allows iterative refinement - user can tweak individual parts
    (subject, action, setting, colors, etc.) and get updated skeleton.
    
    Args:
        skeleton: Output from build_prompt_skeleton
        component_name: Which section to modify (subject, action, setting, colors, effects)
        new_value: New text for that component
    
    Returns:
        Updated skeleton with modified component and tracking metadata
    """
    
    if component_name not in skeleton['sections']:
        available = list(skeleton['sections'].keys())
        raise ValueError(f"Unknown component: {component_name}. Available: {available}")
    
    skeleton['sections'][component_name] = new_value
    
    # Track user modifications
    if 'user_modifications' not in skeleton['metadata']:
        skeleton['metadata']['user_modifications'] = []
    skeleton['metadata']['user_modifications'].append(component_name)
    
    # Recalculate token estimate
    skeleton['metadata']['estimated_tokens'] = sum(
        len(str(v)) for v in skeleton['sections'].values()
    ) // 4
    
    return skeleton


@mcp.tool()
def generate_variants(
    parsed_components: Dict,
    category: str,
    count: int = 3
) -> List[Dict]:
    """
    Generate multiple prompt variations with different style parameters.
    
    Useful for A/B testing or giving users options to choose from.
    Creates variants by adjusting energy levels, saturation, and density.
    
    Args:
        parsed_components: Output from parse_prompt
        category: Category to use for all variants
        count: Number of variants to generate (1-5)
    
    Returns:
        List of skeletons, each with different style parameters:
        [
            {
                'name': 'Variant 1 (Subtle)',
                'style_params': {'energy_level': 0.5, 'color_saturation': 'pastel'},
                'skeleton': {...}
            },
            ...
        ]
    """
    
    if count < 1 or count > 5:
        raise ValueError("Count must be between 1 and 5")
    
    # Define parameter variations
    param_sets = [
        {
            'name': 'Subtle',
            'energy_level': 0.5,
            'color_saturation': 'pastel',
            'composition_density': 0.4
        },
        {
            'name': 'Balanced',
            'energy_level': 0.75,
            'color_saturation': 'bright',
            'composition_density': 0.7
        },
        {
            'name': 'Intense',
            'energy_level': 1.0,
            'color_saturation': 'neon',
            'composition_density': 1.0
        },
        {
            'name': 'Vintage',
            'energy_level': 0.6,
            'color_saturation': 'muted',
            'composition_density': 0.5,
            'era': '1970s'  # For nostalgia_revival
        },
        {
            'name': 'Dramatic',
            'energy_level': 0.9,
            'color_saturation': 'bold',
            'composition_density': 0.8
        }
    ]
    
    variants = []
    
    for i, params in enumerate(param_sets[:count]):
        # Apply transformation with these params
        transformed = apply_transformations(
            parsed_components,
            category,
            params
        )
        
        # Build skeleton
        skeleton = build_prompt_skeleton(
            transformed,
            category,
            parsed_components['semantic_weights']
        )
        
        variants.append({
            'name': f"Variant {i+1} ({params['name']})",
            'style_params': params,
            'skeleton': skeleton
        })
    
    return variants


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

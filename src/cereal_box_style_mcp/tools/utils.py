"""Utility functions for weighting, ordering, and prompt generation."""

from typing import Dict, List


def calculate_semantic_weights(components: Dict) -> Dict:
    """Calculate importance scores for each component (0-100)."""
    
    weights = {
        'subject': 0,
        'action': 0,
        'setting': 0,
        'objects': 0,
        'colors': 0,
        'mood': 0
    }
    
    # Base weights
    if components.get('subject', {}).get('name'):
        weights['subject'] = 40
    if components.get('action', {}).get('verb'):
        weights['action'] = 30
    if components.get('setting', {}).get('location'):
        weights['setting'] = 15
    if components.get('objects'):
        weights['objects'] = 10
    if components.get('mood', {}).get('emotion'):
        weights['mood'] = 5
    
    # Adjust based on specificity
    subject = components.get('subject', {})
    if len(subject.get('attributes', [])) > 1 or subject.get('profession'):
        weights['subject'] += 10  # Very specific subject
    
    action = components.get('action', {})
    if action.get('energy_level') in ['high', 'extreme']:
        weights['action'] += 10  # High energy action is important
    
    setting = components.get('setting', {})
    if setting.get('type', '').endswith('_specific'):
        weights['setting'] += 10  # Specific location matters
    
    # Normalize to 100
    total = sum(weights.values())
    if total > 0:
        for key in weights:
            weights[key] = int((weights[key] / total) * 100)
    
    return weights


def order_by_importance(
    components: Dict,
    semantic_weights: Dict,
    emphasis_order: List[str]
) -> Dict:
    """Order components by category emphasis and semantic weight."""
    
    ordered = {}
    
    # Follow category emphasis order first
    for key in emphasis_order:
        if key in components and components[key]:
            ordered[key] = components[key]
    
    # Add any remaining components
    for key, value in components.items():
        if key not in ordered and value:
            ordered[key] = value
    
    return ordered


def generate_negative_prompt(category: str, categories: Dict) -> str:
    """Generate negative prompt to avoid unwanted elements."""
    
    # Universal negatives
    universal = [
        'blurry',
        'low quality',
        'distorted',
        'deformed',
        'watermark',
        'text overlay',
        'signature',
        'cropped',
        'out of frame'
    ]
    
    # Category-specific negatives
    category_negatives = categories.get(category, {}).get('negative_prompts', [])
    
    all_negatives = universal + category_negatives
    
    return ', '.join(all_negatives)

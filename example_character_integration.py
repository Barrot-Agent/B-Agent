"""
Example Integration: Character Figure Search for Research Initiatives

Demonstrates how to use the character figure search system to discover capabilities,
transform them into practical implementations, and optimize them for research goals.
"""

import json
from character_figure_search import (
    CharacterFigureDatabase,
    CapabilityTransformer,
    CapabilityPermutator
)


def discover_capabilities_for_research(research_domain: str):
    """
    Discover and optimize character capabilities for specific research domain
    
    Args:
        research_domain: Research area (e.g., 'agi_development', 'data_processing', 'optimization')
    """
    print(f"\n{'=' * 80}")
    print(f"Research Domain: {research_domain.upper()}")
    print(f"{'=' * 80}\n")
    
    # Initialize database
    db = CharacterFigureDatabase()
    
    # Get all characters
    all_characters = db.characters
    
    print(f"Analyzing {len(all_characters)} characters across {len(db.get_all_genres())} genres...\n")
    
    # Extract all capabilities
    all_capabilities = []
    for char in all_characters:
        for cap in char.capabilities:
            all_capabilities.append({
                'character': char.name,
                'source': char.source,
                'genre': char.genre,
                'capability': cap
            })
    
    print(f"Total capabilities discovered: {len(all_capabilities)}\n")
    
    # Transform capabilities
    print("-" * 80)
    print("Top 10 Transformative Capabilities")
    print("-" * 80)
    
    transformed = []
    for item in all_capabilities:
        cap = item['capability']
        if cap.power_level in ['extreme', 'high']:
            trans = CapabilityTransformer.transform_capability(cap)
            trans['character'] = item['character']
            trans['genre'] = item['genre']
            transformed.append(trans)
    
    # Sort by impact
    impact_order = {'transformative': 4, 'significant': 3, 'moderate': 2, 'minor': 1}
    transformed_sorted = sorted(
        transformed,
        key=lambda x: impact_order.get(x['implementation']['impact'], 0),
        reverse=True
    )
    
    for i, trans in enumerate(transformed_sorted[:10], 1):
        print(f"\n{i}. {trans['fictional_ability']} ({trans['character']})")
        print(f"   Genre: {trans['genre']}")
        print(f"   Framework: {trans['framework_feature']}")
        print(f"   Impact: {trans['implementation']['impact']}")
        print(f"   Priority: {trans['implementation']['priority']}")
    
    # Augment for research domain
    print(f"\n{'-' * 80}")
    print(f"Augmented Capabilities for {research_domain}")
    print(f"{'-' * 80}\n")
    
    augmented = []
    for item in all_capabilities[:5]:  # Top 5 for example
        aug = CapabilityPermutator.augment_for_research(
            item['capability'],
            research_domain
        )
        aug['character'] = item['character']
        augmented.append(aug)
    
    for aug in augmented:
        print(f"• {aug['original_capability']} ({aug['character']})")
        print(f"  → {aug['augmented_feature']}")
        print(f"  Power: {aug['enhanced_power_level']}")
        print()
    
    # Generate capability combinations
    print(f"{'-' * 80}")
    print(f"Novel Capability Combinations")
    print(f"{'-' * 80}\n")
    
    # Combine different categories
    physical_caps = [item for item in all_capabilities if item['capability'].category == 'physical']
    mental_caps = [item for item in all_capabilities if item['capability'].category == 'mental']
    magical_caps = [item for item in all_capabilities if item['capability'].category == 'magical']
    
    if physical_caps and mental_caps:
        combo1 = CapabilityPermutator.combine_capabilities(
            physical_caps[0]['capability'],
            mental_caps[0]['capability']
        )
        print(f"Physical + Mental Hybrid:")
        print(f"  {combo1['hybrid_name']}")
        print(f"  Synergy: {combo1['synergy_mapping']}")
        print(f"  Power Level: {combo1['combined_power_level']}")
        print()
    
    if magical_caps and mental_caps and len(mental_caps) > 1:
        combo2 = CapabilityPermutator.combine_capabilities(
            magical_caps[0]['capability'],
            mental_caps[1]['capability']
        )
        print(f"Magical + Mental Hybrid:")
        print(f"  {combo2['hybrid_name']}")
        print(f"  Synergy: {combo2['synergy_mapping']}")
        print(f"  Power Level: {combo2['combined_power_level']}")
        print()
    
    # Generate matrix
    print(f"{'-' * 80}")
    print(f"Capability Matrix Analysis")
    print(f"{'-' * 80}\n")
    
    matrix = CapabilityPermutator.generate_capability_matrix(all_characters)
    
    print(f"Total Capabilities: {matrix['total_capabilities']}")
    print(f"Cross-Genre Sources: {matrix['cross_genre_potential']}")
    print()
    
    print("Distribution by Category:")
    for category, count in sorted(matrix['capability_categories'].items(), key=lambda x: x[1], reverse=True):
        bar = '█' * (count // 2)
        print(f"  {category:15s} [{count:2d}] {bar}")
    print()
    
    print("Distribution by Power Level:")
    for level, count in sorted(matrix['power_distribution'].items(), key=lambda x: x[1], reverse=True):
        bar = '█' * (count // 2)
        print(f"  {level:15s} [{count:2d}] {bar}")
    
    return {
        'total_capabilities': len(all_capabilities),
        'transformed': transformed_sorted[:10],
        'augmented': augmented,
        'matrix': matrix
    }


def export_capabilities_to_json(output_file: str = "discovered_capabilities.json"):
    """Export all discovered capabilities to JSON file"""
    db = CharacterFigureDatabase()
    
    export_data = {
        'timestamp': db.characters[0].discovered_at if db.characters else None,
        'total_characters': len(db.characters),
        'genres': db.get_all_genres(),
        'capability_types': db.get_all_capability_types(),
        'characters': db.export_all()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print(f"Exported to {output_file}")
    print(f"{'=' * 80}\n")
    print(f"Total characters: {export_data['total_characters']}")
    print(f"Genres: {', '.join(export_data['genres'])}")
    print(f"File size: {len(json.dumps(export_data))} bytes")


def search_by_genre_examples():
    """Show examples of searching by genre"""
    db = CharacterFigureDatabase()
    
    print(f"\n{'=' * 80}")
    print("Genre-Based Discovery Examples")
    print(f"{'=' * 80}\n")
    
    genres = db.get_all_genres()
    
    for genre in genres:
        chars = db.search(genre=genre)
        print(f"{genre.upper().replace('_', ' ')} ({len(chars)} characters)")
        for char in chars:
            cap_count = len(char.capabilities)
            high_power = sum(1 for c in char.capabilities if c.power_level in ['extreme', 'high'])
            print(f"  • {char.name:25s} - {cap_count} capabilities ({high_power} high-power)")
        print()


def recommend_for_barrot_initiatives():
    """Recommend capabilities optimized for Barrot's research initiatives"""
    db = CharacterFigureDatabase()
    
    print(f"\n{'=' * 80}")
    print("Capability Recommendations for Barrot's Research Initiatives")
    print(f"{'=' * 80}\n")
    
    initiatives = [
        ('AGI Development', 'mental'),
        ('Quantum Computing', 'temporal'),
        ('Data Transformation', 'magical'),
        ('System Optimization', 'physical'),
        ('Multi-Agent Systems', 'social')
    ]
    
    for initiative, preferred_category in initiatives:
        print(f"\n{initiative}:")
        print(f"{'-' * 40}")
        
        # Find capabilities matching category
        matching = []
        for char in db.characters:
            for cap in char.capabilities:
                if cap.category == preferred_category or cap.power_level == 'extreme':
                    matching.append({
                        'char': char.name,
                        'cap': cap.name,
                        'mapping': cap.real_world_mapping,
                        'feature': cap.framework_feature,
                        'power': cap.power_level
                    })
        
        # Show top 3
        for item in matching[:3]:
            print(f"  ✓ {item['cap']} ({item['char']})")
            print(f"    → {item['feature']}")
            print(f"    Power: {item['power']}")


def main():
    """Main execution"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     Character Figure Search & Capability Integration System                  ║
║     Dynamic Discovery | Real-World Transformation | Research Optimization    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Search by genre examples
    search_by_genre_examples()
    
    # Discover capabilities for research domains
    research_domains = [
        'agi_development',
        'data_processing',
        'system_optimization'
    ]
    
    for domain in research_domains:
        results = discover_capabilities_for_research(domain)
    
    # Show recommendations
    recommend_for_barrot_initiatives()
    
    # Export to JSON
    export_capabilities_to_json()
    
    print(f"\n{'=' * 80}")
    print("Integration complete! Capabilities ready for Barrot's use.")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()

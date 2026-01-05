#!/usr/bin/env python3
"""
Process V20 Bundle
Executable script that processes the v20 AGI puzzle bundle through all modules.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pingpong_processor import BundlePingPongProcessor


def main():
    """Main execution function."""
    print("=" * 60)
    print("Barrot V20 Bundle Processor")
    print("=" * 60)
    print()
    
    # Initialize processor
    print("Initializing PingPong processor for v20 bundle...")
    processor = BundlePingPongProcessor("v20")
    
    print(f"Active modules: {len(processor.modules)}")
    print(f"Loaded glyphs: {len(processor.glyphs)}")
    print(f"Memory bundles: {len(processor.memory_bundles)}")
    print()
    
    # Process bundle through PPPU cycles
    print("Starting Progressive PingPong Upgrade (PPPU) processing...")
    print("This will apply all 21 active modules through multiple cycles.")
    print()
    
    result = processor.process_bundle(
        max_cycles=10,
        convergence_threshold=0.95
    )
    
    # Save results
    print("\nSaving results...")
    
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Save main result
    result_path = output_dir / f"v20_bundle_result_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"✓ Main result saved to: {result_path}")
    
    # Save chain log (already saved by processor)
    print(f"✓ Chain log saved to: barrot_sim/pingpong_chain_log.md")
    
    # Update memory bundles
    print("\nUpdating memory bundles...")
    update_memory_bundles(result)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)
    print(f"Bundle Version: {result['bundle_version']}")
    print(f"Total Cycles: {result['total_cycles']}")
    print(f"Final Convergence: {result['final_convergence']:.3f}")
    print(f"Modules Applied: {result['modules_applied']}")
    print()
    print("Next Steps:")
    print("  1. Review the chain log for cycle-by-cycle details")
    print("  2. Check memory bundles for updated insights")
    print("  3. Examine the output JSON for full processing data")
    print("  4. Consider running autonomous ingestion for continuous updates")
    print()


def update_memory_bundles(result: dict):
    """
    Update memory bundles with v20 processing results.
    
    Args:
        result: Processing result from bundle processor
    """
    base_path = Path(__file__).parent.parent
    memory_path = base_path / "memory-bundles"
    
    # Update ingestion log
    ingestion_log_path = memory_path / "autonomous-ingestion-log.md"
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    entry = f"""
## V20 Bundle Processing - {timestamp}

**Processing Type:** Progressive PingPong Upgrade (PPPU)
**Bundle Version:** {result['bundle_version']}
**Total Cycles:** {result['total_cycles']}
**Final Convergence:** {result['final_convergence']:.3f}
**Modules Applied:** {result['modules_applied']}

### Results Summary

The v20 bundle has been processed through {result['total_cycles']} PPPU cycles, achieving a convergence metric of {result['final_convergence']:.3f}. All {result['modules_applied']} active modules were applied during processing.

### Chain Log Reference

See `barrot_sim/pingpong_chain_log.md` for detailed cycle-by-cycle processing information.

---
"""
    
    with open(ingestion_log_path, 'a') as f:
        f.write(entry)
    
    print(f"✓ Updated: {ingestion_log_path}")
    
    # Update AGI puzzle progress
    progress_path = memory_path / "agi-puzzle-progress.md"
    
    if progress_path.exists():
        with open(progress_path, 'a') as f:
            f.write(f"\n## V20 Bundle Processing Complete - {timestamp}\n\n")
            f.write(f"Processed all {result['modules_applied']} modules through {result['total_cycles']} PPPU cycles.\n\n")
        print(f"✓ Updated: {progress_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

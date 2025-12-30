#!/usr/bin/env python3
# barrot/runners/run_cognition_cycle.py
"""
Run a cognition cycle - analyze proof space and update lattice
"""
from barrot.core.cognition_lattice import CognitionLattice, Node, Edge
from barrot.core.proof_space import ProofSpace
from barrot.core.goals import GoalTracker, Goal, GoalStatus

def run_cognition_cycle(lattice: CognitionLattice, proof_space: ProofSpace, 
                       goal_tracker: GoalTracker) -> dict:
    """
    Execute one cycle of cognition:
    1. Review active goals
    2. Analyze proof fragments
    3. Update cognition lattice
    4. Identify new connections
    """
    print("Starting cognition cycle...")
    
    # Get active goals
    active_goals = goal_tracker.get_active_goals()
    print(f"Active goals: {len(active_goals)}")
    
    # Process each goal
    for goal in active_goals:
        fragments = proof_space.get_fragments_for_problem(goal.problem)
        print(f"Processing goal: {goal.description} ({len(fragments)} fragments)")
        
        # Add fragments as nodes to lattice
        for fragment in fragments:
            node = Node(
                id=fragment.id,
                kind="proof_fragment",
                metadata={"status": fragment.status, "problem": fragment.problem}
            )
            lattice.add_node(node)
    
    # Analyze connections between concepts
    concepts = lattice.find_by_kind("concept")
    print(f"Concepts in lattice: {len(concepts)}")
    
    return {
        "active_goals": len(active_goals),
        "total_nodes": len(lattice.nodes),
        "total_edges": len(lattice.edges),
        "concepts": len(concepts)
    }

def main():
    """Main entry point"""
    lattice = CognitionLattice()
    proof_space = ProofSpace()
    goal_tracker = GoalTracker()
    
    # Add a sample goal
    goal = Goal(
        id="goal_1",
        description="Understand Riemann Hypothesis",
        problem="riemann_hypothesis",
        priority=10
    )
    goal_tracker.add_goal(goal)
    
    # Run cycle
    results = run_cognition_cycle(lattice, proof_space, goal_tracker)
    print("\nCognition cycle complete:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()

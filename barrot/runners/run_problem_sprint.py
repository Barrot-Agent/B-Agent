#!/usr/bin/env python3
# barrot/runners/run_problem_sprint.py
"""
Run a focused sprint on a specific Millennium Problem
"""
from barrot.domains.millennium.riemann_hypothesis import RiemannHypothesis
from barrot.domains.millennium.p_vs_np import PvsNP
from barrot.domains.millennium.navier_stokes import NavierStokes
from barrot.core.proof_space import ProofSpace, ProofFragment
from barrot.core.goals import GoalTracker, Goal, GoalStatus

def run_problem_sprint(problem_name: str, duration_hours: int = 8) -> dict:
    """
    Execute a focused sprint on a problem:
    1. Load problem definition
    2. Review existing approaches
    3. Generate new proof fragments
    4. Track progress
    """
    print(f"Starting problem sprint: {problem_name}")
    print(f"Duration: {duration_hours} hours")
    
    # Initialize problem
    problems = {
        "riemann": RiemannHypothesis(),
        "p_vs_np": PvsNP(),
        "navier_stokes": NavierStokes(),
    }
    
    problem = problems.get(problem_name)
    if not problem:
        return {"error": f"Unknown problem: {problem_name}"}
    
    print(f"\nProblem: {problem.name}")
    print(f"Description: {problem.description}")
    print(f"Status: {problem.status}")
    
    # Review approaches
    approaches = problem.get_approaches()
    print(f"\nKnown approaches ({len(approaches)}):")
    for i, approach in enumerate(approaches, 1):
        print(f"  {i}. {approach}")
    
    # Initialize proof space and goals
    proof_space = ProofSpace()
    goal_tracker = GoalTracker()
    
    # Create sprint goal
    goal = Goal(
        id=f"sprint_{problem_name}",
        description=f"Make progress on {problem.name}",
        problem=problem_name,
        priority=100
    )
    goal_tracker.add_goal(goal)
    goal_tracker.update_status(goal.id, GoalStatus.IN_PROGRESS)
    
    # Generate initial proof fragments (placeholder)
    for i, approach in enumerate(approaches[:3]):  # Focus on first 3 approaches
        fragment = ProofFragment(
            id=f"fragment_{problem_name}_{i}",
            problem=problem_name,
            statement=f"Investigate {approach}",
            sketch=f"Apply {approach} to the problem",
            status="hypothesis"
        )
        proof_space.add_fragment(fragment)
    
    return {
        "problem": problem.name,
        "approaches_reviewed": len(approaches),
        "fragments_generated": len(proof_space.fragments),
        "status": "sprint_initialized"
    }

def main():
    """Main entry point"""
    import sys
    
    problem_name = sys.argv[1] if len(sys.argv) > 1 else "riemann"
    results = run_problem_sprint(problem_name)
    
    print("\nProblem sprint results:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()

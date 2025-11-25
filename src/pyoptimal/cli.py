"""
Command-line interface for PyOptimal.
"""

import argparse
import sys
from pathlib import Path
from .grammar import Grammar
from .learner import Learner


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Learn constraint rankings from OT/HG grammars"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to YAML file containing grammar and examples"
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        choices=["ot", "hg"],
        default="ot",
        help="Learning algorithm to use (default: ot)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file for learned ranking (optional)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.verbose:
            print(f"Loading grammar from {args.input_file}...")
        
        grammar = Grammar.from_yaml(str(input_path))
        
        if args.verbose:
            print(f"Grammar loaded: {len(grammar.constraints)} constraints, {len(grammar.examples)} examples")
        
        learner = Learner(grammar, algorithm=args.algorithm)
        
        if args.verbose:
            print(f"Training using {args.algorithm.upper()} algorithm...")
        
        ranking = learner.train()
        
        print(f"\nLearned constraint ranking:")
        print(ranking)
        
        if args.algorithm == "hg":
            from .hg import HGLearner
            hg_learner = HGLearner(grammar)
            hg_learner.learn()
            weights = hg_learner.get_weights()
            print(f"\nConstraint weights:")
            for c_name in sorted(weights.keys(), key=lambda k: weights[k], reverse=True):
                print(f"  {c_name}: {weights[c_name]:.4f}")
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(f"Constraint ranking:\n{ranking}\n")
            print(f"\nRanking saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()

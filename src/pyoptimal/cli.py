"""
Command-line interface for PyOptimal.
"""

import argparse
import sys
from pathlib import Path
from .grammar import Grammar
from .learner import Learner
from .tableau import generate_tableaux_from_yaml


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Learn constraint rankings from OT/HG grammars and generate LaTeX tableaux"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to YAML file containing grammar and examples"
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        choices=["ot", "rcd", "edcd", "gla", "maxent", "hg"],
        default="ot",
        help="Learning algorithm to use: ot (constraint demotion), rcd (recursive constraint demotion), edcd (error-driven constraint demotion), gla (gradual learning algorithm), maxent (maximum entropy), hg (harmonic grammar) (default: ot)"
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
    parser.add_argument(
        "-t", "--tableaux",
        action="store_true",
        help="Generate LaTeX tableaux for all examples"
    )
    parser.add_argument(
        "--tableaux-dir",
        type=str,
        default="tableaux",
        help="Output directory for LaTeX tableaux (default: tableaux)"
    )
    parser.add_argument(
        "--no-input-column",
        action="store_true",
        help="Exclude input column from tableaux"
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
        
        weights = None
        if args.algorithm == "hg":
            from .hg import HGLearner
            hg_learner = HGLearner(grammar)
            hg_learner.learn()
            weights = hg_learner.get_weights()
            print(f"\nConstraint weights:")
            for c_name in sorted(weights.keys(), key=lambda k: weights[k], reverse=True):
                print(f"  {c_name}: {weights[c_name]:.4f}")
        elif args.algorithm == "gla":
            from .ot import GLALearner
            gla_learner = GLALearner(grammar)
            gla_learner.learn()
            ranking_values = gla_learner.get_ranking_values()
            print(f"\nConstraint ranking values:")
            for c_name in sorted(ranking_values.keys(), key=lambda k: ranking_values[k], reverse=True):
                print(f"  {c_name}: {ranking_values[c_name]:.2f}")
        elif args.algorithm == "maxent":
            from .ot import MaxEntLearner
            maxent_learner = MaxEntLearner(grammar)
            maxent_learner.learn()
            weights = maxent_learner.get_weights()
            print(f"\nConstraint weights:")
            for c_name in sorted(weights.keys(), key=lambda k: weights[k], reverse=True):
                print(f"  {c_name}: {weights[c_name]:.4f}")
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(f"Constraint ranking:\n{ranking}\n")
            print(f"\nRanking saved to {args.output}")
        
        if args.tableaux:
            if args.verbose:
                print(f"\nGenerating LaTeX tableaux...")
            
            tableau_files = generate_tableaux_from_yaml(
                str(input_path),
                args.tableaux_dir,
                algorithm=args.algorithm,
                weights=weights,
                include_input_column=not args.no_input_column,
                ranking=ranking,
            )
            
            print(f"\nGenerated {len(tableau_files)} tableau file(s) in {args.tableaux_dir}/:")
            for filepath in tableau_files:
                print(f"  {filepath.name}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()

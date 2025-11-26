"""
Example demonstrating the use of LaTeX constraint names in tableaux.

This script shows how to use the optional 'latex' field in constraint
definitions to specify custom LaTeX formatting for constraint names
in generated tableaux.
"""

from pathlib import Path
from pyoptimal.grammar import Grammar, Constraint, Example
from pyoptimal.tableau import generate_tableaux_from_grammar

# Example 1: Using constraints with LaTeX formatting
def example_with_latex():
    """Generate a tableau with LaTeX-formatted constraint names."""
    constraints = [
        Constraint("NOCODA", "No coda consonants", latex=r"\textsc{NoCoda}"),
        Constraint("MAX", "No deletion", latex=r"\textsc{Max}"),
        Constraint("DEP", "No epenthesis", latex=r"\textsc{Dep}"),
    ]
    
    examples = [
        Example("pat", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
        Example("pat", "pat", False, {"NOCODA": 1, "MAX": 0, "DEP": 0}),
    ]
    
    grammar = Grammar(constraints, examples)
    
    # Generate tableaux - will use LaTeX names automatically
    output_dir = Path("output_latex")
    files = generate_tableaux_from_grammar(grammar, output_dir, algorithm="ot")
    
    print(f"Generated {len(files)} tableau(s) with LaTeX constraint names:")
    for f in files:
        print(f"  - {f}")

# Example 2: Loading from YAML with latex field
def example_from_yaml():
    """Load a grammar from YAML that includes latex fields."""
    yaml_path = Path(__file__).parent / "tableau_with_latex.yaml"
    
    if yaml_path.exists():
        grammar = Grammar.from_yaml(str(yaml_path))
        
        print("\nLoaded constraints:")
        for c in grammar.constraints:
            print(f"  {c.name}: {c.get_display_name()}")
        
        # Generate tableaux
        output_dir = Path("output_from_yaml")
        files = generate_tableaux_from_grammar(grammar, output_dir, algorithm="ot")
        
        print(f"\nGenerated {len(files)} tableau(s) from YAML:")
        for f in files:
            print(f"  - {f}")
    else:
        print(f"YAML file not found: {yaml_path}")

if __name__ == "__main__":
    print("=" * 60)
    print("LaTeX Constraint Names Example")
    print("=" * 60)
    
    example_with_latex()
    example_from_yaml()
    
    print("\nNote: Compile the generated .tex files with pdflatex to see the")
    print("      formatted constraint names in the tableaux.")

"""
Example demonstrating tableau generation from PyOptimal.

This script shows how to:
1. Load a grammar from YAML
2. Generate LaTeX tableaux for all examples
3. Use the tableaux in LaTeX documents
"""
from pathlib import Path
from pyoptimal.grammar import Grammar
from pyoptimal.learner import Learner
from pyoptimal.tableau import generate_tableaux_from_grammar, generate_tableaux_from_yaml


def main():
    # Example 1: Generate tableaux from a YAML file directly with learned ranking
    print("Example 1: Generating OT tableaux from YAML file with learned ranking...")
    grammar = Grammar.from_yaml("simple_ot.yaml")
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    print(f"Learned ranking: {ranking}")
    
    tableau_files = generate_tableaux_from_grammar(
        grammar=grammar,
        output_dir=Path("tableaux_output/ot"),
        algorithm="ot",
        include_input_column=True,
        ranking=ranking
    )
    
    print(f"Generated {len(tableau_files)} OT tableau file(s):")
    for filepath in tableau_files:
        print(f"  - {filepath}")
    
    # Example 2: Generate HG tableaux with weights
    print("\nExample 2: Generating HG tableaux from YAML file...")
    
    # First, load the grammar and learn weights
    # (In practice, you would use the HGLearner to get weights)
    grammar = Grammar.from_yaml("simple_hg.yaml")
    learner = Learner(grammar, algorithm="hg")
    ranking = learner.train()
    print(f"Learned ranking: {ranking}")
    
    # Mock weights for demonstration
    # In a real scenario, these would come from HGLearner
    weights = {
        "NOCODA": 1.5,
        "MAX": 2.0,
        "DEP": 0.5
    }
    
    tableau_files = generate_tableaux_from_grammar(
        grammar=grammar,
        output_dir=Path("tableaux_output/hg"),
        algorithm="hg",
        weights=weights,
        include_input_column=True,
        ranking=ranking
    )
    
    print(f"Generated {len(tableau_files)} HG tableau file(s):")
    for filepath in tableau_files:
        print(f"  - {filepath}")
    
    # Example 3: Generate tableaux without input column
    print("\nExample 3: Generating compact tableaux (no input column)...")
    grammar = Grammar.from_yaml("simple_ot.yaml")
    learner = Learner(grammar, algorithm="ot")
    ranking = learner.train()
    
    tableau_files = generate_tableaux_from_grammar(
        grammar=grammar,
        output_dir=Path("tableaux_output/compact"),
        algorithm="ot",
        include_input_column=False,
        ranking=ranking
    )
    
    print(f"Generated {len(tableau_files)} compact tableau file(s):")
    for filepath in tableau_files:
        print(f"  - {filepath}")
    
    print("\nThe generated .tex files contain tblr environments (LaTeX fragments).")
    print("To use them in a document, create a LaTeX file with the tabularray package:")
    print("\n\\documentclass{article}")
    print("\\usepackage{tabularray}")
    print("\\UseTblrLibrary{booktabs}")
    print("\\begin{document}")
    print("\\input{tableaux_output/ot/tableau_01_*.tex}")
    print("\\end{document}")
    print("\nThen compile with pdflatex, xelatex, or lualatex.")


if __name__ == "__main__":
    main()

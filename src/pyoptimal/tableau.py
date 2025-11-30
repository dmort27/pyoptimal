"""
LaTeX tableau generation for Optimality Theory and Harmonic Grammar.

This module provides functionality to generate LaTeX tableaux using the
tabularray package from Grammar objects loaded from YAML files.
"""
from typing import List, Dict, Optional
from pathlib import Path
from .grammar import Grammar, Example
from .candidate import Candidate


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text.
    
    Note: $, ^, and _ are not escaped to allow LaTeX math mode, superscripts, and subscripts.
    """
    # Process backslash first, then other characters
    # to avoid double-escaping
    result = text.replace('\\', r'\textbackslash{}')
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
    }
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result


def format_constraint_name(name: str, escape: bool = True) -> str:
    """
    Format constraint name for LaTeX output.
    
    Args:
        name: The constraint name to format
        escape: Whether to escape special LaTeX characters (default True).
                Set to False if the name is already in LaTeX format.
    
    Returns:
        Formatted constraint name
    """
    if escape:
        name = escape_latex(name)
    return name


def group_examples_by_input(examples: List[Example]) -> Dict[str, List[Example]]:
    """Group examples by their input form."""
    groups = {}
    for example in examples:
        input_form = example.input_form
        if input_form not in groups:
            groups[input_form] = []
        groups[input_form].append(example)
    return groups


def generate_ot_tableau(
    input_form: str,
    candidates: List[Example],
    constraints: List[str],
    include_input_column: bool = True,
    constraint_display_names: Optional[List[str]] = None,
) -> str:
    """
    Generate an OT tableau in LaTeX using tabularray.
    
    Args:
        input_form: The input form for this tableau
        candidates: List of candidate examples for this input
        constraints: List of constraint names in order
        include_input_column: Whether to include input column (default True)
        constraint_display_names: Optional list of display names for constraints
            (if not provided, uses constraint names)
    
    Returns:
        LaTeX code for a tblr environment (fragment, not a complete document)
    """
    # Track whether display names were explicitly provided
    escape_display_names = constraint_display_names is None
    if constraint_display_names is None:
        constraint_display_names = constraints
    lines = []
    
    # Determine column specification
    # columns: optimal marker | output | constraints
    # Note: input is shown in header above output column
    n_constraints = len(constraints)
    colspec = "c c " + "c " * n_constraints
    
    lines.append(r"\begin{tblr}{")
    lines.append(f"  colspec = {{{colspec}}},")
    lines.append(r"  row{1} = {font=\bfseries},")
    lines.append(r"  hlines,")
    lines.append(r"  vlines,")
    lines.append(r"}")
    
    # Header row
    header_parts = []
    if include_input_column:
        # Input appears above the output column
        header_parts.extend(["", f"/{escape_latex(input_form)}/"])
    else:
        # No input shown
        header_parts.extend(["", ""])
    
    for display_name in constraint_display_names:
        header_parts.append(format_constraint_name(display_name, escape=escape_display_names))
    
    lines.append("  " + " & ".join(header_parts) + r" \\")
    
    # Data rows - one per candidate
    for candidate in candidates:
        row_parts = []
        
        # Optimal marker
        if candidate.optimal:
            row_parts.append("☞")
        else:
            row_parts.append("")
        
        # Output column (input was in header above this column)
        row_parts.append(escape_latex(candidate.output_form))
        
        # Constraint violations (use original constraint names for lookups)
        for constraint in constraints:
            violation_count = candidate.violations.get(constraint, 0)
            if violation_count == 0:
                row_parts.append("")
            else:
                row_parts.append("*" * violation_count)
        
        lines.append("  " + " & ".join(row_parts) + r" \\")
    
    lines.append(r"\end{tblr}")
    
    return "\n".join(lines)


def generate_hg_tableau(
    input_form: str,
    candidates: List[Example],
    constraints: List[str],
    weights: Optional[Dict[str, float]] = None,
    include_harmony: bool = True,
    include_input_column: bool = True,
    constraint_display_names: Optional[List[str]] = None,
) -> str:
    """
    Generate an HG tableau in LaTeX using tabularray.
    
    Args:
        input_form: The input form for this tableau
        candidates: List of candidate examples for this input
        constraints: List of constraint names in order
        weights: Dictionary of constraint weights (if available)
        include_harmony: Whether to include harmony score column
        include_input_column: Whether to include input column (default True)
        constraint_display_names: Optional list of display names for constraints
            (if not provided, uses constraint names)
    
    Returns:
        LaTeX code for a tblr environment (fragment, not a complete document)
    """
    # Track whether display names were explicitly provided
    escape_display_names = constraint_display_names is None
    if constraint_display_names is None:
        constraint_display_names = constraints
    lines = []
    
    # Determine column specification
    # optimal | output | constraints | harmony (optional)
    # Note: input is shown in header above output column
    n_base = 2  # optimal, output
    colspec = "c c"
    
    colspec += " c" * len(constraints)
    if include_harmony:
        colspec += " c"
    
    lines.append(r"\begin{tblr}{")
    lines.append(f"  colspec = {{{colspec}}},")
    lines.append(r"  row{1} = {font=\bfseries},")
    if weights:
        lines.append(r"  row{2} = {font=\small\itshape},")
    lines.append(r"  hlines,")
    lines.append(r"  vlines,")
    lines.append(r"}")
    
    # Header row 1: constraint names
    header_parts = []
    if include_input_column:
        # Input appears above the output column
        header_parts.extend(["", f"/{escape_latex(input_form)}/"])
    else:
        # No input shown
        header_parts.extend(["", ""])
    
    for display_name in constraint_display_names:
        header_parts.append(format_constraint_name(display_name, escape=escape_display_names))
    
    if include_harmony:
        header_parts.append("H")
    
    lines.append("  " + " & ".join(header_parts) + r" \\")
    
    # Header row 2: weights (if provided, use original constraint names for lookups)
    if weights:
        weight_parts = []
        # Empty cells for optimal marker and output columns
        weight_parts.extend(["", ""])
        
        for constraint in constraints:
            weight = weights.get(constraint, 0.0)
            weight_parts.append(f"{weight:.2f}")
        
        if include_harmony:
            weight_parts.append("")
        
        lines.append("  " + " & ".join(weight_parts) + r" \\")
    
    # Data rows - one per candidate
    for candidate in candidates:
        row_parts = []
        
        # Optimal marker
        if candidate.optimal:
            row_parts.append("☞")
        else:
            row_parts.append("")
        
        # Output column (input was in header above this column)
        row_parts.append(escape_latex(candidate.output_form))
        
        # Constraint violations (use original constraint names for lookups)
        harmony = 0.0
        for constraint in constraints:
            violation_count = candidate.violations.get(constraint, 0)
            row_parts.append(str(violation_count) if violation_count > 0 else "")
            
            # Calculate harmony if weights provided
            if weights and include_harmony:
                weight = weights.get(constraint, 0.0)
                harmony -= weight * violation_count
        
        # Harmony score
        if include_harmony:
            row_parts.append(f"{harmony:.2f}")
        
        lines.append("  " + " & ".join(row_parts) + r" \\")
    
    lines.append(r"\end{tblr}")
    
    return "\n".join(lines)


def generate_tableaux_from_grammar(
    grammar: Grammar,
    output_dir: Path,
    algorithm: str = "ot",
    weights: Optional[Dict[str, float]] = None,
    include_input_column: bool = True,
    ranking: Optional['PartialOrder'] = None,
) -> List[Path]:
    """
    Generate LaTeX tableaux for all examples in a grammar.
    
    Args:
        grammar: Grammar object with constraints and examples
        output_dir: Directory to save tableau files
        algorithm: "ot" or "hg"
        weights: Constraint weights (for HG tableaux)
        include_input_column: Whether to include input column
        ranking: Optional PartialOrder to determine constraint ordering
    
    Returns:
        List of paths to generated tableau files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Group examples by input
    input_groups = group_examples_by_input(grammar.examples)
    
    # Get constraint names and display names
    # If ranking is provided, use it to order constraints
    if ranking:
        # Order constraints by strata (highest ranked first)
        strata = ranking.get_strata()
        ordered_constraints = []
        for stratum in strata:
            # Within each stratum, sort alphabetically for consistency
            ordered_constraints.extend(sorted(stratum, key=lambda c: c.name))
        constraint_names = [c.name for c in ordered_constraints]
        constraint_display_names = [c.get_display_name() for c in ordered_constraints]
    else:
        # Use original grammar order
        constraint_names = [c.name for c in grammar.constraints]
        constraint_display_names = [c.get_display_name() for c in grammar.constraints]
    
    generated_files = []
    
    for i, (input_form, examples) in enumerate(input_groups.items(), 1):
        # Generate filename
        safe_input = input_form.replace("/", "").replace(" ", "_")
        filename = f"tableau_{i:02d}_{safe_input}.tex"
        filepath = output_dir / filename
        
        # Generate tableau
        if algorithm.lower() == "hg":
            tableau_latex = generate_hg_tableau(
                input_form,
                examples,
                constraint_names,
                weights=weights,
                include_harmony=True,
                include_input_column=include_input_column,
                constraint_display_names=constraint_display_names,
            )
        else:  # OT
            tableau_latex = generate_ot_tableau(
                input_form,
                examples,
                constraint_names,
                include_input_column=include_input_column,
                constraint_display_names=constraint_display_names,
            )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(tableau_latex)
        
        generated_files.append(filepath)
    
    return generated_files


def generate_tableaux_from_yaml(
    yaml_path: str,
    output_dir: str,
    algorithm: str = "ot",
    weights: Optional[Dict[str, float]] = None,
    include_input_column: bool = True,
    ranking: Optional['PartialOrder'] = None,
) -> List[Path]:
    """
    Generate LaTeX tableaux from a YAML grammar file.
    
    Args:
        yaml_path: Path to YAML grammar file
        output_dir: Directory to save tableau files
        algorithm: "ot" or "hg"
        weights: Constraint weights (for HG tableaux)
        include_input_column: Whether to include input column
        ranking: Optional PartialOrder to determine constraint ordering
    
    Returns:
        List of paths to generated tableau files
    """
    grammar = Grammar.from_yaml(yaml_path)
    return generate_tableaux_from_grammar(
        grammar,
        Path(output_dir),
        algorithm=algorithm,
        weights=weights,
        include_input_column=include_input_column,
        ranking=ranking,
    )

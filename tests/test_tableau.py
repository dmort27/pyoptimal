"""
Tests for tableau generation functionality.
"""
import os
import tempfile
import shutil
from pathlib import Path
import pytest
from pyoptimal.grammar import Grammar, Constraint, Example
from pyoptimal.tableau import (
    escape_latex,
    format_constraint_name,
    group_examples_by_input,
    generate_ot_tableau,
    generate_hg_tableau,
    generate_tableaux_from_grammar,
    generate_tableaux_from_yaml,
)


class TestLatexEscape:
    def test_escape_basic_characters(self):
        assert escape_latex("test") == "test"
    
    def test_escape_ampersand(self):
        assert escape_latex("a&b") == r"a\&b"
    
    def test_escape_percent(self):
        assert escape_latex("50%") == r"50\%"
    
    def test_escape_dollar(self):
        assert escape_latex("$100") == r"\$100"
    
    def test_escape_multiple_characters(self):
        assert escape_latex("$100 & 50%") == r"\$100 \& 50\%"


class TestFormatConstraintName:
    def test_format_simple_name(self):
        assert format_constraint_name("NOCODA") == "NOCODA"
    
    def test_format_name_with_special_chars(self):
        # Constraint names with special chars should be escaped
        result = format_constraint_name("MAX_IO")
        assert r"\_" in result


class TestGroupExamples:
    def test_group_by_input(self):
        ex1 = Example("pat", "pa.ta", True, {"NOCODA": 0})
        ex2 = Example("pat", "pat", False, {"NOCODA": 1})
        ex3 = Example("tak", "ta.ka", True, {"NOCODA": 0})
        
        examples = [ex1, ex2, ex3]
        groups = group_examples_by_input(examples)
        
        assert len(groups) == 2
        assert "pat" in groups
        assert "tak" in groups
        assert len(groups["pat"]) == 2
        assert len(groups["tak"]) == 1


class TestGenerateOTTableau:
    def test_generate_simple_ot_tableau(self):
        input_form = "pat"
        candidates = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "MAX": 0, "DEP": 0}),
        ]
        constraints = ["NOCODA", "MAX", "DEP"]
        
        latex = generate_ot_tableau(input_form, candidates, constraints)
        
        # Should only contain tblr environment, not document wrapper
        assert r"\documentclass" not in latex
        assert r"\usepackage{tabularray}" not in latex
        assert r"\begin{document}" not in latex
        assert r"\end{document}" not in latex
        assert r"\begin{tblr}" in latex
        assert r"\end{tblr}" in latex
        assert "/pat/" in latex
        assert "NOCODA" in latex
        assert "MAX" in latex
        assert "DEP" in latex
        assert "☞" in latex
        assert "pa.ta" in latex
        assert "pat" in latex
    
    def test_ot_tableau_without_input_column(self):
        input_form = "pat"
        candidates = [Example("pat", "pa.ta", True, {"NOCODA": 0})]
        constraints = ["NOCODA"]
        
        latex = generate_ot_tableau(
            input_form, candidates, constraints, include_input_column=False
        )
        
        # Should have same columns (input just not shown in header)
        assert "colspec = {c c c }" in latex
        # But input should not appear in header
        assert "/pat/" not in latex
    
    def test_ot_tableau_violation_marks(self):
        input_form = "test"
        candidates = [
            Example("test", "out1", True, {"C1": 0, "C2": 1, "C3": 2}),
        ]
        constraints = ["C1", "C2", "C3"]
        
        latex = generate_ot_tableau(input_form, candidates, constraints)
        
        # Check that violations are represented correctly
        lines = latex.split("\n")
        data_lines = [l for l in lines if "out1" in l]
        assert len(data_lines) == 1
        # Should have empty, *, ** for violations 0, 1, 2
        assert " & * & **" in data_lines[0] or "& * &" in data_lines[0]


class TestGenerateHGTableau:
    def test_generate_simple_hg_tableau(self):
        input_form = "pat"
        candidates = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "MAX": 0, "DEP": 0}),
        ]
        constraints = ["NOCODA", "MAX", "DEP"]
        weights = {"NOCODA": 0.1, "MAX": 0.1, "DEP": -0.2}
        
        latex = generate_hg_tableau(
            input_form, candidates, constraints, weights=weights
        )
        
        # Should only contain tblr environment, not document wrapper
        assert r"\documentclass" not in latex
        assert r"\usepackage{tabularray}" not in latex
        assert r"\begin{document}" not in latex
        assert r"\end{document}" not in latex
        assert r"\begin{tblr}" in latex
        assert r"\end{tblr}" in latex
        assert "/pat/" in latex
        assert "NOCODA" in latex
        assert "☞" in latex
        assert "0.10" in latex  # Weight formatting
        assert "-0.20" in latex
        assert "H" in latex  # Harmony column header
    
    def test_hg_tableau_without_weights(self):
        input_form = "pat"
        candidates = [Example("pat", "pa.ta", True, {"NOCODA": 0})]
        constraints = ["NOCODA"]
        
        latex = generate_hg_tableau(
            input_form, candidates, constraints, weights=None
        )
        
        # Should not have weight row without weights
        assert "row{2}" not in latex
    
    def test_hg_tableau_harmony_calculation(self):
        input_form = "test"
        candidates = [
            Example("test", "out1", True, {"C1": 1, "C2": 2}),
        ]
        constraints = ["C1", "C2"]
        weights = {"C1": 1.0, "C2": 2.0}
        
        latex = generate_hg_tableau(
            input_form, candidates, constraints, weights=weights
        )
        
        # Harmony should be -(1*1.0 + 2*2.0) = -5.0
        assert "-5.00" in latex


class TestGenerateTableauxFromGrammar:
    def test_generate_from_grammar(self):
        constraints = [
            Constraint("NOCODA", "No codas"),
            Constraint("MAX", "No deletion"),
            Constraint("DEP", "No epenthesis"),
        ]
        examples = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "MAX": 0, "DEP": 0}),
            Example("tak", "ta.ka", True, {"NOCODA": 0, "MAX": 0, "DEP": 1}),
        ]
        grammar = Grammar(constraints, examples)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = generate_tableaux_from_grammar(
                grammar, output_dir, algorithm="ot"
            )
            
            assert len(files) == 2  # Two input forms: pat, tak
            for f in files:
                assert f.exists()
                assert f.suffix == ".tex"
                # Check file content - should only contain tblr environment
                with open(f, 'r') as fh:
                    content = fh.read()
                    assert r"\documentclass" not in content
                    assert r"\begin{tblr}" in content
                    assert r"\end{tblr}" in content
    
    def test_generate_hg_tableaux_from_grammar(self):
        constraints = [Constraint("C1"), Constraint("C2")]
        examples = [
            Example("in1", "out1", True, {"C1": 0, "C2": 1}),
            Example("in1", "out2", False, {"C1": 1, "C2": 0}),
        ]
        grammar = Grammar(constraints, examples)
        weights = {"C1": 1.0, "C2": 2.0}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = generate_tableaux_from_grammar(
                grammar, output_dir, algorithm="hg", weights=weights
            )
            
            assert len(files) == 1
            with open(files[0], 'r') as fh:
                content = fh.read()
                assert "1.00" in content  # Weight
                assert "H" in content  # Harmony column


class TestGenerateTableauxFromYAML:
    def test_generate_from_yaml(self):
        # Create a temporary YAML file
        yaml_content = """
constraints:
  - name: C1
    description: Test constraint 1
  - name: C2
    description: Test constraint 2

examples:
  - input: test
    output: output1
    optimal: true
    violations:
      C1: 0
      C2: 1
  - input: test
    output: output2
    optimal: false
    violations:
      C1: 1
      C2: 0
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            output_dir = Path(tmpdir) / "output"
            
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            
            files = generate_tableaux_from_yaml(
                str(yaml_path), str(output_dir), algorithm="ot"
            )
            
            assert len(files) == 1
            assert files[0].exists()
            
            with open(files[0], 'r') as f:
                content = f.read()
                assert "C1" in content
                assert "C2" in content
                assert "output1" in content
                assert "output2" in content


class TestTableauWithLatexField:
    def test_ot_tableau_with_latex_constraint_names(self):
        input_form = "pat"
        candidates = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "DEP": 0}),
        ]
        constraints = ["NOCODA", "DEP"]
        display_names = [r"\textsc{NoCoda}", r"\textsc{Dep}"]
        
        latex = generate_ot_tableau(
            input_form, 
            candidates, 
            constraints,
            constraint_display_names=display_names
        )
        
        # Check that latex names appear in output
        assert r"\textsc{NoCoda}" in latex
        assert r"\textsc{Dep}" in latex
        # Should only contain tblr environment
        assert r"\documentclass" not in latex
        assert r"\begin{tblr}" in latex
    
    def test_hg_tableau_with_latex_constraint_names(self):
        input_form = "pat"
        candidates = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "DEP": 0}),
        ]
        constraints = ["NOCODA", "DEP"]
        display_names = [r"\textsc{NoCoda}", r"\textsc{Dep}"]
        weights = {"NOCODA": 1.0, "DEP": 2.0}
        
        latex = generate_hg_tableau(
            input_form,
            candidates,
            constraints,
            weights=weights,
            constraint_display_names=display_names
        )
        
        # Check that latex names appear in output
        assert r"\textsc{NoCoda}" in latex
        assert r"\textsc{Dep}" in latex
        # Should only contain tblr environment
        assert r"\documentclass" not in latex
        assert r"\begin{tblr}" in latex
        assert "1.00" in latex  # Weight
    
    def test_tableaux_from_grammar_with_latex(self):
        constraints = [
            Constraint("NOCODA", "No codas", latex=r"\textsc{NoCoda}"),
            Constraint("DEP", "No epenthesis", latex=r"\textsc{Dep}"),
        ]
        examples = [
            Example("pat", "pa.ta", True, {"NOCODA": 0, "DEP": 1}),
            Example("pat", "pat", False, {"NOCODA": 1, "DEP": 0}),
        ]
        grammar = Grammar(constraints, examples)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = generate_tableaux_from_grammar(
                grammar, output_dir, algorithm="ot"
            )
            
            assert len(files) == 1
            with open(files[0], 'r') as fh:
                content = fh.read()
                # Check that latex constraint names are used
                assert r"\textsc{NoCoda}" in content
                assert r"\textsc{Dep}" in content

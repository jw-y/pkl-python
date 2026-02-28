"""
Tests for class inheritance ordering in generated Python code.

This tests the fix for https://github.com/jw-y/pkl-python/issues/9
where base classes sometimes appeared after derived classes in generated code.

The fix is implemented in codegen/src/internal/PythonNamespace.pkl using
topological sort to ensure base classes are always defined before subclasses.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path


def get_class_order(python_code: str) -> list:
    """Extract class names in order of definition from Python code."""
    pattern = r'^class\s+(\w+)'
    classes = []
    for line in python_code.split('\n'):
        match = re.match(pattern, line)
        if match:
            classes.append(match.group(1))
    return classes


def get_class_bases(python_code: str) -> dict:
    """Extract base classes for each class definition."""
    pattern = r'^class\s+(\w+)(?:\(([^)]+)\))?:'
    bases = {}
    for line in python_code.split('\n'):
        match = re.match(pattern, line)
        if match:
            class_name = match.group(1)
            base_str = match.group(2)
            if base_str:
                bases[class_name] = [b.strip() for b in base_str.split(',')]
            else:
                bases[class_name] = []
    return bases


def verify_class_order(python_code: str) -> tuple:
    """
    Verify that all base classes are defined before their subclasses.
    
    Returns:
        (is_valid, error_message)
    """
    class_order = get_class_order(python_code)
    class_bases = get_class_bases(python_code)
    
    defined = set()
    for class_name in class_order:
        bases = class_bases.get(class_name, [])
        for base in bases:
            if base in class_bases and base not in defined:
                return False, f"Class '{class_name}' uses base '{base}' before it's defined"
        defined.add(class_name)
    
    return True, None


def generate_with_local_generator(pkl_file: str, output_dir: str) -> subprocess.CompletedProcess:
    """
    Run the code generator using the local Generator.pkl.
    
    Creates a temporary generator-settings.pkl that points to the local
    codegen/src/Generator.pkl to test our local changes.
    """
    project_root = Path(__file__).parent.parent
    generator_settings_pkl = project_root / "codegen" / "src" / "GeneratorSettings.pkl"
    local_generator = project_root / "codegen" / "src" / "Generator.pkl"
    
    # Create a generator settings file pointing to local Generator.pkl
    settings_content = f'''amends "{generator_settings_pkl.absolute()}"

generateScript = "{local_generator.absolute()}"
'''
    
    with tempfile.NamedTemporaryFile("w+t", suffix=".pkl", delete=False) as settings_file:
        settings_file.write(settings_content)
        settings_file.flush()
        settings_path = settings_file.name
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pkl_gen_python",
                "--generator-settings", settings_path,
                "-o", output_dir,
                pkl_file
            ],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        return result
    finally:
        Path(settings_path).unlink()


def test_classes_pkl_ordering():
    """
    Test that codegen produces correctly ordered classes for tests/_pkl/classes.pkl.
    
    This file has multi-level inheritance:
    - Animal (abstract base)
    - Dog extends Animal
    - Greyhound extends Dog  
    - Cat extends Animal
    - House (no inheritance)
    """
    project_root = Path(__file__).parent.parent
    pkl_file = project_root / "tests" / "_pkl" / "classes.pkl"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_with_local_generator(str(pkl_file), tmpdir)
        
        assert result.returncode == 0, f"Code generation failed: {result.stderr}"
        
        generated_file = Path(tmpdir) / "classes_pkl.py"
        assert generated_file.exists(), f"Generated file not found: {generated_file}"
        
        python_code = generated_file.read_text()
        
        # Verify the code is valid Python
        compile(python_code, str(generated_file), "exec")
        
        # Verify class ordering
        is_valid, error = verify_class_order(python_code)
        assert is_valid, f"Class ordering is incorrect: {error}\n\nGenerated code:\n{python_code}"
        
        # Verify specific ordering requirements
        class_order = get_class_order(python_code)
        
        # Animal must come before Dog and Cat
        assert class_order.index("Animal") < class_order.index("Dog"), \
            "Animal should be defined before Dog"
        assert class_order.index("Animal") < class_order.index("Cat"), \
            "Animal should be defined before Cat"
        
        # Dog must come before Greyhound
        assert class_order.index("Dog") < class_order.index("Greyhound"), \
            "Dog should be defined before Greyhound"


def test_issue9_scenario():
    """
    Test the exact scenario from GitHub issue #9.
    
    With 7+ classes where B1 extends A1, the ordering was previously incorrect.
    """
    project_root = Path(__file__).parent.parent
    
    pkl_content = """\
module test_issue9

open class A1 {}
open class A2 {}
open class A3 {}
open class A4 {}
open class A5 {}
open class A6 {}
open class A7 {}

class B1 extends A1 {}
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the test pkl file
        pkl_file = Path(tmpdir) / "test_issue9.pkl"
        pkl_file.write_text(pkl_content)
        
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        result = generate_with_local_generator(str(pkl_file), str(output_dir))
        
        assert result.returncode == 0, f"Code generation failed: {result.stderr}"
        
        generated_file = output_dir / "test_issue9_pkl.py"
        assert generated_file.exists(), f"Generated file not found: {generated_file}"
        
        python_code = generated_file.read_text()
        
        # Verify the code is valid Python
        compile(python_code, str(generated_file), "exec")
        
        # Verify class ordering
        is_valid, error = verify_class_order(python_code)
        assert is_valid, f"Class ordering is incorrect: {error}\n\nGenerated code:\n{python_code}"
        
        # A1 must come before B1
        class_order = get_class_order(python_code)
        assert class_order.index("A1") < class_order.index("B1"), \
            f"A1 should be defined before B1. Order: {class_order}"

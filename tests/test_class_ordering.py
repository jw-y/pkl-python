"""
Tests for class inheritance ordering in generated Python code.

This tests the fix for https://github.com/jw-y/pkl-python/issues/9
where base classes sometimes appeared after derived classes in generated code.
"""

from pkl_gen_python import extract_class_info, reorder_classes, topological_sort


# Topological sort tests

def test_topological_sort_no_dependencies():
    """Classes with no dependencies maintain alphabetical order."""
    graph = {"A": set(), "B": set(), "C": set()}
    all_nodes = {"A", "B", "C"}
    result = topological_sort(graph, all_nodes)
    assert result == ["A", "B", "C"]


def test_topological_sort_simple_dependency():
    """Base class appears before derived class."""
    graph = {"A": set(), "B": {"A"}}
    all_nodes = {"A", "B"}
    result = topological_sort(graph, all_nodes)
    assert result.index("A") < result.index("B")


def test_topological_sort_chain_dependency():
    """Multi-level inheritance is ordered correctly."""
    graph = {"A": set(), "B": {"A"}, "C": {"B"}}
    all_nodes = {"A", "B", "C"}
    result = topological_sort(graph, all_nodes)
    assert result.index("A") < result.index("B") < result.index("C")


def test_topological_sort_diamond_dependency():
    """Diamond inheritance pattern is handled."""
    # D inherits from both B and C, which both inherit from A
    graph = {"A": set(), "B": {"A"}, "C": {"A"}, "D": {"B", "C"}}
    all_nodes = {"A", "B", "C", "D"}
    result = topological_sort(graph, all_nodes)
    assert result.index("A") < result.index("B")
    assert result.index("A") < result.index("C")
    assert result.index("B") < result.index("D")
    assert result.index("C") < result.index("D")


# Extract class info tests

def test_extract_class_info_simple_class():
    code = """
class Foo:
    pass
"""
    classes, prefix, suffix = extract_class_info(code)
    assert len(classes) == 1
    assert classes[0][0] == "Foo"
    assert classes[0][3] == set()  # no base classes


def test_extract_class_info_with_base():
    code = """
class Bar(Foo):
    pass
"""
    classes, prefix, suffix = extract_class_info(code)
    assert len(classes) == 1
    assert classes[0][0] == "Bar"
    assert classes[0][3] == {"Foo"}


def test_extract_class_info_multiple_bases():
    code = """
class Child(Parent1, Parent2):
    pass
"""
    classes, prefix, suffix = extract_class_info(code)
    assert len(classes) == 1
    assert classes[0][3] == {"Parent1", "Parent2"}


# Reorder classes tests

def test_reorder_classes_already_correct_order():
    """Code that is already in correct order is not modified."""
    code = '''from dataclasses import dataclass

@dataclass
class A:
    _registered_identifier = "test#A"


@dataclass
class B(A):
    _registered_identifier = "test#B"
'''
    result = reorder_classes(code)
    # Order is already correct, should return unchanged
    assert result == code


def test_reorder_classes_simple():
    """Derived class before base class gets reordered."""
    code = '''@dataclass
class B(A):
    pass


@dataclass
class A:
    pass
'''
    result = reorder_classes(code)
    # After reordering, A should come before B
    lines = result.split("\n")
    a_line = next(i for i, line in enumerate(lines) if "class A" in line)
    b_line = next(i for i, line in enumerate(lines) if "class B" in line)
    assert a_line < b_line


def test_reorder_classes_issue_9_scenario():
    """
    Test the exact scenario from GitHub issue #9.
    
    With 7+ classes where B1 extends A1, the ordering was incorrect
    and B1 appeared before A1.
    """
    # Simulating the problematic output from issue #9
    code = '''# Code generated from Pkl module `test`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class B1(A1):
    _registered_identifier = "test#B1"


@dataclass
class A7:
    _registered_identifier = "test#A7"


@dataclass
class A6:
    _registered_identifier = "test#A6"


@dataclass
class A5:
    _registered_identifier = "test#A5"


@dataclass
class A4:
    _registered_identifier = "test#A4"


@dataclass
class A3:
    _registered_identifier = "test#A3"


@dataclass
class A2:
    _registered_identifier = "test#A2"


@dataclass
class A1:
    _registered_identifier = "test#A1"
'''
    result = reorder_classes(code)
    
    # A1 must come before B1 in the reordered code
    lines = result.split("\n")
    a1_line = next(i for i, line in enumerate(lines) if "class A1" in line and "B1" not in line)
    b1_line = next(i for i, line in enumerate(lines) if "class B1" in line)
    assert a1_line < b1_line, f"A1 (line {a1_line}) should come before B1 (line {b1_line})"


def test_reorder_classes_multi_level_inheritance():
    """Test reordering with multiple levels of inheritance."""
    code = '''@dataclass
class C(B):
    pass


@dataclass
class B(A):
    pass


@dataclass
class A:
    pass
'''
    result = reorder_classes(code)
    lines = result.split("\n")
    a_line = next(i for i, line in enumerate(lines) if "class A:" in line)
    b_line = next(i for i, line in enumerate(lines) if "class B(A)" in line)
    c_line = next(i for i, line in enumerate(lines) if "class C(B)" in line)
    assert a_line < b_line < c_line


def test_reorder_classes_multiple_derived():
    """Test reordering with multiple classes inheriting from the same base."""
    code = '''@dataclass
class Dog(Animal):
    pass


@dataclass
class Cat(Animal):
    pass


@dataclass
class Animal:
    pass
'''
    result = reorder_classes(code)
    lines = result.split("\n")
    animal_line = next(i for i, line in enumerate(lines) if "class Animal:" in line)
    dog_line = next(i for i, line in enumerate(lines) if "class Dog" in line)
    cat_line = next(i for i, line in enumerate(lines) if "class Cat" in line)
    assert animal_line < dog_line
    assert animal_line < cat_line


def test_reorder_classes_external_base_ignored():
    """Classes inheriting from external bases (not defined in file) are handled."""
    code = '''@dataclass
class MyClass(ExternalBase):
    pass


@dataclass
class Another:
    pass
'''
    result = reorder_classes(code)
    # Should not error, ExternalBase is not in the file so no reordering needed
    assert "class MyClass" in result
    assert "class Another" in result


def test_reorder_classes_preserves_imports():
    """Import statements and comments before classes are preserved."""
    code = '''# This is a header comment
from dataclasses import dataclass

import pkl


@dataclass
class B(A):
    pass


@dataclass
class A:
    pass
'''
    result = reorder_classes(code)
    # Header should still be at the top
    assert result.startswith("# This is a header comment")
    # Imports should be preserved
    assert "from dataclasses import dataclass" in result
    assert "import pkl" in result


def test_reorder_classes_no_classes():
    """Code with no classes is returned unchanged."""
    code = '''import foo

def bar():
    pass
'''
    result = reorder_classes(code)
    assert result == code


def test_reorder_classes_produces_valid_python():
    """Ensure reordered code can be parsed as valid Python."""
    code = '''@dataclass
class B1(A1):
    _registered_identifier = "test#B1"


@dataclass
class A1:
    _registered_identifier = "test#A1"
'''
    result = reorder_classes(code)
    # Should not raise any exception
    compile(result, "<string>", "exec")

"""Integration tests for longer proofs
"""
import pytest

import euclipy.theorems as theorems
from euclipy.core import Expression, RegisteredObject
from euclipy.geometricobjects import Line, Segment, Angle
from euclipy.polygon import Triangle

@pytest.fixture(autouse=True)
def reset_registry():
    """Core fixture for all tests ensuring an empty registry at the start
    """
    RegisteredObject.reset_registry()

def test_subsegment_sum_theorem():
    """Verify theorems.theorem_subsegment_sum is working correctly
    """
    line = Line('A B C D E')
    theorems.subsegment_sum_theorem(line)
    Segment('A C').measure = 5
    Segment('C E').measure = 12
    Segment('B E').measure = 15
    assert Segment('A B').measure == 2

def test_triange_angle_sum_theorem():
    Triangle('A B C')
    Angle('A B C').measure = 60
    Angle('B C A').measure = 50
    theorems.triangle_angle_sum_theorem(Triangle('A B C'))
    assert Angle('C A B').measure == 70

def test_straight_angle_theorem():
    Line('A B C')
    Line('D B E')
    Angle('A B D').measure = 70
    theorems.straight_angle_theorem(Line('A B C'))
    assert Angle('D B C').measure == 110
    assert Angle('C B E').measure == 70

    Line('F G H')
    Line('F I J')
    Angle('H F J', reflex=False)
    assert theorems.straight_angle_theorem(Line('F G H')) is None

    Line('G L')
    Angle('L G F').measure = 90
    theorems.straight_angle_theorem(Line('F G H'))
    assert Angle('H G L').measure == 90

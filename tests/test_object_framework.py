"""Tests for euclipy
"""
import pytest

from euclipy.core import RegisteredObject, Point, Segment, Line, Expression, points
from euclipy.polygon import Polygon, Triangle
from euclipy import theorems

# Framework tests

@pytest.fixture(autouse=True)
def reset_registry():
    """Core fixture for all tests ensuring an empty registry at the start
    """
    RegisteredObject.reset_registry()

def test_reset_registry_acts_recursively():
    """Reseting a registry should reset registries for all subclasses as well
    """
    Triangle('A B C')
    assert len(Point.get_registry()) == 3
    RegisteredObject.reset_registry()
    assert len(Point.get_registry()) == 0

def test_registered_objects_are_registered():
    """Verifies that instances of RegisteredObject subclasses are registered.
    """
    assert Point('A') in Point.elements()
    assert Segment('A B') in Segment.elements()
    assert Triangle('A B C') in Triangle.elements()

def test_recursive_registry_view():
    """Test recursive view of registry used by RegisteredObject.print
    """
    Segment('A B')
    expected = (r"{'RegisteredObject': {'GeometricObject': "
                r"{'MeasurableGeometricObject': "
                r"{'Segment': {'A B': Segment(A B)}}, "
                r"'Point': {'A': Point(A), 'B': Point(B)}}}}")
    assert repr(RegisteredObject.recursive_registry()) == expected

def test_elements():
    """Test RegisteredObject.elements() is returning correct iterators
    """
    seg = Segment('A B')
    seg_elems = set(Segment.elements())
    assert set([seg]) == seg_elems
    pt_elems = set(Point.elements())
    assert set([Point('A'), Point('B')]) == pt_elems

def test_elements_recursive():
    """Test RegisteredObject.elements_recursive() is returning correct iterators
    """
    Segment('A B')
    rec_elems = set(RegisteredObject.elements_recursive())
    assert set([Segment('A B'), Point('A'), Point('B')]) == rec_elems

# Point tests

def test_points_are_cached():
    """Point instantiation with a previously used label should return original
    object, not a new object.
    """
    assert Point('A') is Point('A')

def test_valid_point_initializations():
    """Points can be initialized using valid strings.
    """
    assert Point('A') in Point.elements()
    # Multi-character strings are allowed (even though unconventional)
    assert Point('mypoint') in Point.elements()

def test_point_repr():
    """Point string representation test
    """
    assert repr(Point('A')) == 'Point(A)'

def test_invalid_point_initializations_raise_exceptions():
    """Only strings not containing spaces can be used as point labels.
    """
    with pytest.raises(ValueError):
        Point('')
    with pytest.raises(ValueError):
        Point('A ')
    with pytest.raises(ValueError):
        Point(1)
    with pytest.raises(ValueError):
        Point({'A': 1, 'B': 2})
    with pytest.raises(ValueError):
        Point({1, 2})

def test_points_function():
    """Convenience function points performs point construction as specified"""
    # Works for single point construction
    assert points('A') is Point('A')
    assert points(Point('A')) is Point('A')
    # Works for multiple point construction
    assert points('A B') == ((Point('A'), Point('B')))
    assert points((Point('A'), Point('B'))) == ((Point('A'), Point('B')))
    # Raises exception if provided a tuple of non-Point objects
    with pytest.raises(ValueError):
        points((1, 2))
    # Raises an exception if asked to construct multiple points with duplicates
    with pytest.raises(ValueError):
        points('A A')

# Segment tests

def test_segments_are_cached():
    """Segment instantiation with a previously used label (or an equivalent
    label) should return original object, not a new object.

    Segment('A B') and Segment('B A') are considered to be equivalent.
    """
    # Segment equivalence with same label
    assert Segment('A B') is Segment('A B')
    # Segment equivalence with equivalent but different label
    assert Segment('C D') is Segment('D C')

def test_invalid_segment_labels_raise_exceptions():
    """Only strings representing two points or a tuple of two points can be
    use to instantiate segments.
    """
    # Segment requires exactly two points
    with pytest.raises(ValueError):
        Segment('A')
    with pytest.raises(ValueError):
        Segment('A B C')
    with pytest.raises(ValueError):
        Segment((1, 2))

def test_segments_implicitly_create_points():
    """Creating a segment should automatically create Points for its endpoints

    Instantiating Segment('A B') should instantiate Point('A') and Point('B')
    """
    seg = Segment('A B')
    assert set(_.key for _ in Point.elements()) == {'A', 'B'}
    assert set(_.key for _ in seg.points) == {'A', 'B'}

# Polygon tests

def test_polygons_are_cached():
    """Triangle instantiation with a previously used label (or an equivalent
    label) should return original object, not a new object.

    Triangle('A B C') and Triangle('C A B') are considered to be equivalent.
    """
    # Triangle equivalence with same label
    assert Triangle('A B C') is Triangle('A B C')
    # Triangle equivalence with equivalent but different label
    assert Triangle('C A B') is Triangle('A B C')
    assert Triangle('B C A') is Triangle('A B C')
    # Polygon equivalence with equivalent but different label
    assert Polygon('D E F G') is Polygon('F G D E')

def test_polygons_implicitly_create_segments_and_points():
    """Creating a Polygon should automatically create Points for its vertices
    and Segments for its sides.

    Instantiating Polygon('A B C D') should instantiate:
        Point('A'),  Point('B'), Point('C'), Point('D')
        Segment('A B'), Segment('B C'), Segment('C D'), Segment('A D')
    """
    poly = Polygon('A B C D')
    assert set(_.key for _ in Point.elements()) == {'A', 'B', 'C', 'D'}
    assert set(_.key for _ in Segment.elements()) == {'A B', 'B C', 'C D', 'A D'}
    assert set(_.key for _ in poly.points) == {'A', 'B', 'C', 'D'}
    assert set(_.key for _ in poly.segments) == {'A B', 'B C', 'C D', 'A D'}

def test_polygon_with_3_vertices_is_triangle():
    """Instantiating a polygon with 3 vertices should return a Triangle
    """
    assert Polygon('A B C') is Triangle('A B C')

def test_polygon_repr():
    """Polygon string representation test
    """
    assert repr(Polygon('A B C D')) == 'Polygon(A B C D)'
    assert repr(Triangle('E F G')) == 'Triangle(E F G)'

def test_invalid_polygon_labels_raise_exceptions():
    """Only strings representing 3+ points or a tuple of 3+ points can be
    use to instantiate segments.
    """
    with pytest.raises(ValueError):
        Triangle('A B')
    with pytest.raises(ValueError):
        Triangle((Point('A'), Point('B')))

def test_inconsistent_polygon_raises_exception():
    """Polygons are specified with vertices in clockwise order. Attempting to
    create a new polygon that shares the same vertices as an existing polygon
    but in an order inconsistent with that existing polygon should raise an
    exception.
    """
    # Test exception for Triangle
    Triangle('A B C')
    with pytest.raises(RuntimeError):
        Triangle('C B A')
    # Test exception for Polygon
    Polygon('D E F G')
    with pytest.raises(RuntimeError):
        Polygon('D F E G')
    with pytest.raises(RuntimeError):
        Polygon('E D G F')

# Line tests

def test_lines_are_merged_when_aligned():
    """When two lines sharing 2 or more points can be unambigously aligned,
    even when points are specified in opposite order, they should be merged
    into a single line"""
    line1 = Line('A X B C D')
    line2 = Line('C F E B A')
    assert line1 is line2
    # The points are ordered, starting with lexically smallest endpoint
    assert ' '.join([_.key for _ in line1.points]) == 'A X B E F C D'

def test_line_with_fewer_than_one_point_raises_exception():
    """A Line cannot be specified with fewer than two points"""
    with pytest.raises(ValueError):
        Line('A')

def test_theorem_subsegment_sum():
    """Verify theorems.theorem_subsegment_sum is working correctly
    """
    # TODO: Replace with unit tests; this is an integration test
    line = Line('A B C D E')
    theorems.theorem_subsegment_sum(line)
    Segment('A C').measure = 5
    Segment('C E').measure = 12
    Segment('B E').measure = 15
    Expression.solve_system()
    assert Segment('A B').measure == 2

# TODO: Add tests for lines
# TODO: Add tests for measures
# TODO: Add tests for Expressions
# TODO: Add tests for Expression.solve

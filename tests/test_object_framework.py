"""Tests for euclipy's object framework
"""
import pytest

from euclipy.core import RegisteredObject, Expression
from euclipy.geometricobjects import Point, Segment, Angle, Line, Ray, points
from euclipy.polygon import Polygon, Triangle
import euclipy.exceptions as exceptions

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
                r"{'Point': {'A': Point(A), 'B': Point(B)}, "
                r"'Segment': {'A B': Segment(A B)}}}}")
    assert repr(RegisteredObject.recursive_registry()) == expected

def test_update_key():
    """Test RegisteredObject.update_key() is updating keys correctly
    """
    obj = RegisteredObject()
    obj.update_key('A')
    assert 'A' in RegisteredObject.get_registry()
    obj.update_key('B')
    assert 'B' in RegisteredObject.get_registry()
    assert 'A ' not in RegisteredObject.get_registry()

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

def test_segment_identifier():
    assert Segment('A B')._identifier == (Point('A'), Point('B'))

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

def test_line_merge_with_ambiguous_ordering_raises_exception():
    """When two lines sharing 2 or more points cannot be unambigously aligned,
    even when points are specified in opposite order, they should raise an
    exception"""
    Line('A C B')
    with pytest.raises(exceptions.ColinearPointSequenceError):
        Line('A D B')

def test_line_merge_with_inconsistent_point_alignment_raises_exception():
    """When two lines sharing 2 or more points cannot be aligned consistently,
    they should raise an exception"""
    Line('A B C')
    with pytest.raises(exceptions.ColinearPointSequenceError):
        Line('B C A')

def test_replaced_object_with_measure_delegates_to_successor():
    """When an object with measure is replaced, it should delegate
    its attributes to its successor"""
    obj1 = Segment('A B')
    obj2 = Segment('C D')
    obj1.replace(obj2)
    obj2.measure = 5
    assert obj1.measure == 5

def test_angle_construction():
    with pytest.raises(ValueError):
        Angle('A B')
    with pytest.raises(ValueError):
        Angle((Point('A'), Point('B')))
    a1 = Angle('A B C')
    a2 = Angle('A B C')
    a3 = Angle('C B A')
    assert a1 is a2
    assert a1 is not a3
    # assert a1._identifier == IntersectionAngle((Line('A B'), Line('B C'))) #TODO: REDO

def test_angle_measure():
    a1 = Angle('A B C')
    a2 = Angle('A B C')
    a1.measure = 50
    assert a1.measure == 50
    assert a1.measure == a2.measure

def test_invalid_angle_measure_raises_exception():
    a1 = Angle('A B C')
    with pytest.raises(ValueError):
        a1.measure = 360
    with pytest.raises(ValueError):
        a1.measure = 400
    with pytest.raises(ValueError):
        a1.measure = 0
    with pytest.raises(ValueError):
        a1.measure = -10    

def test_retroactive_intersection_angle_update_after_line_update():
    angle1 = Angle("A B C")
    angle2 = Angle("A B D")
    Line("B C D")
    assert angle1.measure == angle2.measure
    angle3 = Angle("E G H")
    angle4 = Angle("F G H")
    Line("E F G")
    assert angle3.measure == angle4.measure

def test_measure_substitution_preserves_specific_information():
    obj1 = Segment('A B')
    obj2 = Segment('C D')
    obj1.measure = 5
    obj1.measure = obj2.measure
    assert obj2.measure == 5

def test_measure_substitution_raises_exception_with_inconsistent_information():
    obj1 = Segment('A B')
    obj2 = Segment('C D')
    obj1.measure = 5
    obj2.measure = 6
    with pytest.raises(ValueError):
        obj1.measure = obj2.measure

def test_measure_setter_raises_exception_with_invalid_input():
    obj = Segment('A B')
    with pytest.raises(ValueError):
        obj.measure = [1, 2, 3]
    with pytest.raises(ValueError):
        obj.measure = 'x***2'

def test_point_can_be_replaced_by_other_point():
    p1 = Point('A')
    p2 = Point('B')
    p1.key = 'B'
    Point.remove_duplicates()
    assert p1._successor is p2 or p2._successor is p1

def test_line_segments_with_subsegments():
    L = Line('A B C D')
    assert set(L.segments_with_subsegments()) == {Segment('A C'), Segment('B D'), Segment('A D')}

def test_line_intersection_point():
    L1 = Line('A B C')
    with pytest.raises(ValueError):
        L1.intersection_point('A D E')
    # Single point of intersection should return that point
    L2 = Line('A D E')
    assert L1.intersection_point(L2) is Point('A')
    # Multiple common points should return None, because intersection_point
    # returns a single point if and only of the lines intersect at a single point
    L3 = Line('D A B')
    assert L1.intersection_point(L3) is None
    # No common points should return None
    L4 = Line('D E F')
    assert L1.intersection_point(L4) is None

def test_line_is_interior_of_known_points():
    L1 = Line('A B C D')
    assert L1.is_interior_of_known_points(Point('B'))
    assert not L1.is_interior_of_known_points(Point('A'))
    assert not L1.is_interior_of_known_points(Point('F'))
    with pytest.raises(ValueError):
        L1.is_interior_of_known_points('B')

def test_line_canonical_ray_direction_point():
    Line('A B C D E')
    assert Line.canonical_ray_direction_point(Point('C'), Point('D')) is Point('E')
    assert Line.canonical_ray_direction_point(Point('C'), Point('E')) is Point('E')
    assert Line.canonical_ray_direction_point(Point('C'), Point('B')) is Point('A')
    assert Line.canonical_ray_direction_point(Point('C'), Point('A')) is Point('A')
    with pytest.raises(ValueError):
        Line.canonical_ray_direction_point(Point('C'), Point('C'))


def test_segment_implicitly_makes_lines():
    S = Segment('A B')
    assert S.line is Line('A B')

def test_atomic_subsegments_of_line():
    Line('A B C D')
    assert set(Segment('A D').atomic_subsegments()) == {Segment('A B'),
                                                        Segment('B C'),
                                                        Segment('C D')}

# Ray tests

def test_ray_construction():
    """Test Ray construction
    """
    with pytest.raises(ValueError):
        Ray('A')
    assert Ray('A B')._identifier == (Point('A'), Point('B'))
    Line('D E F')
    Ray('D E')._identifier == (Point('D'), Point('F'))
    Ray('F E')._identifier == (Point('F'), Point('D'))
    assert Ray('D E') is Ray('D F')

def test_ray_when_its_line_is_modified():
    ray = Ray('A B')
    Line('A B C')
    assert ray._identifier == (Point('A'), Point('C'))
    assert ray.key == 'A C'
    Line('F E D')
    Line('E D C B')
    assert ray._identifier == (Point('A'), Point('F'))
    assert ray.key == 'A F'


# Angle tests

def test_explementary_angles():
    a1 = Angle('A B C')
    assert Angle('C B A').explementary is a1
    assert a1.explementary is Angle('C B A')
    assert a1.explementary.explementary is a1

# Expression tests

def test_expression_creation():
    s1 = Segment('A B')
    s2 = Segment('B C')
    e1 = Expression(s1.measure + s2.measure - 5)
    e2 = Expression(s1.measure - 3, predecessor=e1, substitutions={s2.measure: 2})
    assert e1._successor is e2
    assert e1._identifier == e1.expr

def test_expression_subs():
    m1 = Segment('A B').measure
    m2 = Segment('B C').measure
    m3 = Segment('C D').measure

    Expression(m1 - 5)
    assert Segment('A B').measure == 5

    e2 = Expression(m2 * m3 - 8)
    e2.subs({m2: 2})
    assert Segment('B C').measure == 2
    assert Segment('C D').measure == 4

def test_expression_subs_all_expressions():
    m1 = Segment('A B').measure
    m2 = Segment('B C').measure
    m3 = Segment('C D').measure
    Expression(m1 + m2 - 5)
    Expression(m2 + m3 - 7)
    Expression.subs_all_expressions({m2: 3})
    assert Segment('A B').measure == 2
    assert Segment('B C').measure == 3
    assert Segment('C D').measure == 4
    # assert {e.expr for e in Expression.elements()} == {m1 - 2, m3 - 4}

def test_expression_solve():
    m1 = Segment('A B').measure
    m2 = Segment('B C').measure
    m3 = Segment('C D').measure
    Expression(m1 + m2 - 5)
    Expression(m2 + m3 - 7)
    Expression(m1 + m3 - 6)
    # solution = Expression.solve_system()
    # assert solution == {m1: 2, m2: 3, m3: 4}
    assert Segment('A B').measure == 2
    assert Segment('B C').measure == 3
    assert Segment('C D').measure == 4

def test_expression_solve_with_no_solutions():
    assert Expression.solve_system() == {}
    m1 = Segment('A B').measure
    m2 = Segment('B C').measure
    Expression(m1+m2-5)
    assert Expression.solve_system() == {}

#TODO: Rename test
def test_substitution_causing_expression_to_evaluate_to_nonzero_raises_exception():
    """When an Expression evaluates to a nonzero value, it should raise an
    exception"""
    segment = Segment('A B')
    Expression(segment.measure-1)
    # with pytest.raises(exceptions.SystemOfEquationsError):
    #     segment.measure = 2
    with pytest.raises(ValueError):
        segment.measure = 2

def test_no_solution_raises_exception():
    m1 = Segment('A B').measure
    m2 = Segment('B C').measure
    Expression(m1 + m2 - 5)
    with pytest.raises(exceptions.SystemOfEquationsError):
        Expression(m1 + m2 - 6)

def test_non_unique_positive_solutions_raises_exception():
    m1 = Segment('A B').measure
    with pytest.raises(exceptions.SystemOfEquationsError):
        Expression((m1 - 5) * (m1 - 6))

def test_negative_unique_solution_raises_exception():
    m1 = Segment('A B').measure
    with pytest.raises(exceptions.SystemOfEquationsError):
        Expression(m1 + 5)

def test_nonreflex_angles_formed_by_intersection():
    l1 = Line('A B C')
    l2 = Line('D E F')
    with pytest.raises(RuntimeError):
        l1.nonreflex_angles_formed_by_intersection(l2)
    l3 = Line('D B E')
    assert l1.nonreflex_angles_formed_by_intersection(l3) == []

def test_reflexivity_of_angle_updates():
    Angle('A B C')
    Angle('A B C', reflex=True)
    assert Angle('A B C').reflex is True
    Angle('D E F', reflex=True)
    assert Angle('D E F').reflex is True
    with pytest.raises(ValueError):
        Angle('D E F', reflex=False)

def test_angle_measure_setter():
    Angle('A B C', reflex=False)
    with pytest.raises(ValueError):
        Angle('A B C').measure = 200
    Angle('D E F').measure = 180
    assert Angle('D E F').reflex is False
    with pytest.raises(ValueError):
        Angle('G H I').measure = -1

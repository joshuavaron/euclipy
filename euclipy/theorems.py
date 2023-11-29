"""Implementation of theorems
"""
from euclipy.core import Expression, RegisteredObject
from euclipy.geometricobjects import Line, Angle, Ray
from euclipy.polygon import Triangle

def definition_supplementary_angles(angles: list):
    """Prototype: Insert equations into registry for supplementary angles
    """
    Expression(sum(angle.measure for angle in angles) - 180)

def straight_angle_theorem(line: Line):
    """Prototype: Insert equations into registry for straight angles
    """
    other_lines = [other for other in Line.elements() if other is not line and other.intersection_point(line) is not None]
    for other in other_lines:
        angles = line.nonreflex_angles_formed_by_intersection(other)
        num_angles = len(angles)
        if num_angles == 1:
            continue
        if num_angles == 2:
            definition_supplementary_angles([angles[0], angles[1]])
        else:
            for _ in range(num_angles):
                definition_supplementary_angles([angles[_], angles[(_ + 1) % num_angles]])

def subsegment_sum_theorem(line: Line):
    """Prototype: Insert equations into registry for subsegment measure sums of
    subsegments of a line
    """
    # TODO: Refactor once a more concrete theorem framework is in place.
    segs = line.segments_with_subsegments()
    for seg in segs:
        Expression(seg.measure -
                   sum(_.measure for _ in seg.atomic_subsegments()))
        
def angle_addition_postulate():
    """Prototype: Insert equations into registry for angle addition postulate
    """
    angles = Angle.elements()
    angle_pairs = [(angle1, angle2) for angle1 in angles for angle2 in angles if angle1 is not angle2]
    for angle1, angle2 in angle_pairs:
        if (angle1.spanning_rays[1] is angle2.spanning_rays[0] and
            angle1.explementary is not angle2 and
            angle1.reflex is False and angle2.reflex is False):
            Expression(angle1.measure + angle2.measure - Angle((angle1.spanning_rays[0], angle2.spanning_rays[1])).measure)

def triangle_angle_sum_theorem(triangle: Triangle): # TODO: refactor to polygon angle sum theorem
    """Prototype: Insert equations into registry for triangle angle sum
    """
    angle_addition_postulate()
    if not isinstance(triangle, Triangle):
        raise ValueError("Triangle angle sum theorem requires a triangle")
    Expression(180 - sum(angle.measure for angle in triangle.angles))

def herons_formula(triangle: Triangle):
    """Prototype: Insert equations into registry for Heron's formula
    """
    if not isinstance(triangle, Triangle):
        raise ValueError("Heron's formula requires a triangle")
    a, b, c = [edge.measure for edge in triangle.edges]
    s = (a + b + c) / 2
    Expression(triangle.area - (s * (s - a) * (s - b) * (s - c)) ** 0.5)
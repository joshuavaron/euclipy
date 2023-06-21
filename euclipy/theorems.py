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
    print(f'other_lines: {other_lines}')
    for other in other_lines:
        angles = line.nonreflex_angles_formed_by_intersection(other)
        print(f'angles: {angles}')
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

def triangle_angle_sum_theorem(triangle: Triangle): # TODO: refactor to polygon angle sum theorem
    """Prototype: Insert equations into registry for triangle angle sum
    """
    if not isinstance(triangle, Triangle):
        raise ValueError("Triangle angle sum theorem requires a triangle")
    Expression(180 - sum(angle.measure for angle in triangle.angles))

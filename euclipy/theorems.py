"""Implementation of theorems
"""
from euclipy.core import Line, Expression

def theorem_subsegment_sum(line: Line):
    """Prototype: Insert equations into registry for subsegment measure sums of
    subsegments of a line
    """
    # TODO: Refactor once a more concrete theorem framework is in place.
    segs = line.segments_with_subsegments()
    for seg in segs:
        Expression(seg.measure -
                   sum(_.measure for _ in seg.atomic_subsegments()))

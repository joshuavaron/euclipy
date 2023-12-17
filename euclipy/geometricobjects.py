"""Geometric classes and functionality of euclipy.

TODO: Provide longer description of classes

Typical usage example:

    TODO: Provide usage example
"""

import functools
import sympy
from euclipy.core import GeometricObject, Expression, Measure, MeasurableProperty
import euclipy.exceptions as exceptions


@functools.total_ordering
class Point(GeometricObject):
    """A point on the Euclidean plane

    Represents a point on the Euclidean plane, identified by a string label not
    containing spaces. Upon instantiation, Points are registered in the global
    registry. Therefore, subsequent attempts to instantiate Point objects with
    the same label simply return the existing Point object with that label.

    >>> Point('A') is Point ('A')
    True

    Attributes:
        label: string label not containing spaces
        key: label is used as the key in the registry
    """
    def __new__(cls, label: str):
        if not isinstance(label, str):
            raise ValueError('Points require string labels.')
        registered_point = cls.get(label)
        if registered_point:
            return registered_point
        if label == '':
            raise ValueError('Empty string is not a valid Point label.')
        if ' ' in label:
            raise ValueError('Spaces are not permitted in Point labels.')
        return super().__new__(cls, key=label)

    @property
    def _identifier(self):
        return self.key

    def __lt__(self, obj):
        return self.key < obj.key

    def __eq__(self, obj):
        return self.key == obj.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self) -> str: # pragma: no cover
        """Provides string represetnation of point, e.g. 'Point(A)'
        """
        return f'{self.__class__.__name__}({self.key})'

def points(pts):
    """Provides standard representation of point(s) from multiple inputs

    Args:
        pts: Point, tuple of Points, or space-delimited point label(s)

    Returns:
        Point instance or a tuple of Point instances

    Raises:
        ValueError if pts is an invalid representation of point(s)

    Typical use:

    >>> points(Point('A'))
    Point(A)
    >>> points('A')
    Point(A)
    >>> points((Point('A'), Point('B')))
    (Point(A), Point(B))
    >>> points('A B')
    (Point(A), Point(B))
    """
    if isinstance(pts, Point):
        return pts
    if isinstance(pts, str):
        pts = tuple(Point(pt_label) for pt_label in pts.split(' '))
    if not (isinstance(pts, tuple) and all(isinstance(p, Point) for p in pts)):
        raise ValueError('Invalid representation of point(s) as input')
    if len(pts) != len(set(pts)):
        raise ValueError('Points are not all distinct')
    if len(pts) == 1:
        return pts[0]
    return pts


class Line(GeometricObject):
    """A line represented by ordered colinear points on the Euclidean plan

    Attributes:
        points: tuple of Points, as ordered on the line they are a part of
    """
    def __new__(cls, pts):
        pts = points(pts)
        if not (isinstance(pts, tuple) and len(pts) > 1):
            raise ValueError('Instantiating a Line requires >= 2 points.')
        canonical_points = cls.canonical_points(pts)
        key = ' '.join([p.key for p in canonical_points])
        registered = cls.get(key)
        if registered:
            return registered
        # Find objects with 2 or more common points
        reg_common_pts = [obj for obj in cls.elements()
                          if len(set(obj.points).intersection(set(pts))) > 1]
        # If objects with 2 or more common points exist, merge them
        obj = None
        if reg_common_pts:
            for registered in reg_common_pts:
                pts = cls.bidirectional_order_preserving_merge(registered.points, pts)
            pts = cls.canonical_points(pts)
            updates_made = False
            for registered in reg_common_pts:
                if registered.points != pts:
                    registered.points = pts
                    updates_made = True
            if len(reg_common_pts) > 1:
                obj = cls.remove_duplicates()
            else:
                if updates_made:
                    reg_common_pts[0].broadcast_change(None)
                obj = reg_common_pts[0]
        # No existing line has two or more points in common with the new line;
        # create a new line instance.
        else:
            obj = super().__new__(cls, key=key)
            obj.points = canonical_points
        # Create segments for all pairs of points on the line
        _ = [Segment((obj.points[i], p2))
             for i in range(len(obj.points))
             for p2 in obj.points[i+1:]]
        return obj

    @property
    def _identifier(self):
        return self.points

    def __repr__(self) -> str: # pragma: no cover
        return f'{self.__class__.__name__}({" ".join([p.key for p in self.points])})'

    @staticmethod
    def canonical_points(pts):
        """Canonical ordering of segment endpoints by lexical ordering"""
        if pts[0] < pts[-1]:
            return pts
        return tuple(reversed(pts))

    @staticmethod
    def bidirectional_order_preserving_merge(s_a, s_b):
        """Merges two sequences of points, if they can be consistently aligned
        """
        def order_preserving_merge(s_a, s_b):
            if len(s_a) == 0:
                return tuple(s_b)
            if len(s_b) == 0:
                return tuple(s_a)
            if s_a[0] == s_b[0]:
                return (s_a[0],) + tuple(order_preserving_merge(s_a[1:], s_b[1:]))
            if s_a[0] in s_b:
                return (s_b[0],) + tuple(order_preserving_merge(s_a, s_b[1:]))
            if s_b[0] in s_a:
                return (s_a[0],) + tuple(order_preserving_merge(s_a[1:], s_b))
            # Neither of the first elements are common among the two tuples
            raise exceptions.ColinearPointSequenceError(
                'Order of sequences ambiguous.', s_a, s_b)

        common_ordered_as_s_a = tuple(e for e in s_a if e in s_b)
        common_ordered_as_s_b = tuple(e for e in s_b if e in s_a)

        if common_ordered_as_s_a == common_ordered_as_s_b:
            return order_preserving_merge(tuple(s_a), tuple(s_b))
        if common_ordered_as_s_a == tuple(reversed(common_ordered_as_s_b)):
            return order_preserving_merge(tuple(s_a), tuple(reversed(s_b)))
        raise exceptions.ColinearPointSequenceError(
            'Sequences cannot be aligned consistently.', tuple(s_a), tuple(s_b))

    def segments_with_subsegments(self):
        """All segments contained in the line that have subsegments
        """
        pts = self.points
        num_pts = len(pts)
        return [Segment((pts[i], pts[i+k]))
                for k in range(2, num_pts)
                for i in range(num_pts-k)]

    def intersection_point(self, other):
        """Intersection point of two lines if and only if
        they have exactly one point in common
        """
        if not isinstance(other, Line):
            raise ValueError('Intersection point requires a Line as input')
        common_pts = set(self.points).intersection(set(other.points))
        if len(common_pts) == 1:
            return common_pts.pop()

    def is_interior_of_known_points(self, point: Point):
        """Returns True if point is interior to the line
        with respect to known points, False otherwise
        """
        if not isinstance(point, Point):
            raise ValueError('Point is required as input')
        try:
            index = self.points.index(point)
            return not (index == 0 or index == len(self.points) - 1)
        except ValueError:
            return False

    def nonreflex_angles_formed_by_intersection(self, other):
        intersection = self.intersection_point(other)
        if intersection is None:
            raise RuntimeError("Intersection angles can not be determined due to unknown intersection point.")
        pts = [self.points[0], other.points[0], self.points[-1], other.points[-1]]
        rays = [Ray((intersection, point)) if point != intersection else None for point in pts]
        num_rays = len(rays)
        angles = []
        for _ in range(num_rays):
            ray_pair = (rays[_], rays[(_ + 1) % num_rays])
            if all(ray_pair):
                angles.append(Angle(ray_pair))
        reflexivities = [angle.reflex for angle in angles]
        if any([reflex is not None for reflex in reflexivities]):
            if True in reflexivities:
                angles = [angle.explementary for angle in angles]
            for angle in angles:
                angle.reflex = False
            return angles
        else:
            return []

    @staticmethod
    def canonical_ray_direction_point(vertex: Point, pointing_to: Point):
        """Returns a the outrermost known point of a ray defined by a vertex
        and a point on the ray

        Raises: ValieError if vertex and pointing_to are the same point
        """
        line = Line((vertex, pointing_to)) # Will raise ValueError if vertex and pointing_to are the same point
        v_idx = line.points.index(vertex)
        p_idx = line.points.index(pointing_to)
        if v_idx < p_idx:
            return line.points[-1]
        if v_idx > p_idx:
            return line.points[0]

class Ray(GeometricObject):
    """A ray represented by a vertex point and another point in the
    direction the ray is pointing to
    """
    def __new__(cls, pts):
        '''Argument pts is one of the following:
        - a space separated pair of point labels representing a ray, e.g. 'B A'
        - a tuple of two Point objects
        '''
        pts = points(pts)
        if not (isinstance(pts, tuple) and len(pts) == 2):
            raise ValueError('Instantiating a Ray requires exactly 2 points.')
        vertex, pointing_to = cls.canonical_points(pts)
        registered = cls.get(f'{vertex.key} {pointing_to.key}')
        if registered:
            return registered
        # Create new instance
        obj = super().__new__(cls, key=f'{vertex.key} {pointing_to.key}')
        obj.vertex, obj.pointing_to = vertex, pointing_to
        Line((vertex, pointing_to)).call_when_changed(obj.update_pointing_to)
        return obj

    @property
    def _identifier(self):
        return (self.vertex, self.pointing_to)

    @staticmethod
    def canonical_points(pts):
        vertex, pointing_to = pts
        pointing_to = Line.canonical_ray_direction_point(vertex, pointing_to)
        return (vertex, pointing_to)

    @property
    def line(self):
        return Line((self.vertex, self.pointing_to))

    def update_pointing_to(self, old_line, new_line):
        del old_line, new_line
        self.pointing_to = Line.canonical_ray_direction_point(self.vertex, self.pointing_to)
        self.update_key(f'{self.vertex.key} {self.pointing_to.key}')

    def points_on_line_in_ray_direction(self):
        """Returns all points on the line in the direction of the ray
        """
        if self.line.points.index(self.vertex) < self.line.points.index(self.pointing_to):
            return self.line.points
        return list(reversed(self.line.points))

    def __repr__(self):
        return f'Ray({self.vertex.key} {self.pointing_to.key})'

class Segment(GeometricObject):
    """A segment represented by its two endpoints on the Euclidean plane
    """

    measure = MeasurableProperty(auto_symbol_prefix = 'mSegment')

    def __new__(cls, pts):
        '''Argument pts is one of the following:
        - a space separated pair of point labels representing a segment, e.g. 'B A'
        - a tuple of two Point objects
        '''
        pts = points(pts)
        if not (isinstance(pts, tuple) and len(pts) == 2):
            raise ValueError('Instantiating a Segment requires exactly 2 points.')
        # Construct key based on canonically ordered points
        pts = tuple(sorted(pts))
        canonical_key = ' '.join([p.key for p in pts])
        # If Segment with canonical_key is already registered, return it
        registered = cls.get(canonical_key)
        if registered:
            return registered
        # Create new instance
        obj = super().__new__(cls, key=canonical_key)
        obj.points = pts
        return obj

    def solve(self, metric='measure'):
        """Solves for the measure of the segment
        """
        super().solve(metric)
        if metric == 'measure':
            # TODO: Find a way to avoid importing outside of top level here
            from euclipy import theorems
            from euclipy.polygon import Triangle
            # Try to solve for measure using subsegment sum theorem
            theorems.subsegment_sum_theorem(self.line)
            if self.measure.is_number: # pylint: disable=no-member
                return self.measure
            # Try to solve for measure using equivalence of area formulas
            is_altitude_of = [triangle for triangle in Triangle.elements() if self in triangle.altitudes]
            for triangle in is_altitude_of:
                theorems.herons_formula(triangle)
                theorems.triangle_area_using_altitude(triangle, self)
            if self.measure.is_number: # pylint: disable=no-member
                return self.measure
            # Try to solve for measure using angle bisector theorem
            shares_point_with_angle_bisector_of = []
            for triangle in Triangle.elements():
                for bisector in triangle.angle_bisectors:
                    if (set(self.points) & set(bisector.points)) and self.line is not bisector.line:
                        shares_point_with_angle_bisector_of.append(triangle)
            for triangle in shares_point_with_angle_bisector_of:
                for bisector in triangle.angle_bisectors:
                    theorems.angle_bisector_theorem(triangle, bisector)
            if self.measure.is_number: # pylint: disable=no-member
                return self.measure
            # Try to solve for measure using pythagorean theorem
            is_edge_of_right_triangle = [triangle for triangle in Triangle.elements() if self in triangle.segments and
                                         90 in [angle.measure for angle in triangle.angles]]
            for triangle in is_edge_of_right_triangle:
                theorems.pythagorean_theorem(triangle)
            if self.measure.is_number: # pylint: disable=no-member
                return self.measure
            
        else:
            raise ValueError('Invalid metric for Segment.solve()')

    def component_of(self):
        from euclipy.polygon import Triangle
        triangles =  {triangle for triangle in Triangle.elements()
                      if self in triangle.edges}
        supersegments = {segment for segment in Segment.elements()
                         if self in segment.subsegments()}
        return supersegments | triangles

    @classmethod
    def search_registry(cls, pts):
        """Returns segment defined by pts if it exists
        Otherwise, returns None
        """
        pts = tuple(sorted(pts))
        canonical_key = ' '.join([p.key for p in pts])
        # If Segment with canonical_key is already registered, return it
        return cls.get(canonical_key)

    @property
    def _identifier(self):
        return self.points

    @property
    def line(self):
        """Returns the Line that segment lies on
        """
        return Line(self.points)

    def subsegments(self):
        """Returns a list of all subsegments of the segment, excluding itself
        """
        line_pts = self.line.points
        pt_l, pt_r = self.points
        idx_l, idx_r = line_pts.index(pt_l), line_pts.index(pt_r)
        if idx_l > idx_r:
            idx_l, idx_r = idx_r, idx_l
        seg_pts = line_pts[idx_l:idx_r+1]
        segments =  [Segment((seg_pts[i], seg_pts[j]))
                     for i in range(len(seg_pts)-1)
                     for j in range(i+1, len(seg_pts))]
        segments.remove(self)
        return segments

    def contained_points(self):
        """Returns a list of all points contained in the segment, including endpoints
        """
        line_pts = self.line.points
        pt_l, pt_r = self.points
        idx_l, idx_r = line_pts.index(pt_l), line_pts.index(pt_r)
        if idx_l > idx_r:
            idx_l, idx_r = idx_r, idx_l
        return line_pts[idx_l:idx_r+1]

    def atomic_subsegments(self):
        """Returns a list of all atomic subsegments of the segment, including itself if atomic

        Atomic subsegments are subsegments that do not contain other subsegments
        of the segment.
        """
        seg_pts = self.contained_points()
        return [Segment((seg_pts[i], seg_pts[i+1]))
                for i in range(len(seg_pts)-1)]


class Angle(GeometricObject):
    """An angle represented by 3 points on the Euclidean plane
    """

    measure = MeasurableProperty(auto_symbol_prefix='mAngle', post_set='post_set_measure')

    def __new__(cls, pts_or_rays, reflex=None): #TODO: Should reflex default to True?
        '''Argument pts is one of the following:
        - a space separated triple of point labels representing an angle, e.g. 'B A C'
        - a tuple of three Point objects

        The points are to be ordered in a clockwise fashion, for example:
        - Angle('A B C') represents the angle between Segment('A B') and Segment('B C'),
            starting at Segment('A B') and moving counterclockwise.
        '''
        if len(pts_or_rays) == 2 and isinstance(pts_or_rays[0], Ray) and isinstance(pts_or_rays[1], Ray):
            ray1, ray2 = pts_or_rays
        else:
            pts = points(pts_or_rays)
            if not (isinstance(pts, tuple) and len(pts) == 3):
                raise ValueError('Instantiating an Angle requires exactly 3 points or 2 rays.')
            ray1, ray2 = Ray((pts[1], pts[0])), Ray((pts[1], pts[2]))
        canonical_key = ' '.join([ray1.pointing_to.key, ray1.vertex.key, ray2.pointing_to.key])
        # If Angle with canonical_key is already registered, return it
        registered = cls.get(canonical_key)
        if registered:
            if reflex is not None:
                registered.reflex = reflex
            return registered
        # Create new instance
        obj = super().__new__(cls, key=canonical_key)
        obj.spanning_rays = (ray1, ray2)
        ray1.call_when_changed(obj.update_a_defining_ray)
        ray2.call_when_changed(obj.update_a_defining_ray)
        if isinstance(reflex, bool):
            obj.reflex = reflex
        obj._explementary_paired = False
        return obj

    def __repr__(self) -> str: # pragma: no cover
        measures = ', '.join([f'{k}={m.value}' for k, m in self.measures.items()])
        reflex = ', reflex=' + repr(self.reflex) if self.reflex is not None else ''
        return f'{self.__class__.__name__}({self.key}{", " if measures else ""}{measures}{reflex})'

    def update_a_defining_ray(self, old_ray, new_ray):
        if new_ray is None:
            new_ray = old_ray
        ray1, ray2 = self.spanning_rays
        if ray1 is old_ray:
            self.spanning_rays = (new_ray, ray2)
        if ray2 is old_ray:
            self.spanning_rays = (ray1, new_ray)
        ray1, ray2 = self.spanning_rays
        self.update_key(' '.join([ray1.pointing_to.key, ray1.vertex.key, ray2.pointing_to.key]))
        self.remove_duplicates()

    @property
    def reflex(self):
        if hasattr(self, "_reflex"):
            return self._reflex
        return None

    @reflex.setter
    def reflex(self, reflexivity):
        assert isinstance(reflexivity, bool)
        if self.reflex is None:
            self._reflex = reflexivity
            self.explementary.reflex = not reflexivity
            ray1, ray2 = self.spanning_rays
            ray1.line.nonreflex_angles_formed_by_intersection(ray2.line)
        elif self.reflex != reflexivity:
            raise ValueError('Angle reflexivity cannot be changed after initiation.')

    @property
    def _identifier(self):
        return self.spanning_rays

    @property
    def explementary(self):
        return Angle(self.spanning_rays[-1::-1])

    def post_set_measure(self, value):
        """Executes after MeasurableProperty measure is set
        """
        if isinstance(self.measure, sympy.Number):
            if value < 180:
                if self.reflex is True:
                    raise ValueError('Reflex angle must be >= 180 degrees.')
                self.reflex = False
            elif value > 180:
                if self.reflex is False:
                    raise ValueError('Non-reflex angle must be <= 180 degrees.')
                self.reflex = True
            else:
                if self.reflex is None:
                    self.reflex = False
            if value >= 360:
                raise ValueError('Angle  must be < 360 degrees.')
            if value <= 0:
                raise ValueError('Angle must be >  0 degrees.')
        # self.set_explementary_pair()
        for obj in [self] + Measure.objects_measured_by(value):
            if not obj._explementary_paired:
                Expression(obj.measure + obj.explementary.measure - 360)
                obj._explementary_paired = True
                obj.explementary._explementary_paired = True
        # NEXT: Refactor Expression.__init__ to call solve_system() after each expression is added

if __name__ == '__main__':
    pass

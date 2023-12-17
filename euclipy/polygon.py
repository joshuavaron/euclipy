"""Classes representing polygons on the Euclidean plane
"""
import sympy

from euclipy.core import GeometricObject, MeasurableProperty
from euclipy.geometricobjects import Segment, Angle, Ray, points

class Polygon(GeometricObject):
    """A polygon represented by its vertices on the Euclidean plane
    """

    area = MeasurableProperty(auto_symbol_prefix='Area')

    def __new__(cls, pts):
        """Find or construct new Polygon

        Args:
            pts: tuple of Points or space-delimited point labels

        Returns:
            Polygon, if number of points > 3
            Triangle, if number of points == 3

        Raises
            ValueError if fewer than 3 points is supplied
        """
        pts = points(pts)
        if len(pts) < 3:
            raise ValueError('Polygon must have at least 3 points.')
        if cls.__name__ == 'Polygon' and len(pts) == 3:
            return Triangle(pts)
        pts = cls.canonical_points(pts)
        key = ' '.join([pt.key for pt in pts])
        registered = cls.get(key)
        if registered:
            return registered
        existing_with_shared_pts = [obj for obj in cls.elements()
                                    if set(obj.points) == set(pts)]
        if existing_with_shared_pts:
            assert len(existing_with_shared_pts) == 1
            # TODO: Replace with custom error InconsistentConstructionError
            raise RuntimeError(f'Polygon{pts} is inconsistent with {existing_with_shared_pts}.')
        # Create new instance
        obj = super().__new__(cls, key=key)
        obj.points = pts
        circular_points = obj.points * 2
        obj.segments = [Segment((p1, p2)) for p1, p2
                        in zip(pts, circular_points[1:])]
        obj.angles = [Angle((p1, p2, p3)) for p1, p2, p3 in
                      zip(pts, circular_points[1:], circular_points[2:])]
        return obj

    def __repr__(self): # pragma: no cover
        return f'{self.__class__.__name__}({" ".join([p.key for p in self.points])})'

    @staticmethod
    def canonical_points(pts):
        """Provide canonical ordering of points for Polygon

        Starts with the lexically smallest point label and preserves order,
        treating sequence as a cycle.

        >>> canonical_points((Point('C'), Point('B'), Point('A')))
        (Point(A), Point(C), Point(B))
        """
        min_point_index = pts.index(min(pts))
        return pts[min_point_index:] + pts[:min_point_index]


class Triangle(Polygon):
    """A triangle represented by its three vertices on the Euclidean plane
    """
    def __new__(cls, pts):
        return super().__new__(cls, pts)
    
    def edge_opposite_vertex(self, vertex) -> Segment:
        """The edge opposite a vertex of the triangle
        """
        return Segment(tuple(set(self.points) - set([vertex])))
    
    @property
    def altitudes(self):
        """The altitudes of the triangle
        """
        altitudes = []
        for vertex in self.points:
            edge = self.edge_opposite_vertex(vertex)
            for foot in edge.line.points:
                if foot == edge.points[0]:
                    angles_to_check = [Angle((vertex, foot, edge.points[1])),
                                       Angle((edge.points[1], foot, vertex))]
                elif foot == edge.points[1]:
                    angles_to_check = [Angle((vertex, foot, edge.points[0])),
                                       Angle((edge.points[0], foot, vertex))]
                else:
                    angles_to_check = [Angle((vertex, foot, edge.points[0])),
                                    Angle((vertex, foot, edge.points[1])),
                                    Angle((edge.points[0], foot, vertex)),
                                    Angle((edge.points[1], foot, vertex))]
                if any(angle.measure == 90 for angle in angles_to_check):
                    altitudes.append(Segment((vertex, foot)))
        return altitudes
    
    @property
    def medians(self):
        """The medians of the triangle
        """
        medians = []
        for vertex in self.points:
            edge = self.edge_opposite_vertex(vertex)
            for candidate_endpoint in edge.contained_points()[1:-1]:
                edge_sub1 = Segment((edge.points[0], candidate_endpoint))
                edge_sub2 = Segment((edge.points[1], candidate_endpoint))
                if edge_sub1.measure == edge_sub2.measure:
                    medians.append(Segment((vertex, candidate_endpoint)))
        return medians

    @property
    def angle_bisectors(self):
        """The angle bisectors of the triangle
        """
        angle_bisectors = []
        for vertex in self.points:
            edge = self.edge_opposite_vertex(vertex)
            for candidate_endpoint in edge.contained_points()[1:-1]:
                angle1 = Angle((candidate_endpoint, vertex, edge.points[0]))
                angle2 = Angle((edge.points[1], vertex, candidate_endpoint))
                if angle1.measure == angle2.measure:
                    angle_bisectors.append(Segment((vertex, candidate_endpoint)))
        return angle_bisectors

    def sub_and_sur_triangles_from_existing_segments(self):
        new_triangles = set()
        existing_triangles = set(Triangle.elements())
        for vertex in self.points:
            circular_points = self.points * 2
            v_index = circular_points.index(vertex)
            other_vertices = circular_points[v_index+1:v_index+3]
            pts = Ray(tuple(other_vertices)).points_on_line_in_ray_direction()
            pts = [pt for pt in pts if Segment.search_registry((vertex, pt))] #Lines too
            new_triangles |= {Triangle((pts[i], pt2, vertex))
                              for i in range(len(pts)) for pt2 in pts[i+1:]}
        return list(new_triangles - existing_triangles)

    @classmethod
    def all_sub_and_sur_triangles(cls):
        triangles = list(cls.elements())
        existing_triangles = triangles[:]
        while triangles:
            triangle = triangles.pop()
            additions = triangle.sub_and_sur_triangles_from_existing_segments()
            triangles.extend(additions)
        new_triangles = cls.elements()
        return list(set(new_triangles) - set(existing_triangles))
    
    @classmethod
    def type_one_constructions(cls):
        cls.all_sub_and_sur_triangles()

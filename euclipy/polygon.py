"""Classes representing polygons on the Euclidean plane
"""
from euclipy.core import GeometricObject
from euclipy.geometricobjects import Segment, Angle, points

class Polygon(GeometricObject):
    """A polygon represented by its vertices on the Euclidean plane
    """
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
        canonical_pts = cls.canonical_points(pts)
        key = ' '.join([pt.key for pt in canonical_pts])
        registered = cls.get(key)
        if registered:
            return registered
        existing_with_shared_pts = [obj for obj in cls.elements()
                                    if set(obj.points) == set(canonical_pts)]
        if existing_with_shared_pts:
            assert len(existing_with_shared_pts) == 1
            # TODO: Replace with custom error InconsistentConstructionError
            raise RuntimeError('Polygon inconsistent with existing polygon.')
        # Create new instance
        return cls.__construct(key, canonical_pts)

    @classmethod
    def __construct(cls, key, canonical_pts):
        obj = super().__new__(cls)
        obj.key = key
        obj.points = canonical_pts
        circular_points = obj.points + obj.points[:2]
        obj.angles = []
        for i in range(len(obj.points)):
            obj.angles.append(
                Angle((circular_points[i], circular_points[i+1], circular_points[i+2])))
        obj.segments = [Segment((p1, p2)) for p1, p2
                        in zip(obj.points, obj.points[1:] + (obj.points[0],))]
        # obj._pred = set(obj.segments)
        # obj._op = cls.__construct
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
        return cls.__construct(points(pts))

    @classmethod
    def __construct(cls, pts):
        return super().__new__(cls, pts)

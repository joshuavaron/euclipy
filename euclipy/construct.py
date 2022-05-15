from collections import defaultdict

class Registry:
    '''Singleton registry of measures.
    '''
    def __new__(cls):
        '''entries is a dictionary with:
            - keys: _registry_key
            - values: dictionaries mapping entry labels to registered entries
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registry, cls).__new__(cls)
            cls.instance.entries = defaultdict(dict)
            cls.instance.auto_label_counter = defaultdict(int)
        return cls.instance
   
    def add_to_registry(self, entry):
        self.entries[entry._registry_key][entry.label] = entry
    
    def remove_from_registry(self, entry):
        self.entries[entry._registry_key].pop(entry.label, None)

    def get_auto_label(self, registry_key):
        self.auto_label_counter[registry_key] += 1
        return self.auto_label_counter[registry_key]

    def search_registry(self, registry_key, label):
        try:
            return self.entries[registry_key][label]
        except KeyError:
            return None

    def search_polygon(self, registry_key, points: list):
        '''Find polygon that shares points, regardless of point order
        '''
        try:
            matches = [p for p in iter(self.entries[registry_key].values()) if set(p.points) == set(points)]
            return matches[0] if matches else None
        except KeyError:
            return None

class Measure:
    def __init__(self, measure=None) -> None:
        '''If measure is None, then the measure is not yet quantified.
        '''
        self.measure = measure
        self.measured_objects = set()
        self.label = Registry().get_auto_label(self._registry_key)
        Registry().add_to_registry(self)
    
    def __repr__(self) -> str:
        return f'{self._registry_key}(#{self.label}={self.measure})'

    def _add_measured_object(self, measured_object) -> None:
        self.measured_objects.add(measured_object)

    def set_equal_to(self, other_measure):
        for measured_object in other_measure.measured_objects:
            measured_object.set_measure(self)
        Registry().remove_from_registry(other_measure)

class SegmentMeasure(Measure):
    _registry_key = 'SegmentMeasure'
    def __init__(self, measure=None) -> None:
        super().__init__(measure)

class AngleMeasure(Measure):
    _registry_key = 'AngleMeasure'
    def __init__(self, measure=None) -> None:
        super().__init__(measure)
    
class Geometry:
    def __new__(cls, label):
        entry = Registry().search_registry(cls._registry_key, label)
        if entry is None:
            cls.instance = super().__new__(cls)
            cls.instance.label = label
            Registry().add_to_registry(cls.instance)
            return cls.instance
        return entry

    def __repr__(self) -> str:
        return f'{self._registry_key}({self.label})'

    def set_measure(self, measure: Measure) -> None:
        assert not isinstance(self, Point)
        self.measure = measure
        measure._add_measured_object(self)

class Point(Geometry):
    _registry_key = 'Point'

    def __new__(cls, label):
        return super().__new__(cls, label)

class Segment(Geometry):
    _registry_key = 'Segment'

    def __new__(cls, endpoints: set):
        label = '-'.join(sorted([p.label for p in endpoints]))
        instance = super().__new__(cls, label)
        instance.endpoints = endpoints
        return instance

class Angle(Geometry):
    _registry_key = 'Angle'

    def __new__(cls, points: list):
        '''Points must be ordered such that the angle represents the clockwise motion from the first defined segment to the second defined segment.
        For example, if points = [A, B, C], then the angle is the clockwise motion from Segment(AB) to Segment(BC).
        '''
        label = '-'.join([p.label for p in points])
        instance = super().__new__(cls, label)
        instance.points = points
        return instance

class Shape(Geometry):
    def __new__(cls, label):
        return super().__new__(cls, label)

class Polygon(Shape):
    def __new__(cls, points: list):
        entry = Registry().search_polygon(cls._registry_key, points)
        points = cls.translate_shape_points(points)
        label = '-'.join([p.label for p in points])
        if entry is None:
            instance = super().__new__(cls, label)
            instance.points = points
        else:
            entry_label = '-'.join([p.label for p in entry.points])
            if label == entry_label:
                instance = entry
            else:
                raise Exception #TODO: Create custom exception
        instance.edges = [Segment(set((points + points)[i:i+2])) for i in range(len(points))]
        instance.angles = [Angle(list(reversed((points + points)[i:i+3]))) for i in range(len(points))]
        return instance

    @staticmethod
    def translate_shape_points(points: list) -> list:
        '''Reorder points starting with the lexically first one, but preserving order otherwise
        For example [C, B, A] would be reordered as [A, C, B]
        '''
        point_labels = [p.label for p in points]
        lexical_first_loc = point_labels.index(min(point_labels))
        return points[lexical_first_loc:] + points[:lexical_first_loc]

class Triangle(Polygon):
    _registry_key = 'Triangle'
    def __new__(cls, points: list):
        '''Points must be ordered in a clockwise motion.
        '''
        assert len(points) == 3
        return super().__new__(cls, points)

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    A = Point('A')
    B = Point('B')
    C = Point('C')
    # s1 = Segment({A, B})
    # s2 = Segment({B, C})
    # s1.set_measure(SegmentMeasure())
    # s2.set_measure(SegmentMeasure())
    # s1.measure.set_equal_to(s2.measure)
    # print(s1.measure)
    # print(s2.measure)
    # print(s1.measure.measured_objects)
    T1 = Triangle([A, B, C])
    T2 = Triangle([B, C, A])
    print(T1.edges)
    print(T1.angles)
    try:
        T3 = Triangle([B, A, C])
    except:
        print('Inconsistent triangle')
    pp.pprint(Registry().entries)
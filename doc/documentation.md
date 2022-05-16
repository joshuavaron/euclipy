# Help on module 'euclipy.construct' in euclipy:

## NAME
### &nbsp;&nbsp;&nbsp;&nbsp; euclipy.construct

## CLASSES
```py
builtins.object
    Geometry
        Angle
        Point
        Segment
        Shape
            Polygon
                Triangle
    Measure
        AngleMeasure
        SegmentMeasure
    Registry
 ```
## METHODS
```py
    class Angle(Geometry)
     |  Angle(points: list)
     |
     |  Method resolution order:
     |      Angle
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, points: list)
     |      Points must be ordered such that the angle represents the clockwise motion from the first defined segment to the second defined segment.
     |      For example, if points = [A, B, C], then the angle is the clockwise motion from Segment(AB) to Segment(BC).
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Geometry:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class AngleMeasure(Measure)
     |  AngleMeasure(measure=None) -> None
     |
     |  Method resolution order:
     |      AngleMeasure
     |      Measure
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __init__(self, measure=None) -> None
     |      If measure is None, then the measure is not yet quantified.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Measure:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_equal_to(self, other_measure)
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Measure:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Geometry(builtins.object)
     |  Geometry(label)
     |
     |  Methods defined here:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |
     |  __new__(cls, label)
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Measure(builtins.object)
     |  Measure(measure=None) -> None
     |
     |  Methods defined here:
     |
     |  __init__(self, measure=None) -> None
     |      If measure is None, then the measure is not yet quantified.
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_equal_to(self, other_measure)
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Point(Geometry)
     |  Point(label)
     |
     |  Method resolution order:
     |      Point
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, label)
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Geometry:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Polygon(Shape)
     |  Polygon(points: list)
     |
     |  Method resolution order:
     |      Polygon
     |      Shape
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, points: list)
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  translate_shape_points(points: list) -> list
     |      Reorder points starting with the lexically first one, but preserving order otherwise
     |      For example [C, B, A] would be reordered as [A, C, B]
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Geometry:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Registry(builtins.object)
     |  Singleton registry of measures.
     |
     |  Methods defined here:
     |
     |  add_to_registry(self, entry)
     |
     |  get_auto_label(self, registry_key)
     |
     |  remove_from_registry(self, entry)
     |
     |  search_polygon(self, registry_key, points: list)
     |      Find polygon that shares points, regardless of point order
     |
     |  search_registry(self, registry_key, label)
     |
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |
     |  __new__(cls)
     |      entries is a dictionary with:
     |      - keys: _registry_key
     |      - values: dictionaries mapping entry labels to registered entries
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Segment(Geometry)
     |  Segment(endpoints: set)
     |
     |  Method resolution order:
     |      Segment
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, endpoints: set)
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Geometry:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class SegmentMeasure(Measure)
     |  SegmentMeasure(measure=None) -> None
     |
     |  Method resolution order:
     |      SegmentMeasure
     |      Measure
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __init__(self, measure=None) -> None
     |      If measure is None, then the measure is not yet quantified.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Measure:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_equal_to(self, other_measure)
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Measure:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Shape(Geometry)
     |  Shape(label)
     |
     |  Method resolution order:
     |      Shape
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, label)
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Geometry:
     |
     |  __dict__
     |      dictionary for instance variables (if defined)
     |
     |  __weakref__
     |      list of weak references to the object (if defined)

    class Triangle(Polygon)
     |  Triangle(points: list)
     |
     |  Method resolution order:
     |      Triangle
     |      Polygon
     |      Shape
     |      Geometry
     |      builtins.object
     |
     |  Static methods defined here:
     |
     |  __new__(cls, points: list)
     |      Points must be ordered in a clockwise motion.
     |
     |  ----------------------------------------------------------------------
     |  Static methods inherited from Polygon:
     |
     |  translate_shape_points(points: list) -> list
     |      Reorder points starting with the lexically first one, but preserving order otherwise
     |      For example [C, B, A] would be reordered as [A, C, B]
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from Geometry:
     |
     |  __repr__(self) -> str
     |      Return repr(self).
     |
     |  set_measure(self, measure: euclipy.construct.Measure) -> None
     |
```

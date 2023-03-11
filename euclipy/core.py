"""Base classes and core functionality of euclipy, a computational geometry
package for Python.

TODO: Provide longer description of euclipy

Typical usage example:

    TODO: Provide code example once euclipy can solve some non-trivial problems
"""

import collections
import functools
import itertools
import pprint

import sympy

from euclipy import exceptions

class RegisteredObject:
    """Base class for all euclipy objects that need to be tracked by the central
    registry.
    """
    # Instance methods for initializing/registering and deregistering objects

    def __init__(self, *_args, **_kwargs) -> None:
        """Add object to registry if not already registered
        """
        # __init__ will still be called after __new__ for subclasses that return
        # a previously-created object.  In that case, object should not be
        # initialized/registered again.
        if not hasattr(self, '_registered'):
            # If object lacks a key, use an automatically generated key instead
            if not hasattr(self, 'key'):
                self.key = self.auto_key()
            self.register()
            super().__init__()

    def register(self):
        """Add object to the registry.
        """
        self.get_registry()[self.key] = self
        self._registered = True

    def deregister(self, successor):
        """Remove object from the registry.
        """
        assert type(self) is type(successor)
        self.get_registry().pop(self.key)
        self.successor = successor
        successor.predecessor = self
        del self._registered

    # Class methods for class-level registries

    @classmethod
    def auto_key(cls):
        """Automatically generate an integer key for an object of cls
        
        Returns:
            Auto-incremented integer key for object, unique only among
            instances of the same class (not unique among subclasses)
        """

        if '_auto_key_counter' not in cls.__dict__:
            cls._auto_key_counter = 0
        cls._auto_key_counter += 1
        return cls._auto_key_counter

    @classmethod
    def get_registry(cls):
        """Obtain class-specific registry for cls
        """
        if '_registry' not in cls.__dict__:
            cls._registry = {}
        return cls._registry

    @classmethod
    def get(cls, key):
        """Obtain element from cls sub-registry by key
        """
        return cls.get_registry().get(key)

    @classmethod
    def elements(cls):
        """Iterator for all registered elements of cls (but not subclasses)
        """
        return cls.get_registry().values()

    @classmethod
    def elements_recursive(cls):
        """Iterator for all registered elements of cls and its subclasses
        """
        own = cls.elements()
        subs = (_.elements_recursive() for _ in cls.__subclasses__())
        return itertools.chain(own, itertools.chain.from_iterable(subs))

    @classmethod
    def reset_registry(cls):
        """Reset registry to empty dict
        """
        for _cls in cls.__subclasses__():
            _cls.reset_registry()
        if '_registry' in cls.__dict__:
            del cls._registry

    @classmethod
    def recursive_registry(cls):
        """Recursively traverse subclasses to create a dict view of the registry
        """
        def cls_reg(_cls):
            reg = _cls.get_registry().copy()
            for sub in _cls.__subclasses__():
                sub_reg = cls_reg(sub)
                if sub_reg:
                    reg[sub.__name__] = sub_reg
            return reg
        return {cls.__name__: cls_reg(cls)}

    @classmethod
    def print(cls): # pragma: no cover
        """Print registry using easy-to-read indentations
        """
        pprint.pprint(cls.recursive_registry())


class Expression(RegisteredObject):
    """Algebraic expressions and functionality to solve system of equations
    
    TODO: It is possible to insert two equivalent expressions into the registry.
    This can be avoided by prempting instantiation and testing for each
    registered non-zero expression e whether sympy.simplify(e.expr - expr) == 0
    """
    def __init__(self, expr, predecessor=None, substitutions=None) -> None:
        assert isinstance(expr, sympy.Expr)
        self.expr = expr
        if substitutions:
            assert isinstance(substitutions, dict)
        self.substitutions = substitutions
        if predecessor:
            predecessor.deregister(successor=self)
        else:
            self.predecessor = None
        super().__init__()

    def subs(self, replacements):
        """Make substitutions from replacements in expression (self.expr)
        
        Args:
            replacements: dict mapping sympy symbols to substitutions, e.g.,
                {x: 3, y: 5}
        
        Returns:
            If substitution does not change expression, returns self.
            If substitution changes expression, returns new Expression
            with attributes `replaced` and `substitutions`.
            
        Raises:
            SystemOfEquationsError if substitution evaluates to non-zero value
                without free symbols.
        """
        result = self.expr.subs(replacements, simultaneous=True)
        if result == self.expr:
            return self
        if result == 0 or len(result.free_symbols) > 0:
            return Expression(result, predecessor=self, substitutions=replacements)
        raise exceptions.SystemOfEquationsError('Expression without free \
            symbols cannot evaluate to a non-zero value.')

    def __repr__(self) -> str:
        if self.predecessor:
            rep = ', predecessor=' + repr(self.predecessor)
        else:
            rep = ''
        if self.substitutions:
            sub = ', substitutions=' + repr(self.substitutions)
        else:
            sub = ''
        return f'{self.__class__.__name__}({self.expr}{rep}{sub})'

    @classmethod
    def subs_all_expressions(cls, replacements:dict):
        """Make substitutions in replacements in all registered Expressions
        
        Args:
            replacements: dictionary mapping symbols to their replacements
        """
        # Iterate over list(cls.elements()), because loop changes cls._registry
        for expr in list(cls.elements()):
            expr.subs(replacements)

    @classmethod
    def solve_system(cls):
        """Solve expressions for positive values.
        Raise exception if any variable has a unique non-positive solution.
        Raise an exception if any variable with non-unique solutions has zero or
        more than one positive solutions."""

        # Find valid solutions to the system of equuations, if any
        unsolved = [e for e in cls.elements() if e.expr != 0]
        solutions = sympy.solve([e.expr for e in unsolved], dict=True)
        uniques = set.intersection(*[set(sol.items()) for sol in solutions])
        non_uniques = [set(sol.items()) - uniques for sol in solutions]
        uniques = dict(uniques)
        # Create list of dicts with common keys
        non_uniques = [dict(non_unique) for non_unique in non_uniques]
        uniques_without_free_symbols = {k:v for k, v in uniques.items()
                                        if not v.free_symbols}
        # TODO: if v is a free symbol itself, i.e. isinstance(v, sympy.Symbol),
        # then there is probably value in substituting that as well, because the
        # substitution would reduce the number of free symbols in the system
        # and establish measure equalities (i.e. measures represented by the
        # same symbol)
        if not all(e > 0 for e in uniques_without_free_symbols.values()):
            # TODO: If a feature to define new variables as functions of measure
            # symbols is implemented in the future, the following >0 constraint
            # should only be applied to symbols that represent measures.
            raise exceptions.SystemOfEquationsError('All unique solutions \
                must be positive because they represent measures.')
        non_uniques_without_free_symbols = [{k:v for k, v in sol.items()
                                             if not v.free_symbols}
                                            for sol in non_uniques]
        solution_sets = collections.defaultdict(set)
        for non_unique_sol in non_uniques_without_free_symbols:
            for key, val in non_unique_sol.items():
                solution_sets[key].add(val)
        non_uniques_solution_candidate = {k: {e for e in v if e > 0}
                                          for k, v in solution_sets.items()}
        if not all(len(v) == 1 for v in non_uniques_solution_candidate.values()):
            raise exceptions.SystemOfEquationsError('Non-unique solutions \
                must contain exactly one positive solution for each variable.')
        non_uniques_solution = {k: v.pop() for k, v
                                in non_uniques_solution_candidate.items()}
        valid_solutions = uniques_without_free_symbols | non_uniques_solution

        # Substitute valid_solutions for variables in expressions
        for expr in unsolved:
            expr = expr.subs(valid_solutions)
        for sym, val in valid_solutions.items():
            MeasurableGeometricObject.substitute_measure_symbol(sym, val)


class GeometricObject (RegisteredObject):
    """Base class for all geometric objects
    """


class MeasurableGeometricObject(GeometricObject):
    """Base class for all geometric objects that can be measured
    """
    def __init__(self, *_args, **_kwargs):
        if not hasattr(self, '_measure'):
            self._measure = None
        super().__init__()

    @classmethod
    def auto_measure_symbol(cls):
        """Automatically generate a measure variable symbol
        """
        if '_auto_measure_symbol_counter' not in cls.__dict__:
            cls._auto_measure_symbol_counter = 0
        cls._auto_measure_symbol_counter += 1
        label = f'm{cls.__name__}{cls._auto_measure_symbol_counter}'
        return sympy.Symbol(label)

    @staticmethod
    def measure_symbol_to_object_map():
        """Dictionary mapping measure symbols to a list of corresponding objects
        """
        sym_map = collections.defaultdict(list)
        for obj in MeasurableGeometricObject.elements_recursive():
            if obj.has_measure_symbol:
                sym_map[obj.measure].append(obj)
        return sym_map

    @staticmethod
    def substitute_measure_symbol(old_sym, new_sym_or_val):
        """Substitute solved symbol in all MeasurableGeometricObject measures
        """
        sym_obj_map = MeasurableGeometricObject.measure_symbol_to_object_map()
        for obj in sym_obj_map.get(old_sym, []):
            obj.set_measure(new_sym_or_val)

    @property
    def has_measure(self):
        """Boolean property of measurable objects; True if measure exists
        """
        return self._measure is not None

    @property
    def has_measure_symbol(self):
        """Boolean property of measurable objects; True if measure is a symbol
        """
        return self.has_measure and isinstance(self.measure, sympy.Symbol)

    def set_measure(self, measure=None):
        """Set the measure for object without performing any of the other
        actions that @measure.setter performs. Generally intended for
        class-internal use.
        """
        if measure is None:
            self._measure = self.auto_measure_symbol()
        else:
            isinstance(measure, (sympy.Symbol, sympy.Number))
            self._measure = measure

    @property
    def measure(self):
        """Getter property of measurable objects; creates measure if needed
        """
        if not self.has_measure:
            self.set_measure()
        return self._measure

    @measure.setter
    def measure(self, new):
        '''
        new can be one of the following:
        - a number (instance of numbers.Numbers)
        - a sympy number (instnace of sympy.Number)
        - a sympy symbol (instance of sympy.Symbol)
        '''
        try:
            new = sympy.sympify(new)
        except sympy.SympifyError as exc:
            raise ValueError(f'Cannot set measure to {new}.') from exc

        if self.has_measure:
            old = self._measure
            if isinstance(old, sympy.Symbol):
                self.substitute_measure_symbol(old, new)
                Expression.subs_all_expressions({old: new})
            elif isinstance(old, sympy.Number):
                if isinstance(new, sympy.Symbol):
                    self.substitute_measure_symbol(new, old)
                    Expression.subs_all_expressions({new: old})
                elif isinstance(new, sympy.Number):
                    if new != old:
                        raise ValueError(f'Cannot set measure to {new}, \
                            because it is already set to {old}.')
            else:
                raise TypeError(f'Cannot set measure to {new}.')
        else:
            self.set_measure(new)


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
        return cls.__construct(label)

    @classmethod
    def __construct(cls, label: str):
        """Create new Point instance
        
        Args:
            label: non-empty string not containing spaces
            
        Raises:
            ValueError if label is empty or contains spaces
        """
        if label == '':
            raise ValueError('Empty string is not a valid Point label.')
        if ' ' in label:
            raise ValueError('Spaces are not permitted in Point labels.')
        obj = super().__new__(cls)
        obj.key = label
        obj._pred = set()
        obj._op = Point.__construct
        return obj

    def __lt__(self, obj):
        return self.key < obj.key

    def __eq__(self, obj):
        return self.key == obj.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self) -> str:
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
        reg_common_pts = [obj for obj in cls.elements()
                          if len(set(obj.points).intersection(set(pts))) > 1]
        if reg_common_pts:
            for registered in reg_common_pts:
                pts = cls.bidirectional_order_preserving_merge(registered.points, pts)
            pts = cls.canonical_ordering(pts)
            retain = reg_common_pts[0]
            if pts == retain.points:
                return retain
            # Some points have been merged from one or more existing lines from the registry
            remove = reg_common_pts[1:]
            retain.points = pts
            for obj in remove:
                obj.deregister()
            return retain
        # No existing line has two or more points in common with the new line;
        # create a new line instance
        obj = super().__new__(cls)
        obj.points = cls.canonical_ordering(pts)
        return obj

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({" ".join([p.key for p in self.points])})'

    @staticmethod
    def canonical_ordering(pts):
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
        if len(common_ordered_as_s_a) < 2:
            raise exceptions.ColinearPointSequenceError(
                'Sequences have fewer than two points in common.', s_a, s_b)
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


class Segment(MeasurableGeometricObject):
    """A segment represented by its two endpoints on the Euclidean plane
    """
    def __new__(cls, pts):
        '''Argument endpoints is one of the following:
        - a space separated pair of point labels representing a segment, e.g. 'B A'
        - a tuple of two Point objects'''
        pts = points(pts)
        if not (isinstance(pts, tuple) and len(pts) == 2):
            raise ValueError('Instantiating a Segment requires exactly 2 points.')
        # Determine canonical ordering of points (lexical for Segments)
        ordered_pts = tuple(sorted(pts))
        # Construct key based on canonically ordered points
        canonical_key = ' '.join([p.key for p in ordered_pts])
        # If Segment with canonical_key is already registered, return it
        registered = cls.get(canonical_key)
        if registered:
            return registered
        return cls.__construct(canonical_key, ordered_pts)

    @classmethod
    def __construct(cls, key, ordered_pts):
        obj = super().__new__(cls)
        obj.points = ordered_pts
        obj.key = key
        obj._pred = set(ordered_pts)
        obj._op = Segment.__construct
        return obj

    def __repr__(self) -> str:
        measure = ', measure=' + repr(self.measure) if self.has_measure else ''
        return f'{self.__class__.__name__}({self.key}{measure})'

    @property
    def line(self):
        """Returns the Line that segment lies on
        """
        return Line(self.points)

    def atomic_subsegments(self):
        """Returns a list of all atomic subsegments of the segment
        
        Atomic subsegments are subsegments that do not contain other subsegments
        of the segment.
        """
        line_pts = self.line.points
        pt_l, pt_r = self.points
        idx_l, idx_r = line_pts.index(pt_l), line_pts.index(pt_r)
        seg_pts = line_pts[idx_l:idx_r+1]
        return [Segment((seg_pts[i], seg_pts[i+1]))
                for i in range(len(seg_pts)-1)]


if __name__ == '__main__':
    pass

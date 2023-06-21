"""Base classes and core functionality of euclipy, a computational geometry
package for Python.

TODO: Provide longer description of euclipy

Typical usage example:

    TODO: Provide code example once euclipy can solve some non-trivial problems
"""

import collections
import itertools
import pprint

import sympy

from euclipy import exceptions

class RegisteredObject:
    """Base class for all euclipy objects that need to be tracked by the central
    registry.
    """
    # Instance methods for initializing/registering and deregistering objects
    def __new__(cls) -> None:
        obj = super().__new__(cls)
        obj._successor = None
        return obj

    def __init__(self, *_args, **_kwargs) -> None:
        """Add object to registry if not already registered
        """
        # __init__ will still be called after __new__ for subclasses that return
        # a previously-created object.  In that case, object should not be
        # initialized/registered again.
        if not hasattr(self, '_registered'):
            self._successor = None
            # If object lacks a key, use an automatically generated key instead
            if not hasattr(self, '_key'):
                self.key = self.auto_key()
            self.register()
            self._callbacks = []
            super().__init__()

    def __getattribute__(self, name):
        successor = object.__getattribute__(self, '_successor')
        if successor and name != '_successor' and name != '_predecessor':
            return getattr(successor, name)
        return object.__getattribute__(self, name)

    @property
    def _identifier(self): #pragma: no cover
        raise NotImplementedError

    @property
    def key(self):
        """Key for object in registry
        """
        return self._key

    @key.setter
    def key(self, value):
        """Set key for object in registry
        """
        check_registry = hasattr(self, '_key')
        self._key = value
        if check_registry: # pragma: no cover TODO: Remove this line once implemented
            for obj in self.elements():
                # TODO: Need to find objects with same obj.key but different key in the registry
                # TODO: Merging of objects need to fire callbacks to replace all
                    # references to deregistered objects with surviving object
                pass

    def register(self):
        """Add object to the registry.
        """
        self.get_registry()[self.key] = self
        self._registered = True

    def update_key(self, new_key):
        """Update key for object in registry
        """
        if self.key != new_key:
            obj_with_new_key = self.get_registry().get(new_key)
            if obj_with_new_key:
                self.replace(obj_with_new_key)
            else:
                self.get_registry().pop(self.key)
                self.key = new_key
                self.register()
                self.broadcast_change(None)

    def broadcast_change(self, successor):
        for callback in self._callbacks:
            callback(self, successor)
            if successor:
                successor.call_when_changed(callback)

    def replace(self, successor):
        assert type(self) is type(successor)
        # Broadcast replacement to all callbacks
        self.broadcast_change(successor)
        # Set successor and deregister self
        self.get_registry().pop(self.key)
        successor._predecessor = self
        del self._registered
        self._successor = successor
        # TODO: Should also clean up registry

    def call_when_changed(self, callback):
        self._callbacks.append(callback)

    # Class methods for class-level registries

    @classmethod
    def auto_key(cls):
        """Automatically generate an integer key for an object of cls
        
        Returns:
            Auto-incremented integer key for object, unique only among
            instances of the same class (not unique among subclasses)
        """
        # TODO: There may not be users of auto_key left.  Consider removing
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
    def remove_duplicates(cls):
        sig_obj_map = collections.defaultdict(list)
        for obj in cls.elements():
            sig_obj_map[obj._identifier].append(obj)
        dup_objs_list = [objlist for objlist in sig_obj_map.values() if len(objlist) > 1]
        if len(dup_objs_list) > 0:
            assert len(dup_objs_list) == 1
            dup_objs = dup_objs_list[0]
            retain = dup_objs[0]
            for obj in dup_objs[1:]:
                if issubclass(type(obj), MeasurableGeometricObject):
                    obj.measure = retain.measure
                obj.replace(retain)
            retain.broadcast_change(None)
            return retain

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
    def __new__(cls, expr, predecessor=None, substitutions=None) -> None:
        del expr, predecessor, substitutions
        return super().__new__(cls)

    def __init__(self, expr, predecessor=None, substitutions=None) -> None:
        assert isinstance(expr, sympy.Expr)
        self.expr = expr
        if substitutions:
            assert isinstance(substitutions, dict)
        self.substitutions = substitutions
        if predecessor:
            predecessor.replace(successor=self)
        else:
            self._predecessor = None
        super().__init__()

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    @property
    def _identifier(self):
        return self.expr

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

    def __repr__(self) -> str: # pragma: no cover
        if self._predecessor:
            rep = ', predecessor=' + repr(self._predecessor)
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

        Returns:
            - dict mapping symbols to values of solutions
            - empty dict if no unsolved expressions exist
            - empty dict system cannot yet be solved but there are no inconsistencies
        Raises: SystemOfEquationsError if
            - any variable has a unique non-positive solution.
            - any variable with non-unique solutions has zero or more than one positive solutions.
            - the system cannot have any solutions
        """

        # Find valid solutions to the system of equuations, if any
        unsolved = [e for e in cls.elements() if e.expr != 0]
        if not unsolved:
            return {}
        solutions = sympy.solve([e.expr for e in unsolved], dict=True)
        if not solutions:
            raise exceptions.SystemOfEquationsError('Unsolved expressions with no solution.')
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
        return valid_solutions


class GeometricObject(RegisteredObject):
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
            if isinstance(measure, (sympy.Symbol, sympy.Number)):
                self._measure = measure
            else:
                raise ValueError(f'Cannot set measure to {measure}.')

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
        #TODO: Add support for different numeric types
        try:
            new = sympy.sympify(new)
        except sympy.SympifyError as exc:
            raise ValueError(f'Cannot set measure to {new}.') from exc
        if not isinstance(new, (sympy.Symbol, sympy.Number)):
            raise ValueError(f'Cannot set measure to {new}.')

        if self.has_measure:
            old = self._measure
            if isinstance(old, sympy.Symbol):
                self.substitute_measure_symbol(old, new)
                Expression.subs_all_expressions({old: new})
            else: # old is a sympy.Number
                if isinstance(new, sympy.Symbol):
                    self.substitute_measure_symbol(new, old)
                    Expression.subs_all_expressions({new: old})
                elif isinstance(new, sympy.Number):
                    if new != old:
                        raise ValueError(f'Cannot set measure to {new}, \
                            because it is already set to {old}.')
        else:
            self.set_measure(new)

    def __repr__(self) -> str: # pragma: no cover
        measure = ', measure=' + repr(self.measure) if self.has_measure else ''
        return f'{self.__class__.__name__}({self.key}{measure})'

if __name__ == '__main__':
    pass

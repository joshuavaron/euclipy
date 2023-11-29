"""Exceptions used by euclipy classes
"""
class ColinearPointSequenceError(Exception):
    """Errors with merging/aligning two colinear point sequences
    
    Raised by the Line class when two lines with two or more common points
    cannot be consistently or unambiguously merged.
    """
    def __init__(self, message, seq1, seq2):
        self.message = message
        self.seq1 = seq1
        self.seq2 = seq2

    def __str__(self): # pragma: no cover
        return f'{self.message} {self.seq1}  {self.seq2}'

class SystemOfEquationsError(Exception):
    """Inconsistent system of equations with no solutions
    """
    def __init__(self, description):
        self.description = description

    def __str__(self): # pragma: no cover
        return f'{self.description}'

class SubstitutionIntoUnregisteredExpression(Exception):
    """Attempt to substitute into an expression no longer in the registry
    """
    def __init__(self, expr):
        self.expr = expr

    def __str__(self): # pragma: no cover
        return f'{self.expr}'

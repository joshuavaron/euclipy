
# Euclipy

  

[![PyPI version](https://img.shields.io/pypi/v/euclipy.svg?color=dodgerblue&label=%20latest%20version)](https://pypi.org/project/euclipy/)

[![PyPI downloads](https://img.shields.io/pypi/dm/euclipy.svg?color=limegreen&label=PyPI%20downloads)](https://pypi.org/project/euclipy/)

  

### A library used to create, model, and solve figures in Euclidean Geometry.

## Features:

  

- Create symbolic geometric objects (Triangle(), Segment(), Point(), etc.)

- Implicitly defines segments created by constructions

  

## Installation

```sh

# PyPi Installation

pip install euclipy

```

## Sample Code (With Comments):

```py

from euclipy.core import Line, Segment, Expression

import euclipy.theorems as theorems

  

if  __name__ == '__main__':
    # Construct a line with colinear points: A, B, C, D, E
    line = Line('A B C D E')

    # Define the lengths of line segments lying on line AE
    Segment('A C').measure = 5
    Segment('C E').measure = 12
    Segment('B E').measure = 15
    
    # Apply the relevant theorem which creates expressions about the sums of
    # contiguous subsegments of line segments
    theorems.theorem_subsegment_sum(line)

    # Solve the system of equations resresented by all of the expressions
    # created by theorems
    Expression.solve_system()

    # Verify one of the solutions found
    print(f"Segment('A B').measure = {Segment('A B').measure}") # 2

```

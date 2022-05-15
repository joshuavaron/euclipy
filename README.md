# Euclipy

[![PyPI version](https://img.shields.io/pypi/v/euclipy.svg?color=dodgerblue&label=%20latest%20version)](https://pypi.org/project/euclipy/)
[![PyPI downloads](https://img.shields.io/pypi/dm/euclipy.svg?color=limegreen&label=PyPI%20downloads)](https://pypi.org/project/euclipy/)

### A library used to create, model, and solve figures in Euclidean Geometry.
## Features:

- Create points, line segments, angles, and triangles with Point(), Segment(), Angle(), and Triangle(), respectively
- Implicitly defines segments and angles created by polygon constructions
- Keeps a registry of all defined objects, implicit or explicit

## PyPi Installation
```sh
# PyPi Installation
pip install euclipy
```
## Sample Code (With Comments):
```py
from euclipy import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Create 3 unique points
A = Point('A')
B = Point('B')
C = Point('C')

# Create identical triangles
T1 = Triangle([A, B, C])
T2 = Triangle([B, C, A])

print(T1.edges)    # Prints line segments created by T1
print(T1.angles)    # Prints angles created by T1

# Tries to create inconsistent triangle
try:
    T3 = Triangle([B, A, C])
except:
    print('Inconsistent triangle')
    
# Prints all created objects
pp.pprint(Registry().entries)
```

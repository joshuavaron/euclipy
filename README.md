
# Euclipy

  

[![PyPI version](https://img.shields.io/pypi/v/euclipy.svg?color=dodgerblue&label=%20latest%20version)](https://pypi.org/project/euclipy/)

[![PyPI downloads](https://img.shields.io/pypi/dm/euclipy.svg?color=limegreen&label=PyPI%20downloads)](https://pypi.org/project/euclipy/)

  

### A library used to create, model, and solve figures in Euclidean Geometry.

## Features:

  

- Create symbolic geometric objects (Triangle(), Segment(), Point(), etc.)

- Gathers implicit information created by previous constructions

- Solves for unknown measures and expressions

## solve():

  

- Use the solve() function to solve for unknown measures and expressions

- Choose which metric you would like to solve for (measure, area, a ratio, etc.)
  

## Installation

```sh

# PyPi Installation

pip install euclipy

```

## Sample Code (With Comments):

```py
# Note: This is an implementation of Problem 17 from the 2016 AMC 12B Competition
from euclipy.polygon import Triangle
from euclipy.geometricobjects import Angle, Line, Segment

if  __name__ == '__main__':
    # Create a triangle
    Triangle('A C B')

    # Define lines within the triangle
    Line('A P Q H')
    Line('C P E')
    Line('B Q D')
    Line('A E B')
    Line('B H C')
    Line('C D A')
    
    # Define triangle edge measures
    Segment('A C').measure = 9
    Segment('C B').measure = 8
    Segment('A B').measure = 7
    
    # Create an altitude of Triangle(ACB)
    Angle('C H A').measure = 90
    
    # Create angle bisectors in Triangle(ACB)
    Angle('C B D').measure = Angle('D B A').measure
    Angle('E C B').measure = Angle('A C E').measure
    
    # Solve for and print the measure of Segment(PQ)
    print(Segment('P Q').solve())
```
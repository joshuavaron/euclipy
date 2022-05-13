# Define value placeholders
undefined = "undefined"
alpha = (u"\u03b1")
beta = (u"\u03b2")
phi = (u"\u03c6")

construction=[]

# Function creates a triangle (Vertices, angles, side lengths)
def triangle(point_1="a", point_2="b", point_3="c", angle_a=alpha, angle_b=beta, angle_c=phi, side_a=undefined, side_b=undefined, side_c=undefined, construction=construction):
    # Adds data to construction list if all datatypes are correct
    construction.append(["triangle", point_1, point_2, point_3, angle_a, side_b, angle_c, side_a, angle_b, side_c]) if isinstance(point_1, str) and isinstance(point_1, str) and isinstance(point_3, str) else exec("raise RuntimeError('An error occurred: input error')")

def solve(construction=construction):
    for figure in construction:
        if figure[0] == "triangle":
            figureInf = figure[4:10]
            for index, element in enumerate(figureInf): figureInf[index] = 1 if isinstance(figureInf[index], (int, float)) else 0
            # If 2 angles are known, solve for 3rd angle
            if sum(figureInf[slice(0, 5, 2)]) == 2:
                angles = figureInf[slice(0, 5, 2)]
                for index, angle in enumerate(angles): angles[index] = figure[(index*2)+4] if angles[index] == 1 else 0
                index = angles.index(0)
                angles.pop(index)
                figure[(index*2)+4] = 180 - sum(angles)
        else:
            pass
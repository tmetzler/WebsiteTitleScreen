
#It took me 8 hours to make this...

import pyxel
import numpy as np
import os
import math
import cmath
from xml.dom import minidom
from svg.path import parse_path

numvector = 200
svg_file = r'pikachu.svg'
spinrate = 0.0003 # rate of spin
scale = 30 #scale of drawing from 0, 0
num_points = 1000  # Number of samples of the svg path

def precompute_f(svg_file_path, num_points):
    doc = minidom.parse(svg_file_path)
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    doc.unlink()

    all_coordinates = []

    for path_string in path_strings:
        path = parse_path(path_string)
        for path_t in np.linspace(0, 1, num_points):
            try:
                point = path.point(path_t)
                all_coordinates.append(point.real + point.imag * 1j)
            except:
                print("There's a problem in the points!")
                continue  # Skip any problematic points

    return all_coordinates
full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), svg_file)

print(f"Attempting to open file: {full_path}")

# Precompute all f values
f_values = precompute_f(full_path, num_points)

def f(t):
    index = int(t * (len(f_values) - 1))
    return f_values[index]

# Pyxel setup and drawing code

global dot
dot = 0

def update():
    global dot

    dot += 1
    
    
    for vector in currentvectors:
        #gets polar coordinates for the vector
        vector[3] = math.atan2(vector[1], vector[0])
        vector[4] = math.sqrt(vector[1] ** 2 + vector[0] ** 2)

        #adds the spin to theta
        vector[3] += vector[2] * spinrate

        #converts vector back to cartesian coordinates
        vector[0] = math.cos(vector[3])*vector[4]
        vector[1] = math.sin(vector[3])*vector[4]

def draw():
    pyxel.cls(0)
    
    #takes all the vectors and makes a sum to see where they end up
    penposx = sum(vector[0] for vector in currentvectors)
    penposy = sum(vector[1] for vector in currentvectors)

    #pyxel.rect(f(dot/num_points).real*scale, f(dot/num_points).imag*scale, 1, 1, 5)
    circs.append((penposx*scale, penposy*scale, 3, 6))
    for circ in circs:
        pyxel.circ(circ[0], circ[1], circ[2], circ[3])
    

    vectorcount = 0

    points= []
    prevsum = [0, 0]

    currentvectors.sort(key=lambda x: x[4])
    currentvectors.reverse()

    for vector in currentvectors:
        prevsum[0] += vector[0]
        prevsum[1] += vector[1]

        points.append((prevsum[0], prevsum[1]))

        
    
    for number in range(len(currentvectors)):
        if number+1 < len(points):
            pyxel.line(points[number][0]*scale, points[number][1]*scale, points[number+1][0]*scale, points[number+1][1]*scale, 10)
            pyxel.circb(points[number][0]*scale, points[number][1]*scale, currentvectors[number+1][4]*scale, 5)
        
        pyxel.line(0, 0, currentvectors[0][0]*scale, currentvectors[0][1]*scale, 10)
        pyxel.circb(0, 0, currentvectors[0][4]*scale, 5)
 


def add_lists(listoflists): 
    listtotal = [0, 0]
    for list in listoflists:
        listtotal[0] += list[0]
        listtotal[1] += list[1]
    return listtotal

def calculate_Cn(n):
    dt = 1 / num_points
    integral_sum = sum(f(t * dt) * cmath.exp(-n * 2 * cmath.pi * 1j * t * dt) * dt for t in range(num_points))
    return integral_sum

absolutevectornum = (numvector-1)/2
coefs = []

#get the coefficient for all vectors
for vector in range(int(-absolutevectornum), int(absolutevectornum+1)):
    coef = calculate_Cn(vector)
    coefs.append([coef.real, coef.imag, vector, None, None])

currentvectors = coefs
circs = []


pyxel.init(2000, 1000, title="DotTest", fps=480)
pyxel.camera(-1000, -500)
while dot < num_points:
    pyxel.run(update, draw)
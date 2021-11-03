import shapefile
import numpy as np
import matplotlib
import pandas as pd
import simpledbf 
from simpledbf import Dbf5
import util
from util import plotPolygons
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
import matplotlib as mpl

'''
The functions in this file can be used for working through the data of a single fire.

'''


def initialize_grid_representation(xRange, yRange, xDiff, yDiff):
    '''
    Creates a grid representation for a single of a fire. It discretizes each fire square into sizes of (xDiff by yDiff)
    
    If your xRange was (0,10), yRange was (0,20), and xDiff, yDiff = 5,5, then this function will return a 2x4 grid 
    
    Input:
    xRange --> Tuple with minimum latitude and maximum latitude
    yRange -->Tuple with minimum longitude and maximum longitude
    xDiff --> Smallest witnessed distance for an x edge of a vertex of a fire polygon (defines the smallest "unit fire" our wildfire data has)
    yDiff --> Smallest witnessed distance for a y edge of a vertex of a fire polygon (defines the smallest "unit fire" our wildfire data has)
    Output: Returns numpy array of zeros after discretization
    '''
    lonSquares = (xRange[1] - xRange[0])/xDiff
    latSquares = (yRange[1] - yRange[0])/yDiff
    return np.zeros((int(lonSquares), int(latSquares)))


def get_fire_shape_and_discretization(final_fire_indices):
    '''
    From the final_fire_indices (you can find this from the polygon points of the "FinalArea" of a fire in the .dbf files), you can 
    get a bounding box to create a gridlike representation of the fire, with each cell being a "unit fire". 
    
    This function just returns the information to create that bounding box
    
    Input: final_fire_indices --> List of tuples of polygon edges
    Output: 
     xRange --> Tuple with minimum latitude and maximum latitude
    yRange -->Tuple with minimum longitude and maximum longitude
    xDiff --> Smallest witnessed distance for an x edge of a vertex of a fire polygon (defines the smallest "unit fire" our wildfire data has)
    yDiff --> Smallest witnessed distance for a y edge of a vertex of a fire polygon (defines the smallest "unit fire" our wildfire data has)
    '''
    
    x_min = float('inf')
    x_max = float('-inf')
    y_min = float('inf')
    y_max = float('-inf')
    for fire in final_fire_indices:
        if fire[0] < x_min:
            x_min = fire[0]
        if fire[1] < y_min:
            y_min = fire[1]
        if fire[0] > x_max:
            x_max = fire[0]
        if fire[1] > y_max:
            y_max = fire[1]

    x_sorted = np.sort([fire[0] for fire in final_fire_indices])
    y_sorted = np.sort([fire[1] for fire in final_fire_indices])
    xdiff = [np.abs(np.subtract(x_sorted[i], x_sorted[i+1])) for i in range(len(x_sorted) - 1)]
    ydiff = [np.abs(np.subtract(y_sorted[i], y_sorted[i+1])) for i in range(len(y_sorted) - 1)]
    xdifflist = np.nonzero(xdiff)[0].astype(int)
    ydifflist = np.nonzero(ydiff)[0].astype(int)
    x_diff = np.min(np.take(xdiff, xdifflist, axis = 0))
    y_diff = np.min(np.take(ydiff, ydifflist, axis = 0))
    #print("X Range: ", (x_min, x_max), "\nY Range: ", (y_min, y_max))
    #print("X Diff: ", x_diff, "\nY Diff: ", y_diff)
    return (x_min, x_max), (y_min, y_max), x_diff, y_diff

def multi_day_fire_initialization(final_fire_indices, number_of_days):
    '''
    Represent a multiple day fire by adding an extra dimension for days to your fire represesentation.
    
    Input: final_fire_indices --> tuple of final polygon
           number_of_days --> number of days the fire lasted for
    '''
    xRange, yRange, xDiff, yDiff = get_fire_shape_and_discretization(final_fire_indices)
    fireGrid = initialize_grid_representation(xRange, yRange, xDiff, yDiff).shape
    lonSquares = fireGrid[0]
    latSquares = fireGrid[1]
    return np.zeros((number_of_days, lonSquares, latSquares))
   
def multi_day_fire_representation(shape_records, sorted_df, final_fire_indices):
    
    '''
    Fills in the representation of a multi-day fire. Every 1 in the dataset represents an actively burning area on that day.
    
    Every 0 in the dataset represents that it is not currently burning
    
    Outputs: multiDayFire --> 3D array that stores information of "unit fires" on each data
    For example multiDayFire[4][3][15] represents whether the "unit fire" on Day 5 (4 + 1) has an active burn at latitude index
    3 and longitude index 15. You could covert 3 and 15 back to longitudes and latitudes using get_fire_shape_and_discretization(final_fire_indices):
    
    '''
 
    multiDayFireGrid = multi_day_fire_initialization(final_fire_indices, sorted_df.IDate.nunique())
    xRange, yRange, xDiff, yDiff = get_fire_shape_and_discretization(final_fire_indices)
    lastFDate = None
    k = -1
    for row in sorted_df.iterrows():
        shape_record = shape_records[row[0]]
        fire_polygon_indices = np.array([shape_record.shape.points])
        polygon = Polygon(fire_polygon_indices[0])
        x_coordinates = np.arange(xRange[0], xRange[1], xDiff)
        y_coordinates = np.arange(yRange[0], yRange[1], yDiff)
        if row[1]['IDate'] != lastFDate:     
            k += 1
            lastFDate = row[1]['IDate']
        path = polygon.get_path()

        for i in range(len(x_coordinates)):
            x = x_coordinates[i]
            for j in range(len(y_coordinates)):
                y = y_coordinates[j]
                point = (x, y)
                if path.contains_point(point, radius = -xDiff):
                    multiDayFireGrid[k][i][j] = 1
    return multiDayFireGrid

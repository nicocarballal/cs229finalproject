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
import itertools
from matplotlib import pyplot

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
    lonSquares = (xRange[1] - xRange[0])/xDiff + 1
    latSquares = (yRange[1] - yRange[0])/yDiff + 1
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
    x_coordinates = np.arange(xRange[0], xRange[1], xDiff)
    y_coordinates = np.arange(yRange[0], yRange[1], yDiff)
    lastFDate = None
    k = -1
    day_fire_paths = []
    for row in sorted_df.iterrows():
        shape_record = shape_records[row[0]]
        fire_polygon_indices = np.array([shape_record.shape.points])
        polygon = Polygon(fire_polygon_indices[0])
        new_path = polygon.get_path()
        if row[1]['Type'] == 'FinalArea':
            continue
        elif k == -1:
            k = 0
            lastFDate = row[1]['IDate']
            day_fire_paths = [new_path]
            continue
        elif row[1]['IDate'] != lastFDate:     
            k += 1
            lastFDate = row[1]['IDate']
        else: 
            day_fire_paths.append(new_path)
            continue

        # Should I only iterate over possible x_coordinates for a single day of fire? Could speed things up drastically
        all_Vertices = np.array([[np.min(day_fire_paths[i].vertices,axis=0), np.max(day_fire_paths[i].vertices,axis=0)] for i in range(len(day_fire_paths))])
        #min_Range = np.min(all_Vertices, axis = 0)
        #max_Range = np.max(all_Vertices, axis = 0)

        to_check = set()

        for vertex in all_Vertices:
            min_Range = (vertex[0][0], vertex[0][1])
            max_Range = (vertex[1][0], vertex[1][1])

            x_indices = (round((min_Range[0] - xRange[0])/xDiff), round((max_Range[0] - xRange[0])/xDiff))
            y_indices = (round((min_Range[1] - yRange[0])/yDiff), round((max_Range[1] - yRange[0])/yDiff))
            
            x_indices = (int(x_indices[0]), int(x_indices[1]))
            y_indices = (int(y_indices[0]), int(y_indices[1]))

            a = itertools.product(list(range(max(x_indices[0] - 1, 0), min(x_indices[1] + 1, len(x_coordinates)))), list(range(max(y_indices[0] - 1, 0), min(y_indices[1] + 1, len(y_coordinates)))))
            '''
            check_x_indices = check_x_indices.union(list(range(max(x_indices[0] - 1, 0), min(x_indices[1] + 1, len(x_coordinates)))))
            check_y_indices = check_y_indices.union(list(range(max(y_indices[0] - 1, 0), min(y_indices[1] + 1, len(y_coordinates)))))
            '''
            to_check = to_check.union(a)



        for block in to_check:
            i = block[0]
            j = block[1]
            x = x_coordinates[i]
            y = y_coordinates[j]
            point = (x, y)
            for path in day_fire_paths:
                if path.contains_point(point, radius = 0): ## look into how to set radius
                    multiDayFireGrid[k][i][j] = 1
                
                    break
        day_fire_paths = [new_path]
    return multiDayFireGrid

def plot_multi_day_fire_from_npy(month_, year_, ID_, custom_path = "./../data/United_States_Fires/United_States_{year}_Fires/{month}/multi_day/{ID}.npy", month_shape = None):
    '''
    For a specific fire ID from a given month and year, plot from the .npy representation
    
    Inputs:
    month --> String of type 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec
    year --> string of type '2019', '2018', etc.
    ID_ --> string with fire ID (e.g. '20034923')
    custom_path --> string with your custom path to the .npy file
    
    Outputs:
    Plots for the multiple day representation of a fire
    
    '''
    # Read in our shapefile for month and year
    if month_shape is None:
        month_shape = np.load(custom_path.format(month = month_, year = year_, ID = ID_))

    # make a color map of fixed colors
    cmap = mpl.colors.ListedColormap(['green', [.5, .1, .1], 'red'])
    bounds=[-.1, 0.2, .8, 1.1]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    # tell imshow about color map so that only set colors are used
    prev_shapes = np.zeros(month_shape[0].shape)
    for i in range(0, len(month_shape)):
        day_plot = np.zeros(month_shape[i].shape)
        for j in range(len(day_plot)):
            for k in range(len(day_plot[j])):
                if month_shape[i][j][k] == 1:
                    day_plot[j][k] = 1
                elif prev_shapes[j][k] > 0:
                    day_plot[j][k] = prev_shapes[j][k]


        img = pyplot.imshow(day_plot,interpolation='nearest',
                        cmap = cmap,norm=norm)
            # make a color bar
        pyplot.colorbar(img,cmap=cmap,
                        norm=norm,boundaries=bounds,ticks=[0,1])
        legend_elements = [Line2D([0], [0], marker = 'o', color = 'w', markerfacecolor=[.5, .1, .1], markersize = 15,
                              label='Previous Burn'),
                   Line2D([0], [0], marker='o', color='w', label='Active Burn',
                          markerfacecolor='r', markersize=15),
                   Line2D([0], [0], marker='o', color='w', label='Unburned Area',
                          markerfacecolor='g', markersize=15)]
        pyplot.xlabel("Longitude Unit Fire Cells")
        pyplot.ylabel("Latitude Unit Fire Cells")
        fig, ax = plt.subplots()
        ax.legend(handles=legend_elements, loc='center')
        pyplot.show()
        prev_shapes = 0.5 * np.bitwise_or(prev_shapes > 0, month_shape[i] > 0)

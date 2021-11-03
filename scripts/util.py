## Importing shapefile to read the shapefile files
import shapefile
# Other imports 
import time
from time import sleep
import simpledbf 
from simpledbf import Dbf5
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import matplotlib as mpl
from datetime import datetime
import geocoder
import googlemaps
import random

# Creates a new .shp file with only the country entries that you specified
# WARNING: Takes a long time to run
def filter_by_country(fires_data, country, month, year):
    '''
    Takes Global .shp, .dbf data and returns to you a .shp, .dbf with only the data of a country (Currently only does the United States) 
               We could use different bounding boxes if we wanted to do different countries.
    Inputs:
    fires_data --> The output of the .shp
    fires_data = shapefile.Reader("example.shp")
    country --> country you want to filter for 
    month --> Used for dataset creation when going through month by month data
    year --> Used for dataset creation when going through year by year data
    '''
    fireIds = set()
    w = shapefile.Writer('./../data/United_States_{filter_year}_Fires/{filter_month}/{filter_country}_fires_{filter_month}_{filter_year}.shp'.format(filter_country = country, filter_month = month, filter_year = year))
    w.fields = fires_data.fields[1:]
    # valid_id tracks whether the last read unique id was valid for our country
    valid_id = False
    # Iterate through all shapeRecords for global dataset
    counter = 1
    starting_time = time.time()
    fire_data_shape_records = fires_data.shapeRecords()
    adding_count = 0
    US_bounding_box = [(-124.848974, 24.396308), (-66.885444, 49.384358)]
    for shapeRecord in fire_data_shape_records:
        # Get the fire ID
        fireId = shapeRecord.record[2]
        # If the fireId is not in the country and already read, we go to the next fireID
        if fireId == valid_id:
            w.record(*shapeRecord.record)
            w.shape(shapeRecord.shape) 
            adding_count += 1
            continue
        # If the fireId is not in the country and not yet read, we add it, say it's not in the country (for now)
        # and find its latitude and longitude
        else:
            fireIds.add(fireId)
            valid_id = False
            
        # if it got past above, gets the points latitudes and longitudes

        fireLatLong = shapeRecord.shape.points[0][::-1]

        # If it is the right country using a bounding box, add it to our dataset!
        if fireLatLong[1] > US_bounding_box[0][0] and fireLatLong[1] < US_bounding_box[1][0] and fireLatLong[0] > US_bounding_box[0][1] and fireLatLong[0] < US_bounding_box[1][1]:
            valid_id = fireId
            w.record(*shapeRecord.record)
            w.shape(shapeRecord.shape) 
            adding_count += 1
            print("We've now added ", adding_count, " entries")

                
    print("FINAL Time Passed: ", time.time() - starting_time, " seconds")
    w.close()     

# Returns a database with only certain Id entries. 
def sort_by_id(df,eyeD):
    '''
    Returns a database with only certain ID entries sorted by date
    
    Inputs: 
    df --> Pandas dataframe with the entries of the .dbf file
    df has 4 columns ['IDate', 'Type', 'ID', 'FDate']
    eyeD --> ID you want to filter by 
    Output:
    sorted_id --> Sorted dataframe by date with only certain Ids
    '''
    # Get data for just one fire
    sorted_id = df.loc[df['Id'] == eyeD]
    sorted_id = sorted_id.sort_values(by='IDate')
    return sorted_id
    

    
def plotPolygons(oldBurnIndexArrays, newBurnIndexArray, date, figureIndex = 1):
    '''
    Plots your fire polygons by date and differentiates between old burns and new burns
    
    As a definition, a BurnIndexArray is a list of the vertices of the polygons that are burning. If you have two squares burning,
    it may look like:
    
    BurnIndexArray = [ [ (0,0), (0,1), (1,1), (1,0) ], [ (2,2), (2,3), (3,3), (3,2) ]
    
    Inputs:
  
    oldBurnIndexArrays --> List of all the burn index arrays from previous days
    newBurnIndexArray --> The burn index array for the new day
    date --> date of the new Burn Fire
    figureIndex --> Allows you to create several separate figures
    '''
    fig = plt.figure(figureIndex)
    ax = fig.add_subplot(111)
    polygon_array = []
    for polygon_indices in oldBurnIndexArrays:
        coll = PolyCollection(polygon_indices, cmap=mpl.cm.jet, edgecolors='none')
        ax.add_collection(coll)
        coll.set_color([.5, .1, .1])
        ax.autoscale_view()
    coll = PolyCollection(newBurnIndexArray, cmap=mpl.cm.jet, edgecolors='none')
    ax.add_collection(coll)
    coll.set_color([1, 0, 0])
    ax.autoscale_view()
    ax.set_facecolor('darkgreen')

    plt.title("Active burn on: {:%m/%d/%Y}".format(date))
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
        
    
def dayToDayProgression(df, eyeD, shapeRecords):
    
    '''
    Plot all the day to day progression of a fire
    
    Inputs:
    df --> Pandas dataframe with the entries of the .dbf file
    df has 4 columns ['IDate', 'Type', 'ID', 'FDate']
    shapeRecords --> The shape records (for example)
    shape = shapefile.Reader("example.shp")
    shape_records = shape.shapeRecords() 
    eyeD --> ID you want to filter by 
    Output:
    A day to day plot of the fire progression
    '''
    # Detailing the day to day progression of a fire
    # It looks like some dates have better data than others, which is interesting. General trends look okay though for a first go around! 
    ID_df = sort_by_id(df,eyeD)
    lastFDate = None
    min_max_day = [float('inf'), float('inf'), -float('inf'), -float('inf')]
    day_index = 2 
    polygon_date_array = []
    polygon_date_dict = {}
    for row in ID_df.iterrows():
        if row[1]['Type'] == 'FinalArea':
            continue
        feature = shapeRecords[row[0]]
        if row[1]['FDate'] == lastFDate:
            polygon_date_array.append(feature.shape.points) 

        else:
            lastFDate = row[1]['FDate']
            if len(polygon_date_array) == 0:
                continue
            polygon_date_dict[row[1]['FDate']] = polygon_date_array
            polygon_date_array = []
    fig = plt.figure(day_index)
    ax = fig.add_subplot(111)
    polygon_array = []
    day_index = 1
    for date, polygon_indices in polygon_date_dict.items():
        print(date)
        polygon_indices = polygon_date_dict[date]
        plotPolygons(polygon_array, polygon_indices, date, day_index)
        polygon_array.append(polygon_indices)
        day_index += 1
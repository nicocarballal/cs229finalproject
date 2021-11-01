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
def filter_by_country(fires_data, country, month, gmaps, max_iterations = 10000):
    fireIds = set()
    w = shapefile.Writer('{filter_country}_fires_{filter_month}_2020.shp'.format(filter_country = country, filter_month = month))
    w.fields = fires_data.fields[1:]
    # valid_id tracks whether the last read unique id was valid for our country
    valid_id = False
    # Iterate through all shapeRecords for global dataset
    counter = 1
    starting_time = time.time()
    fire_data_shape_records = fires_data.shapeRecords()
    randomShapeRecords = random.sample(range(len(fire_data_shape_records)), max_iterations)
    adding_count = 0
    for shapeRecordIndex in randomShapeRecords:
        shapeRecord = fire_data_shape_records[shapeRecordIndex]
        # Get the fire ID
        fireId = shapeRecord.record[2]
       
        # If the fireId is not in the country and already read, we go to the next fireID
        if fireId in fireIds:
            continue
        # If the fireId is not in the country and not yet read, we add it, say it's not in the country (for now)
        # and find its latitude and longitude
        else:
            fireIds.add(fireId)
            goodId = False
            
        # if it got past above, gets the points latitudes and longitudes

        fireLatLong = shapeRecord.shape.points[0][::-1]
        
        
        if counter % 100 == 0:
            print("Count: ", counter)
            print("Time Passed: ", time.time() - starting_time, " seconds")
        counter += 1

        #try/except is a cheat for now

        # Gets the readable results
        try: 
            results = gmaps.reverse_geocode(fireLatLong)[1]
            address_dicts = results['address_components']
            # Find the address_dict that details the country and get the country name 
            for address_dict in address_dicts:
                if address_dict['types'][0] == 'country':
                    long_name = address_dict['long_name']
                    break
           
            # If it is the right country, add it to our dataset!
            if long_name.lower() == country.lower():
                goodId = fireId
                earlier_index = shapeRecordIndex - 1
                later_index = shapeRecordIndex + 1 
                shapeEntryBefore = fire_data_shape_records[earlier_index]
                w.record(*shapeRecord.record)
                w.shape(shapeRecord.shape) 
                adding_count += 1
                while shapeEntryBefore.record[2] == fireId:
                    w.record(*shapeEntryBefore.record)
                    w.shape(shapeEntryBefore.shape) 
                    earlier_index -= 1
                    shapeEntryBefore = fire_data_shape_records[earlier_index]
                    adding_count += 1

                shapeEntryAfter = fire_data_shape_records[later_index]

                while shapeEntryAfter.record[2] == fireId:
                    w.record(*shapeEntryBefore.record)
                    w.shape(shapeEntryBefore.shape) 
                    later_index += 1
                    shapeEntryAfter = fire_data_shape_records[later_index]
                    adding_count += 1
                
                print("We've now added ", adding_count, " entries")

                
                
        except Exception as e:
            print("Error: ")
            print(results)
    print("FINAL Time Passed: ", time.time() - starting_time, " seconds")
    w.close()     

def plotPolygons(oldBurnIndexArrays, newBurnIndexArray, date, figureIndex):
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
        
    
    
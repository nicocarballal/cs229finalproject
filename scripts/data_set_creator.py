import util 
import os 
import matplotlib.pyplot as plt
import numpy as np
import googlemaps
import shapefile 

def main(country):
    month_dict = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun', 7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'}
    month = 1
    gmaps = googlemaps.Client(key='AIzaSyDOrI9SeNCty-hSU1NOE8Vx06VXnTB_qVc')
    
    for file in os.listdir(r"C:/Users/nico/Downloads/Full_GlobFireV2_Jan_2021/2020"):
        # check the files which are end with specific extension
        if file.endswith(".shp"):
            # print path name of selected files
            shape = shapefile.Reader("C:/Users/nico/Downloads/Full_GlobFireV2_Jan_2021/2020/{file_name}".format(file_name = str(file)))
            shapeRecords = shape.shapeRecords()
            util.filter_by_country(shape, country, month_dict[month], gmaps)
            month += 1
    



if __name__ == '__main__':
    #main('INSERT COUNTRY HERE')
    main('United States')
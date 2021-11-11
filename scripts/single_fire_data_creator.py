# import cell
import shapefile
import numpy as np
import matplotlib
import pandas as pd
import simpledbf 
from simpledbf import Dbf5
import util
from util import *
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
import matplotlib as mpl
from single_fire import *
import os


def save_individual_fire_data(df, shapeRecords, save_path):
    for eyeD in np.unique(df['Id']):
        idx = df[[df['Id'][i] == eyeD and df['Type'][i] == 'FinalArea' for i in range(len(df))]].index
        final_fire_indices = shapeRecords[idx[0]].shape.points
        sorted_df = sort_by_id(df, eyeD)
        M = multi_day_fire_representation(shapeRecords, sorted_df, final_fire_indices)
        save_ID = save_path + str(eyeD)
        np.save(save_ID, M)


def main(parent_path, yr):
    for subdir, dirs, files in os.walk(parent_path):
        for directory in dirs:

            for file in os.listdir(r"{path}/{month}/".format(path = subdir, month = directory)): 
                # check the files which are end with specific extension
                if file.endswith(".shp"):
                    # print path name of selected files
                    shape = shapefile.Reader("{path}/{month}/{file_name}".format(file_name = str(file), path = subdir, month = directory))
                    shapeRecords = shape.shapeRecords()
                if file.endswith(".dbf"):
                    dbf =  Dbf5("{path}/{month}/{file_name}".format(file_name = str(file), month = directory, path = subdir))
                    df = dbf.to_dataframe()
    
            if not os.path.isdir( "{path}\\{month}\\multi_day\\".format(month = directory, path = subdir)):
                os.mkdir("{path}\\{month}\\multi_day\\".format(month = directory, path = subdir))
            
            save_individual_fire_data(df, shapeRecords, "{path}\\{month}\\multi_day\\".format(path = subdir, month = directory))
            print("Saved data for {x0}-{year}!".format(x0 = directory, year = yr))


if __name__ == '__main__':
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2017_Fires\\', '2017')
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2016_Fires\\', '2016')
   
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2018_Fires\\', '2018')
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2015_Fires\\', '2015')


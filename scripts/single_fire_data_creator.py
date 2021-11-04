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
    


def main(parent_path):
    for x in os.walk(parent_path):

        
        if not os.path.isdir(x[0]) or x[0] == parent_path:
            continue

        for file in os.listdir(r"{path}/".format(path = x[0])): 
            # check the files which are end with specific extension
            if file.endswith(".shp"):
                # print path name of selected files
                shape = shapefile.Reader("{path}/{file_name}".format(file_name = str(file), path = x[0]))
                shapeRecords = shape.shapeRecords()
            if file.endswith(".dbf"):
                dbf =  Dbf5("{path}/{file_name}".format(file_name = str(file), path = x[0]))
                df = dbf.to_dataframe()
  
        if not os.path.isdir( "{path}\\multi_day\\".format(path = x[0])):
            os.mkdir("{path}\\multi_day\\".format(path = x[0]))
         
        save_individual_fire_data(df, shapeRecords, "{path}\\multi_day\\".format(path = x[0]))
        print("Saved data for {x0}!".format(x0 = x[0]))


if __name__ == '__main__':
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2018_Fires\\')
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2017_Fires\\')
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2016_Fires\\')
    main('C:\\Users\\nico\\Desktop\\Stanford\\OneDrive - Stanford\\Courses\\CS229\\finalproject\\data\\United_States_Fires\\United_States_2015_Fires\\')


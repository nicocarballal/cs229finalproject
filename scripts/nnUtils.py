## Import for data generation
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import pickle



def nn_train_test(path, n_past, n_comp, n_future = 1, d = 256):
    x_train_list = []
    y_train_list = []
    count = 0
    for file in os.listdir(r"{path}".format(path = path)):
        if os.path.getsize("{path}\\{file}".format(path = path, file = file)) < 10000000:
            continue
        with open("{path}\\{file}".format(path = path, file = file), 'rb') as f:
            data = pickle.load(f)
        training_fire = data['multiDay']
        if data['Elevation Data'].shape[0] > training_fire.shape[0] and data['Elevation Data'].shape[1] > training_fire.shape[1]:
            elevation_data = data['Elevation Data'][:-1,:-1]
        else:
            elevation_data = data['Elevation Data'][:,:-1]
        
        if data['Topographic Data'].shape[0] > training_fire.shape[0] and data['Topographic Data'].shape[1] > training_fire.shape[1]:
            topographic_data = data['Topographic Data'][:-1,:-1]
        else:
            topographic_data = data['Topographic Data'][:,:-1]
            
        valid_append = []
        for i in range(len(data['Unique Dates']) - n_past):
            if (data['Unique Dates'][i + 3] - data['Unique Dates'][i]).days == 3:
                valid_append.append(i)
        if np.any(data['Elevation Data'] == -9999):
            continue
        if np.any(data['Topographic Data'] == -9999):
            continue
        topographic_data[topographic_data > 13] = 0
        
                
        top_shape = np.array(elevation_data.shape)
        elev_shape = np.array(elevation_data.shape)
        elevation_fire = np.zeros((256, 256))
        fuel_moisture_fire = np.zeros((256,256))
        shape = np.array(training_fire.shape) 
        fire = np.where(training_fire[1] == 1)
        x_center, y_center = int(np.median(fire[0])), int(np.median(fire[1]))
        if shape[0] < n_past + n_future:
            continue
        standard_fire = np.zeros((len(training_fire), 256, 256))    
        if shape[1] > 255 or shape[2] > 255:
            # could not broadcast input array from shape (39,350,325) into shape (39,512,416)
            xLow = x_center - 128 
            xHi = shape[1] - x_center
            yLow = y_center - 128
            yHi = shape[2] - y_center 
            if shape[1] > 255:  
                if xLow < 0:
                    xHi = x_center + 128 - xLow
                    xLow = 0
                elif xHi < 128:       
                    xLow = x_center - 256 + xHi
                    xHi = shape[1]                   
                else:
                    xLow = x_center - 128
                    xHi = x_center + 128
            else:            
                xLow = 0
                xHi = shape[1]
            if shape[2] > 255:
                if yLow < 0:
                    yHi = y_center + 128 - yLow
                    yLow = 0
                elif yHi < 128:
                    yLow = y_center - 256 + yHi
                    yHi = shape[2]
                else:
                    yLow = y_center - 128
                    yHi = y_center + 128
            else:
                yLow = 0
                yHi = shape[2]
            standard_fire[:shape[0], :min(256, shape[1]), :min(256, shape[2])] = training_fire[:, xLow: xHi, yLow: yHi]  
            elevation_fire[:min(256, elev_shape[0]), :min(256, elev_shape[1])] = elevation_data[xLow: xHi, yLow: yHi]
            fuel_moisture_fire[:min(256, top_shape[0]), :min(256, top_shape[1])] = topographic_data[xLow: xHi, yLow: yHi]
        else: 
            standard_fire[:shape[0], :shape[1], :shape[2]] = training_fire
            elevation_fire[:min(256, elev_shape[0]), :min(256, elev_shape[1])] = elevation_data
            fuel_moisture_fire[:min(256, top_shape[0]), :min(256, top_shape[1])] = topographic_data
        
        pca_fire = standard_fire
        pca_elev = elevation_fire.reshape((1, 256, 256))
        pca_fuel = fuel_moisture_fire.reshape((1, 256, 256))
        
        for i in range(0 , len(training_fire) - n_future - n_past + 1):
            if i not in valid_append:
                continue
            shape = pca_fire[i : i + n_past].shape
            a = np.zeros((shape[0] + 2, shape[1], shape[2]))
            a[:3] = pca_fire[i : i + n_past]
            a[3:4] = pca_elev 
            a[4:5] = pca_fuel
            for j in np.arange(0, 255, d):
                for k in np.arange(0, 255, d):
                    x_train_list.append(a[:, j:j+d, k:k+d])
                    y_train_list.append(pca_fire[i + n_past: i + n_past + n_future, j:j+d, k:k+d])   
    x_train = np.array(x_train_list)
    y_train = np.array(y_train_list)  
    print(x_train.shape, y_train.shape)
    return x_train, y_train
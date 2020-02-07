# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:26:10 2020

Author: Blas Lajarín Sánchez

Title: Heatwaves alerts calculation

Description: Calculate the number of days with alerts due to heatwaves at required coordinates, using
NetCDF's with daily maximum and minimum temperature.
"""

import itertools as it
import numpy as np
from netCDF4 import Dataset
import pandas as pd


####################################  HEATWAVE ALERTS FUNCTION  #################################################################################################

'''This function calculates the number of days with alert because of heatwaves. The parameters of the alert can be defined.

---INPUTS:
    
    dataframe_temperature: [pandas dataframe] with at least two columns: temperature maximum, temperature minimum
    
    name_tmax_column: [string] name of the maximum temperature column
    
    name_tmin_column: [string] name of the minimum temperature column
    
    tmax_threshold: [integer or real] Threshold of maximum temperature (both maximum and minimum temperatures must be equal or exceed the thresholds to get an alert).
    
    tmin_threshold: [integer or real] Threshold minimum temperature (both maximum and minimum temperatures must be equal or exceed the thresholds to get an alert).
    
    n_days: [integer] Number of days that the threshold must be exceeded to get an alert.

---OUTPUT:
    
    n_alerts_days: [integer] number of days with alert
'''

def calc_heatwave_alerts(dataframe_temperature, name_tmax_column, name_tmin_column, tmax_threshold, tmin_threshold, n_days):
    
    #Create a new column 'check'. If the maximum and the minimum temperature exceed the thresholds = TRUE, else = FALSE
    dataframe_temperature['check'] = (dataframe_temperature[name_tmax_column] >= tmax_threshold) & (dataframe_temperature[name_tmin_column]  >= tmin_threshold) 
    list_check = dataframe_temperature['check'].tolist()
    
    #Create an iterable itertools.groupby 
    groups_boolean = it.groupby(list_check)
    #Create a list of tuples. Each tuple: first element = value grouped, second element = number of consecutive repetitions of that value.
    result = [(label, sum(1 for _ in group)) for label, group in groups_boolean]
    
    #Iteration over result to create a new list (list_check_periods), where only the days, that belong to a period that is equal or exceeds n_days, are TRUE;
    #the rest of them FALSE
    list_check_periods = []
    for i in result:
        list_tuple = list(i)
        if list_tuple[1] < n_days:#Check the number of days
            list_tuple[0] = False
        sublist = list(it.repeat(list_tuple[0],list_tuple[1]))
        list_check_periods.extend(sublist)
    
    #Count the number of days with alert
    n_alert_days = list_check_periods.count(True)
    
    return n_alert_days
    

########################################## HEATWAVE ALERTS CALCULATION #######################################################################################


###################################### EXTRACT VARIABLES FROM NETCDF
    
#Open netcdf's
dataset_tmax_name = 'E:\\Proyectos\\C3S\\Dashboard\\data\\variables_futuro_CMIP5_ERA5land\\todos\\tasmax_ACCESS1-0_rcp45_Spain_2020.nc'
dataset_tmax = Dataset(dataset_tmax_name)
dataset_tmin_name = 'E:\\Proyectos\\C3S\\Dashboard\\data\\variables_futuro_CMIP5_ERA5land\\todos\\tasmin_ACCESS1-0_rcp45_Spain_2020.nc'
dataset_tmin = Dataset(dataset_tmin_name)

#Open variables, longitudes and latitudes
tmax_variable_name = 'tasmax'
tmax_variable = dataset_tmax.variables[tmax_variable_name][:].data
tmin_variable_name = 'tasmin'
tmin_variable = dataset_tmin.variables[tmin_variable_name][:].data
lon_variable_name = 'longitude'
longitudes = dataset_tmin.variables[lon_variable_name][:].data
lat_variable_name = 'latitude'
latitudes = dataset_tmin.variables[lat_variable_name][:].data
dataset_tmin.close()
dataset_tmax.close()

#Point where heatwaves are calculated (example: Madrid Airport)
lon_point = -3.592496
lat_point = 40.509356

#Indexes to extract the value from that point
idx_lon = (np.abs(longitudes - lon_point)).argmin()
idx_lat = (np.abs(latitudes - lat_point)).argmin()

#Extract the time series of that point
tmin_variable_point = tmin_variable[:, idx_lat, idx_lon]
tmax_variable_point = tmax_variable[:, idx_lat, idx_lon]


###################################### CREATE DATAFRAME

#Create array of dates
#Initial date
date = np.array('1986-01-01', dtype=np.datetime64)
#Number of days in our netcdf
number_days = 7305 #1986 to 2005
array_date = date + np.arange(number_days)
#Create pandas dataframe
df_tas = pd.DataFrame()
#Creaete 'date' column
df_tas['date']=array_date


###################################### HEATWAVE ALERTS FUNCTION: ARGUMENTS

#Threshold maximum temperature
tmax_threshold = 38
#Threshold minimum temperature
tmin_threshold = 20
#Name of the maximum temperature column
name_tmax_column = 'tmax'
#Name of the minimum temperature column
name_tmin_column = 'tmin'
#Create maximum temperature column                 
df_tas[name_tmax_column] = tmax_variable_point - 273.15
#Create minimum temperature column   
df_tas[name_tmin_column] = tmin_variable_point - 273.15
#Number of days exceeding the threshold
days = 6
#Number of days with alert
alert_number = calc_heatwave_alerts(df_tas,name_tmax_column, name_tmin_column, tmax_threshold, tmin_threshold, days)



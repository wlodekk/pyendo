# -*- coding: utf-8 -*-
"""
Endomodo json files loader
Created on 10 Nov 2020
@author: Włodzimierz Kuczyński email:wlo.kucz@gmail.com
"""
import pandas as pd
import numpy as np
import datetime
import os
import json
from glom import merge, flatten
from timezonefinder import TimezoneFinder as tf
# from datetime import datetime
from dateutil.parser import parse
prompt = None

prompt = input('Would you like to load the json files?(y/n)')
# default timezone when there are no GPS coordinates; otherwise GPS coordinates are used to determine the timezone 
default_timezone = 'Europe/Warsaw'
if prompt == 'y':
# this finds the json files   
    path_to_json = 'endomondo-2020-10-28/Workouts'
    json_files = [pos_json for pos_json in os.listdir(path_to_json)
                  if pos_json.endswith('.json')]
    jn_all = None
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
            jn_merged = merge(json_text)
            points_merged = []
            for point in jn_merged['points']:
                point_merged = merge(point)
                points_merged.append(point_merged)
            for ptm in points_merged:
                if 'location' in ptm:
                    ptm['location'] = merge(flatten(ptm['location']))
            points_norm = pd.json_normalize(points_merged)
            ptm_len = points_norm.shape[0]
            points_norm.rename(columns={'location.latitude': 'latitude',
                                        'location.longitude': 'longitude',
                                        'distance_km': 'distance'}, inplace=True)
            jn_norm = pd.json_normalize(jn_merged)
            del jn_norm['points']
            jn_norm = pd.concat([jn_norm]*ptm_len, ignore_index = True)
            jn_pts = pd.concat([jn_norm, points_norm], axis=1)
            jn_pts.insert(0, "training_id", index)
            if jn_all is None:
                jn_all = pd.DataFrame(columns=jn_pts.columns)
            jn_all = pd.concat([jn_all, jn_pts])
    jn_all['created_date'] = pd.to_datetime(jn_all['created_date'],
                                            format='%Y-%m-%d %H:%M:%S', utc=True)
    jn_all['start_time'] = pd.to_datetime(jn_all['start_time'],
                                          format='%Y-%m-%d %H:%M:%S', utc=True)
    jn_all['end_time'] = pd.to_datetime(jn_all['end_time'],
                                        format='%Y-%m-%d %H:%M:%S', utc=True)
    jn_all['timestamp'] = jn_all['timestamp'].apply(lambda t: parse(t))
    jn_all['timestamp'] = pd.to_datetime(jn_all['timestamp'], utc=True)
    jn_all.reset_index(drop=True, inplace=True)
    tzat = tf().timezone_at
    jn_all['timezone'] = jn_all[jn_all['latitude'].notnull()].apply(
        lambda x: tzat(lng=x['longitude'], lat=x['latitude']), axis=1)
    jn_all['timezone'] = jn_all.groupby('training_id')['timezone'].transform(lambda x:
                                                                             default_timezone
                                                                             if pd.isnull(x).all() == True else x.loc
                                                                             [x.first_valid_index()])
    jn_all['created_date'] = jn_all.apply(lambda x:
                                          x['created_date'].tz_convert(
                                              x['timezone']).tz_localize(None)
                                          if pd.notnull(x['created_date']) is True
                                          else x['created_date'], axis=1)
    jn_all['start_time'] = jn_all.apply(lambda x:
                                        x['start_time'].tz_convert(
                                            x['timezone']).tz_localize(None)
                                        if pd.notnull(x['start_time']) is True
                                        else x['start_time'], axis=1)
    jn_all['end_time'] = jn_all.apply(lambda x:
                                      x['end_time'].tz_convert(x['timezone']).tz_localize(None)
                                      if pd.notnull(x['end_time']) is True
                                      else x['end_time'], axis=1)
    jn_all['timestamp'] = jn_all.apply(lambda x:
                                       x['timestamp'].tz_convert(x['timezone']).tz_localize(None)
                                       if pd.notnull(x['timestamp']) is True
                                       else x['timestamp'], axis=1)
    #replaces all similar sports with CYCLING
    jn_all['sport'] = jn_all['sport'].replace(['CYCLING_SPORT','MOUNTAIN_BIKING', 'CYCLING_TRANSPORTATION'],'CYCLING')
    
    #converting km/h to timedelta minutes per km
    def convmkm(kmh):
        mkm = np.nan if pd.isna(kmh) or kmh == 0  else datetime.timedelta(minutes=60/kmh)
        return mkm
    #converting timedelta minutes per km to formatted strings i.e. 3:10.86 
    def strmkm_conv(m):
        if pd.isna(m):
            return None
        else:
            s=m.seconds
            ms=m.microseconds
            minutes,seconds=divmod(s,60)
            return '{:02}:{:02}.{:02}'.format (minutes,seconds,int(round((ms/10000))))
    jn_all['avgmkm']=jn_all.apply(lambda x: convmkm(x['speed_avg_kmh'] ), axis=1)
    jn_all['favgmkm']=jn_all.apply(lambda x: strmkm_conv(x['avgmkm']), axis=1)
    jn_all['maxmkm']=jn_all.apply(lambda x: convmkm(x['speed_max_kmh'] ), axis=1)
    jn_all['fmaxmkm']=jn_all.apply(lambda x: strmkm_conv(x['maxmkm']), axis=1)
    jn_all['mkm']=jn_all.apply(lambda x: convmkm(x['speed_kmh'] ), axis=1)
    jn_all['fmkm']=jn_all.apply(lambda x: strmkm_conv(x['mkm']), axis=1)

    #saving main dataframe to feather file
    jn_all.to_feather("Endomodo.feather")
#reading the dataframe from the feather file
jn_all = pd.read_feather("Endomodo.feather")
jn_all.fillna(value=np.nan, inplace=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 18:52:37 2024

@author: doan
"""

import pandas as pd
import glob, os, sys
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import numpy as np


#ifiles = sorted(glob.glob('../download_AMeDAS_and_create_IDF/data_download/hourly/47646/*.csv'))
#for f in ifiles[-365:]:
#    df = pd.read_csv(f, index_col=0, parse_dates=True)

ifiles = sorted(glob.glob('../download_AMeDAS_and_create_IDF/data_download/daily/47646/*.csv'))


dd = []
for f in ifiles[:]:
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    dd.append(df)

dx = pd.concat(dd)
dx = dx.dropna(how='all')
doy = dx.index.day_of_year
dx['doy'] = doy

dx.sort_index(inplace=True)
x_col = ['temp_C']
x_col = ['temp_C']
x_col =         ['precip-accum_mm']
#x_col = ['doy']
y_col = ['precip-accum_mm']
col = x_col + y_col 
col = np.unique(col)

XY = dx[ col ]
XY = XY.dropna()

XY = XY.loc['1981':'2020']

#XX = XY_train[:-1].loc[:,['temp_C']]





x = XY.values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
XY_s = pd.DataFrame(x_scaled, columns=XY.columns, index = XY.index)


XY_train = XY_s.loc['1981':'2010']
XY_test = XY_s.loc['2010':'2020']



#X_train, y_train =  XY_train[:-1].loc[:,['temp_C', 'doy']], XY_train[1:].loc[:,['temp_C']]
#X_test, y_test =  XY_test[:-1].loc[:,['temp_C', 'doy']], XY_test[1:].loc[:,['temp_C']]



X_train, y_train =  XY_train[:-1].loc[:,x_col ], XY_train[1:].loc[:, y_col  ]
X_test, y_test =  XY_test[:-1].loc[:, x_col ], XY_test[1:].loc[:, y_col ]


#X_train, y_train =  XY_train[:-1].loc[:,[ 'doy']], XY_train[1:].loc[:,['temp_C']]
#X_test, y_test =  XY_test[:-1].loc[:,[ 'doy']], XY_test[1:].loc[:,['temp_C']]


#X, Y = XY[:-1].loc[:,['temp_C']], XY[1:].loc[:,['temp_C']]
#x = dx.temp_C
#X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)



from sklearn import linear_model
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor


#tree_model = DecisionTreeRegressor()
#model = linear_model.LinearRegression()
model = MLPRegressor(hidden_layer_sizes=(100), 
                     random_state=1, 
                     activation='relu', 
                     solver='adam', alpha=0.0001, batch_size='auto',
                     max_iter=500)
#DecisionTreeRegressor()

#RandomForestRegressor()

#tree_model.fit(X_train.values, y_train.values)
#model.fit(X_train, y_train)
model.fit(X_train, y_train)

y_pred = model.predict(X_test) #[:,0]
x1 = min_max_scaler.inverse_transform(XY_test)[:-1]

xout = XY_test[:-1].copy()
xout.loc[:,'precip-accum_mm'] = y_pred


y_predx = min_max_scaler.inverse_transform(xout) #- x1

y_pred = pd.DataFrame(y_predx, columns=xout.columns, index = xout.index)
y_pred = y_pred[ y_col ]




y_pred.plot()

print((y_pred**2).mean())

y_pred.loc['2020'].plot()










sys.exit()

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


tree_mse = mean_squared_error(y_train, tree_model.predict(X_train))
tree_mae = mean_absolute_error(y_train, tree_model.predict(X_train))
rf_mse = mean_squared_error(y_train, rf_model.predict(X_train))
rf_mae = mean_absolute_error(y_train, rf_model.predict(X_train))

from math import sqrt

print("Decision Tree training mse = ",tree_mse," & mae = ",tree_mae," & rmse = ", sqrt(tree_mse))
print("Random Forest training mse = ",rf_mse," & mae = ",rf_mae," & rmse = ", sqrt(rf_mse))


tree_test_mse = mean_squared_error(y_test, tree_model.predict(X_test))
tree_test_mae = mean_absolute_error(y_test, tree_model.predict(X_test))
rf_test_mse = mean_squared_error(y_test, rf_model.predict(X_test))
rf_test_mae = mean_absolute_error(y_test, rf_model.predict(X_test))

print("Decision Tree test mse = ",tree_test_mse," & mae = ",tree_test_mae," & rmse = ", sqrt(tree_test_mse))
print("Random Forest test mse = ",rf_test_mse," & mae = ",rf_test_mae," & rmse = ", sqrt(rf_test_mse))


import numpy as np
def display_scores(scores):
    print("Scores:", scores)
    print("Mean:", scores.mean())
    print("Standard deviation:", scores.std())
    print("\n")


from sklearn.model_selection import cross_val_score

scores = cross_val_score(tree_model, X_train, y_train, scoring="neg_mean_squared_error", cv=10)
tree_rmse_scores = np.sqrt(-scores)

scores = cross_val_score(rf_model, X_train, y_train, scoring="neg_mean_squared_error", cv=10)
rf_rmse_scores = np.sqrt(-scores)


display_scores(tree_rmse_scores)



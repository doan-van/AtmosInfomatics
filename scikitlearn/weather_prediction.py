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
import matplotlib.pyplot as plt


#ifiles = sorted(glob.glob('../download_AMeDAS_and_create_IDF/data_download/hourly/47646/*.csv'))
#for f in ifiles[-365:]:
#    df = pd.read_csv(f, index_col=0, parse_dates=True)


stn = '47662'
stn = '47646'
ifiles = sorted(glob.glob('../download_AMeDAS_and_create_IDF/data_download/daily/'+stn+'/*.csv'))

dd = []
for f in ifiles[:]:
    #print(f)
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    dd.append(df)


dx = pd.concat(dd)
dx.sort_index(inplace=True)
dx.replace(-999, np.NaN, inplace=True)
doy = dx.index.day_of_year
dx['doy'] = doy


if 1:
    
    x_col = ['temp_C']
    x_col = ['temp_C'] #, 'precip-accum_mm']
    #x_col =         ['precip-accum_mm']
    #x_col = ['doy']
    #y_col = ['precip-accum_mm']
    y_col = ['temp_C']
    col = x_col + y_col 
    col = np.unique(col)
    
    
    dat = dx.loc['1981':'2020',col ]
    dat.dropna(inplace=True)
    
    # normalize data (max=1 min=0 )
    xmin, xrange = dat.min(), dat.max() - dat.min()
    dat_nml = (dat - xmin ) / xrange
    
    

    # training data
    dat_train = dat_nml.loc['1981':'2010']
    dat_test = dat_nml.loc['2010':'2020']
    
    
    
    #n = 1
    #X_train_x, X_test_x = dat_train[x_col][:-n].values, dat_test[x_col][:-n].values
    #y_train_x, y_test_x = dat_train[y_col][n:].values, dat_test[y_col][n:].values
    
    
    
    yy, xx = [], []
    for d in [dat_train, dat_test]:
        n = 1
        yy.append(d[y_col][n:].values)
        for xc in x_col[:]:
            xt = np.array([d[xc][i:-n+i].values for i in range(n)])
        
        xx.append(xt.T)
        
        
    
    
    X_train, X_test = xx
    y_train, y_test = yy
    
    #X_train, X_test = X_train_x, X_test_x
    #y_train, y_test = y_train_x, y_test_x
    #sys.exit()
    
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
    
    #model = RandomForestRegressor()
    model = linear_model.LinearRegression()
    
    #tree_model.fit(X_train.values, y_train.values)
    #model.fit(X_train, y_train)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)[:,0]
    
    y_pred_inv = y_pred * xrange['temp_C'] + xmin['temp_C']
    y_test_inv = y_test[:,0] * xrange['temp_C'] + xmin['temp_C']
    
    bias = y_pred_inv - y_test_inv
    mse  = ((y_pred_inv - y_test_inv)**2)**.5
    
    #x1 = min_max_scaler.inverse_transform(XY_test)[:-1]
    #xout = XY_test[:-1].copy()
    #xout.loc[:,'temp_C'] = y_pred
    #y_predx = min_max_scaler.inverse_transform(xout) - x1
    
    #y_pred = pd.DataFrame(y_predx, columns=xout.columns, index = xout.index)
    #y_pred = y_pred[ y_col ]
    
    do =  pd.DataFrame({'yp': y_pred_inv, 'yr': y_test_inv, 'bias':bias, 
                        'mse':mse }, index=dat_test[n:].index)
    
    
    #do['bias'].plot()
    
    print(do.mean())
    plt.show()
    do.loc['2020', 'bias'].plot()
    plt.show()
    
    do.loc['2020-02', ['yp', 'yr']].plot()

    (do['yp'] - do['yr']).loc['2020-02'].plot()














sys.exit()

x_col = [ 'temp_C']
#x_col = ['precip-accum_mm', 'temp_C']
#x_col =         ['precip-accum_mm']
#x_col = ['doy']
#y_col = ['precip-accum_mm']
y_col = ['temp_C']

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
x1 = min_max_scaler.inverse_transform(XY_test)[1:]

xout = XY_test[1:].copy()
xout.loc[:,'temp_C'] = y_pred


y_predx = min_max_scaler.inverse_transform(xout) - x1

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



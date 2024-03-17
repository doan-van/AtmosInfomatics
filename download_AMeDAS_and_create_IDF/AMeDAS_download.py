#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time, sys, glob
import pandas as pd
#from download_extract_table import download
import numpy as np
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, Hodograph, SkewT
from metpy.units import units


# plot map
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap, PowerNorm
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np
from sklearn.linear_model import LinearRegression
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker    
import cartopy.feature as cfeature






#-------Header function---------------
def get_info(h,att):
    #if h.has_key(att): nu = int(h.get(att))
    if h.has_attr(att): nu = int(h.get(att))
    else: nu = 1
    return nu

#==========
def conv_text_sonde(text):
    change = {'日':'Day', 
              '気圧(hPa)':'Pres(hPa)',
              'ジオポテンシャル':'GeoPot',
              '高度(m)':'Height(m)',
              '気温(℃)':'Temp(C)',
              '相対湿度(%)':'RH(%)',
              '風速(m/s)':'WindSpd(m/s)',
              '風向(°)':'WindDir(deg)',
              '識別符':'Mark'
              }
    for k, v in change.items(): 
        text = text.replace(k,v)
    return text
#------------------------------------

def rep_text(text):
    text = text.replace('///','')
    text = text.replace('特異点','SingularPoint')
    return text
            
def rep_text_wdir(text):
    text = text.replace('西','W')
    text = text.replace('東','E')
    text = text.replace('南','S')
    text = text.replace('北','N')
    text = text.replace('静穏','Calm')
    text = text.replace('--','0')
    return text


def get_data_sonde(point, date, opath):
    print(date)
    year, mon, day, hour = str(date.year), '%.2d' % date.month, '%.2d' % date.day,'%.2d' % date.hour
    #'2020', '01', '02', '21'
    try:
    #if True:   
        hp1 = 'https://www.data.jma.go.jp/obd/stats/etrn/upper/view/'
        url = hp1 + 'hourly_usp.php?year='+year+'&month='+mon+'&day='+day+'&hour='+hour+'&atm=&point='+point+'&view='
        print('***' , '指定気圧面の観測データ', '****')
        print('trying to access:  ', url)
        
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table1 = soup.find('table', id='tablefix1') # Get table
        table2 = soup.find('table', id='tablefix2') # Get table
                  
        #daily_uth.php?year=2020&month=2&day=1&hour=21&atm=&point=47646&view=
        
        url = hp1 + 'daily_uth.php?year='+year+'&month='+mon+'&day='+day+'&hour='+hour+'&atm=&point='+point+'&view='
        
        print('***' , '気温・湿度の観測データ', '****')
        print('trying to access:  ', url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table3 = soup.find('table', id='tablefix1') # Get table
        
        
        #daily_uwd.php?year=2020&month=2&day=1&hour=21&atm=&point=47646&view=
        
        url = hp1 + 'daily_uwd.php?year='+year+'&month='+mon+'&day='+day+'&hour='+hour+'&atm=&point='+point+'&view='
        print('***' , '風の観測データ', '****')
        print('trying to access:  ', url)        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table4 = soup.find('table', id='tablefix1') # Get table
        
    
        dd = []
        for table in [table1, table2,table3,table4]:
            rows = table.findAll('tr')  # split to rows
            #-----Get header information---------
            header = [ [{ 'scol':get_info(c,'colspan'), 'srow':get_info(c,'rowspan'), 'text':conv_text_sonde(c.text) } for c in tr] for tr in rows]
                
            header = [x for x in header if x ]
            
            # number of header columns
            nu_col = max([ sum([c['scol'] for c in header[irow]]) for irow in range(2)])
            
            hd = ['']*len(header)*nu_col # there are two rows and 2 cols
            # split row and column of header
            for irow in range(len(header)):
                for h1 in header[irow]:
                    idb = hd.index('')
                    for ir in range(h1['srow']):
                        for ic in range(h1['scol']): 
                            #print h1['text'], idb+ic+ir*nu_col 
                            hd[idb + ic + ir*nu_col] = h1['text']
            
            # merge rows of header
            hder = [] 
            nu_headrow = header[0][0]['srow']
            for i in range(nu_col): 
                #if hd[i] != hd[i+nu_col]: hder.append(hd[i + nu_col]+hd[i])
                #else: 
                hder.append( '_'.join(list(np.unique(np.array([ hd[i+ii*nu_col] for ii in range( nu_headrow ) ])))))
                            
            
            # Get data            
            data = [ [ rep_text(c.text) for c in tr] for tr in rows]
            data = [x for x in data if x ][header[0][0]['srow']:]
            
            do = pd.DataFrame(data, columns = hder)
            dd.append(do)

        path = opath + '/'+point+'/' 
        #print(path+year+'_'+month+'_'+day+".csv")
        if not os.path.isdir(path): os.makedirs(path)
        
        if (table1 != None) and (table2 != None):
        
            dout = pd.concat(dd[:2])
            dout.set_index('Pres(hPa)',inplace=True)
            for c in dout.columns: dout.loc[:,c] = pd.to_numeric(dout.loc[:,c], errors='coerce')
            dip = dout
            dip.to_csv(path+'Interp_'+year+'-'+mon+'-'+day+'_'+hour+".csv", header=True, index=False, encoding='utf-8')
        
        
        if (table3 != None):          
            dout = dd[2]
            dout.set_index('Pres(hPa)',inplace=True)
            for c in dout.columns[:-1]: dout.loc[:,c] = pd.to_numeric(dout.loc[:,c], errors='coerce')
            dth = dout
            dth.to_csv(path+'TempHum_'+year+'-'+mon+'-'+day+'_'+hour+".csv", header=True, index=False, encoding='utf-8')

        if (table4 != None):               
            dout = dd[3]
            dout.set_index('Pres(hPa)',inplace=True)
            for c in dout.columns[:-1]: dout.loc[:,c] = pd.to_numeric(dout.loc[:,c], errors='coerce')
            dwd = dout
            dwd.to_csv(path+'Wind_'+year+'-'+mon+'-'+day+'_'+hour+".csv", header=True, index=False, encoding='utf-8')
        return {'noisuy':dip, 'qtrac_th': dth, 'qtrac_wind':dwd}
    except:
        print(date, '\n **** \n File not exist \n **** \n') 
        return {}
        
    
    
def compass2angle(com):
    arr=['N','NNE','NE','ENE','E','ESE', 'SE', 'SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    angle = np.arange(16)*360/16.
    if com in arr: ang = angle[arr.index(com)]
    else: ang = np.NAN 
    return ang        



#======================
# read all daily-basis files
vard =  {# kansho
        'hourly':{
            # kansho
            '気圧(hPa)_現地': 'glp_hPa',
            '気圧(hPa)_海面': 'slp_hPa',
            '降水量(mm)': 'precip_mm',
            '気温(℃)': 'temp_C',
            '露点温度(℃)': 'dewtemp_C',
            '蒸気圧(hPa)': 'vapor-pres_hPa',
            '湿度(％)': 'rh_percent',
            '風向・風速(m/s)_風速': 'wspd_ms',
            '風向_風向・風速(m/s)': 'wdir_deg',
            '日照時間(h)': 'sunlit_h',
            '全天日射量(MJ/㎡)': 'rad-global_MJm-2',
            '降雪_雪(cm)': 'snowfall_cm',
            '積雪_雪(cm)': 'snowdepth_cm',
            '天気': 'weather_typ',
            '雲量': 'cloudcover_x',
            '視程(km)': 'visibility_km', 
            #Amedas
            '降水量(mm)': 'precip_mm', ##
            '気温(℃)': 'temp_C', ##
            '露点温度(℃)': 'dewtemp_C', ##
            '蒸気圧(hPa)': 'vapor-pres_hPa',
            '湿度(％)': 'rh_percent',
            '平均風速(m/s)_風速・風向': 'wspd_ms',
            '風向_風速・風向': 'wdir_deg',
            '日照時間(h)': 'sunlit_h',
            '降雪(cm)_雪': 'snowfall_cm',
            '積雪(cm)_雪': 'snowdepth_cm',},
         'daily':{
             # daily amedas:::::::::
             '合計(mm)_降水量': 'precip-accum_mm',
             '最大1時間(mm)_降水量': 'precip-hourmax_mm',
             '最大10分間(mm)_降水量': 'precip-10minmax_mm',
             '平均(℃)_気温': 'temp_C',
             '最高(℃)_気温': 'temp-max_C',
             '最低(℃)_気温': 'temp-min_C',
             '平均(％)_湿度': 'rh_percent',
             '最小(％)_湿度': 'rh-min_percent',
             '平均風速(m/s)_風向・風速': 'wspd_ms',
             '最大_風向・風速_風速(m/s)': 'wspd-max_ms',
             '最大_風向_風向・風速': 'wdir-max_deg',
             '最大瞬間_風向・風速_風速(m/s)': 'wspd-max-inst_ms',
             '最大瞬間_風向_風向・風速': 'wdir-max-inst_deg',
             '最多風向_風向・風速': 'wdir-dominant_deg',
             '日照時間(h)': 'sunlit_h',
             '降雪の深さの合計(cm)_雪': 'snowfall-accum_cm',
             '最深積雪(cm)_雪': 'snowdepth-accum_cm',
             # daily kansho
             '平均_気圧(hPa)_現地': 'glp_hPa',
             '平均_気圧(hPa)_海面': 'slp_hPa',
             '合計_降水量(mm)': 'precip-accum_mm',
             '1時間_最大_降水量(mm)': 'precip-hourmax_mm',
             '10分間_最大_降水量(mm)': 'precip-10minmax_mm',
             '平均_気温(℃)': 'temp_C',
             '最高_気温(℃)': 'temp-max_C',
             '最低_気温(℃)': 'temp-min_C',
             '平均_湿度(％)': 'rh_percent',
             '最小_湿度(％)': 'rh-min_percent',
             '平均風速_風向・風速(m/s)': 'wspd_ms',
             '最大風速_風向・風速(m/s)_風速': 'wspd-max_ms',
             '最大風速_風向_風向・風速(m/s)': 'wdir-max_deg',
             '最大瞬間風速_風向・風速(m/s)_風速': 'wspd-max-inst_ms',
             '最大瞬間風速_風向_風向・風速(m/s)': 'wdir-max-inst_deg',
             '日照時間(h)': 'sunlit_h',
             '合計_降雪_雪(cm)': 'snowfall-accum_cm',
             '値_最深積雪_雪(cm)': 'snowdepth-accum_cm',
             '天気概況_昼(06:00-18:00)': 'WeaCon-day6-18_x',
             '夜(18:00-翌日06:00)_天気概況': 'WeaCon-night18-n6_x',
         }
    }

#==============================================================================
#==============================================================================


    
    
    
    
    
    
    
    


#==============================================================================
#==============================================================================
def download_amedas(point, date, opath, dtype='hourly'):
    
    amedas_file = 'Amedas_list.csv'
    
    alist = pd.read_csv(amedas_file, index_col=0)
    
    pinf = alist.loc[alist['station_id'] == int(point)].to_dict(orient='records')[0]
    prec_no  = str(pinf['fuken_id'])
    block_no = str(pinf['station_id']).zfill(4)
    st_type = pinf['type'].lower()
    
    year, month, day = str(date.year), '%.2d' % date.month, '%.2d' % date.day


    days = {'hourly':day, 'daily':''}
                
    url = "http://www.data.jma.go.jp/obd/stats/etrn/view/"
    contenturl = url +dtype+'_'+st_type+'1.php?prec_no='+prec_no+ \
           '&block_no='+block_no+ \
           '&year='+year+'&month='+month+'&day='+days[dtype]+'&view='

    
        
    try:
        response = requests.get(contenturl)
        
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find('table', id='tablefix1') # Get table
        if table != None:
            rows = table.findAll('tr')  # split to rows
            #-----Get header information---------
            #header = [ [{ 'scol':get_info(c,'colspan'), 
            #              'srow':get_info(c,'rowspan'), 
            #             'text':conv_text_hourly(c.text) 
            #             } for c in tr] for tr in rows]
            header = []
            for itr, tr in enumerate(rows):
                header1 = []
                for ic, c in enumerate(tr):
                    
                    if c == '\n': continue
                    text = c.text, #conv_text_hourly(c.text)
                    scol = get_info(c,'colspan')
                    srow = get_info(c,'rowspan')
                    header1.append( { 'scol': scol, 'srow': srow, 'text': text })
                                   
                header.append(header1)


            header = [x for x in header if x ]

            # number of header columns
            nu_col = max([ sum([c['scol'] for c in header[irow]]) for irow in range(2)])

            hd = ['']*len(header)*nu_col # there are two rows and 2 cols
            # split row and column of header
            for irow in range(len(header)):
                for h1 in header[irow]:
                    idb = hd.index('')
                    for ir in range(h1['srow']):
                        for ic in range(h1['scol']):
                            #print h1['text'], idb+ic+ir*nu_col
                            hd[idb + ic + ir*nu_col] = h1['text']

            # merge rows of header
            hder = []
            nu_headrow = header[0][0]['srow']
            for i in range(nu_col):
                #if hd[i] != hd[i+nu_col]: hder.append(hd[i + nu_col]+hd[i])
                #else:
                hder.append( '_'.join(list(np.unique(np.array([ hd[i+ii*nu_col] for ii in range( nu_headrow ) ])))))
            
            # Get data
            data = [ [ c.text for c in tr] for tr in rows]
            #data = [ [ rep_text(c.text) for c in tr] for tr in rows]
            data = [x for x in data if x ][header[0][0]['srow']:]
            
            do0 = pd.DataFrame(data, columns = hder)
            
            if dtype == 'hourly':
                index = [ pd.to_datetime( year + '-'+month+'-'+day) + pd.Timedelta(h+' hour')  for h in do0.loc[:,'時'].values ]
                do0 = do0.drop(['時'], axis=1)
            if dtype == 'daily':
                index = [ pd.to_datetime( year + '-'+month+'-'+day) + pd.Timedelta( str(int(h)-1)+' day')  for h in do0.loc[:,'日'].values ]
                do0 = do0.drop(['日'], axis=1)
                
            do0.index = index
            
            #for co in do0.columns: print('\''+co+'\': \'\',')
                
            do0.columns = [ vard[dtype][c] for c in do0.columns]
            #print('*****')
            #for co in do0.columns: print(co)
                
            do = do0.copy()
            
            
            
            if dtype == 'hourly':
                
                do.loc[:,'wdir_deg'] =[ compass2angle(rep_text_wdir(d)) for d in do.wdir_deg.values]
                
                #do.loc[:,'wdir_deg'] = [compass2angle(d) for d in do.wdir_deg.values]
                if 'cloudcover_x' in do.columns:
                    do.loc[:, 'cloudcover_x'] = [ v.replace('-', '').replace('+', '')  for v in do.cloudcover_x.values]
            
            
            if dtype == 'daily':
                for c in do.columns:
                    if 'wdir' in c:
                        #print('change windirection to deg')
                        #do.loc[:,c] = [compass2angle(d) for d in do.loc[:,c].values]
                        do.loc[:,c] =[ compass2angle(rep_text_wdir(d)) for d in do.loc[:,c].values]
            
            #====
            do = do.replace('///',np.NaN)
            do = do.replace('×',-999)
            
            for c in do.columns[:]: do[c] = pd.to_numeric(do[c], errors='coerce')
            
            # =======
            #----------
            # Save file
            path = opath+'/'+ dtype + '/'+block_no +'/'
            if not os.path.isdir(path): os.makedirs(path)
            
            if dtype == 'hourly': ofile = path+year+'_'+month+'_'+day+".csv"
            if dtype == 'daily': ofile = path+year+'_'+month+".csv"
            # =======
            do.to_csv(ofile, header=True, index=True, encoding='utf-8')
            # =======
            if len(do) > 1: print('dowloaded: ', contenturl)
            return do, contenturl
        else:
            print('\n Table does not exist \n')
    

    except:
        print('\n This page does not exist: \n Error: ')
#==============================================================================
#==============================================================================






def plot_hourly_temp_hum_wind(dat, odir='fig/'):
    
    date = dat.index[0]
    
    fig = plt.figure(figsize=(7, 3))
    
    ax = plt.axes([.1,.6,.7,.37])
    x = dat.index.hour.values #range(24) #dat.index
    x[-1] = 24
    c1 = 'orange'
    ax.plot(x,dat['temp_C'], color=c1,lw=1.5, clip_on=False) 
    ax.tick_params(axis='y', labelcolor=c1)
    ax.set_ylabel('Temperature ($^oC$)', color=c1,fontsize=9) 
    #ax.set_xlim(0,23.5)
    ax.set_ylim(int(dat['temp_C'].min() / 2)*2, int(dat['temp_C'].max() / 2+1)*2)
    plt.xticks([1,6,12,18,24],[1,6,12,18,24],fontsize=8)
    plt.yticks(fontsize=5)
    ax.grid(ls='--')
    ax.set_xlim(1,24)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_position(('axes', -.01))
    ax.spines['bottom'].set_position(('axes', -.05))
    plt.xticks(fontsize= 10)
    plt.yticks(fontsize= 10)
    
    #dat['temp_C'].plot(ax=ax,lw=1,c='r')
    ax2 = ax.twinx()
    ax2.spines['right'].set_position(('axes', 1.01))
    c1 = 'g'
    ax2.plot(x,dat['rh_percent'], c = c1,lw=1.5, clip_on=False)
    ax2.tick_params(axis='y', labelcolor=c1)
    ax2.set_ylabel('RH (%)', color=c1) 
    if dat['rh_percent'].min() < 40: ylim = (0,100)
    else: ax2.set_ylim(40,100)
    #dat['rh_percent'].plot(ax=ax2,lw=1,c='g')
    #df2.plot(ax=ax2)
    ax2.spines['left'].set_visible(False)
    
    
    ax3 = ax.twinx()
    ax3.spines['right'].set_position(('axes', 1.15))
    ax3.bar(x,dat['precip_mm'].values, color='royalblue', alpha=0.8)
    ax3.set_ylim(0,10)
    ax3.tick_params(axis='y', labelcolor='royalblue')
    ax3.set_ylabel('Precipitation (mm/hr)', color='royalblue') 
    for a in [ax,ax2,ax3]:
        a.spines['top'].set_visible(False)
    for a in [ax2, ax3]: a.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    #ax.set_xlim(0,24.5)
    
    #dat['precip_mm'].plot(ax=ax3 )
    #df3.plot(ax=ax3)
    
    
    
    #============================
    ax4 = plt.axes([.1,.17,.7,.22])
    c1 = 'y'
    ax4.plot(x,dat['wspd_ms'], color=c1,lw=1.5, clip_on=False)
    ax4.tick_params(axis='y', labelcolor=c1)
    ax4.set_ylabel('Wind speed (mm/s)', color=c1)     
    
    
    ax4.set_xlabel(date.strftime('%d %b %Y'), fontsize=14, fontweight='bold')
    
    
    #ax2 = ax.twinx()
    #ax2.plot(x,dat['wdir_deg'], color='orange')
    #ax2.set_ylim(-100,370)
    #ax2.set_yticks([0, 90, 180, 270, 360])
    #ax2.set_yticklabels(['N','E', 'S', 'W', 'N'], color='orange')
    ws, wd = dat['wspd_ms'].values, dat['wdir_deg'].values
    u, v = mpcalc.wind_components(ws * units('m/s'), wd * units.deg)
    
    qui = ax4.quiver(x, [0]*len(x) , u, v, width = .003,scale=50)
    plt.quiverkey(qui, 0.9, 1.05, 2, label='2 m/s', 
                  labelpos='E')
    
    ax4.set_ylim( - (int(ws.max()/2)+1)*2 , (int(ws.max()/2)+1) * 2)
    ax4.hlines(0,xmin=1,xmax=24,lw=0.2)
    plt.xticks([1,6,12,18,24],[1,6,12,18,24])
    ax4.set_xlim(1,24)
    ax4.grid(ls='--')
    for f in ['right', 'top']: ax4.spines[f].set_visible(False)
    
    ax4.spines['left'].set_position(('axes', -.01))
    ax4.spines['bottom'].set_position(('axes', -.05))
    
    
    #odir = 'fig/'+stn+'/'+dd.strftime('%Y-%m-%d')+'/' 
    if not os.path.exists(odir): os.makedirs(odir)
    plt.savefig(odir+'/temp-hum-wind.png', dpi=150)   



def plot_sounding(df,date,odir='fig/'):
    # plot sounding
    p = df.index.astype(float).values * units.hPa
    T = df['Temp(C)'].values * units.degC
    rh = df['RH(%)'].values * units('percent')  #/100  #* units.%
    
    Td = mpcalc.dewpoint_from_relative_humidity(T, rh)
    
    # Create a new figure. The dimensions here give a good aspect ratio
    fig = plt.figure(figsize=(7, 7))
    #add_metpy_logo(fig, 630, 80, size='large')
    
    # Grid for plots
    gs = gridspec.GridSpec(3, 3)
    #ax = plt.axes([.1,.1,.8,.8])
    skew = SkewT(fig, rotation=45, subplot=gs[:, :2])
    
    skew.plot(p, T, 'r', lw=2)
    skew.plot(p, Td, 'g', lw=2)
    
    # Good bounds for aspect ratio
    skew.ax.set_xlim(-30, 40)
    
    wd = df['WindDir(deg)'].values 
    ws = df['WindSpd(m/s)'].values / 1.9438444924406
    u, v = mpcalc.wind_components(ws * units('knots'), wd * units.deg)
    skew.plot_barbs(p, u, v)
    skew.ax.set_ylim(1000, 100)
    

    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    
    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    skew.plot(p, prof, 'k', linewidth=2)
    
    # Shade areas of CAPE and CIN
    #skew.shade_cin(p, T, prof) #, dewpoint= Td)
    skew.shade_cape(p, T, prof)
    
    # these are matplotlib.patch.Patch properties
    #props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    #props = dict( facecolor='wheat', alpha=0.5)
    # place a text box in upper left in axes coords
    cape, cin = mpcalc.cape_cin(p, T, Td, prof, which_lfc='bottom', which_el='top')
    text = 'LCL: '+'%.0f' % lcl_pressure.magnitude + ' (hPa)\n'+ \
           'CAPE: '+'%.0f' % cape.magnitude + ' (J/kg)\n'+ \
           'CIN: ' + '%.0f' % cin.magnitude + ' (J/kg)\n'
           
          
    skew.ax.text(1.2, 0.3, date.strftime('%Y %b %d %H:00'), 
                 transform=skew.ax.transAxes,
                 fontsize=12, verticalalignment='bottom', 
                 fontweight = 'bold'
                 #bbox=props
                 )
           
    skew.ax.text(1.25, 0.26, text, 
                 transform=skew.ax.transAxes,
                 fontsize=11, verticalalignment='top', 
                 #bbox=props
                 )
    
    
    
    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)
    
    
    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    
    
    # Create a hodograph
    ax = plt.axes([.74,.53,.25,.25]) #fig.add_subplot(gs[0, -1])
    h = Hodograph(ax, component_range=60.)
    h.add_grid(increment=20)
    h.plot(u, v)    
    
    if not os.path.exists(odir): os.makedirs(odir)
    #plt.savefig(odir+'/' + date.strftime('%Y-%b-%d_%H00.png'), dpi=150)
    plt.savefig(odir+'/skewp.png', dpi=150)
#==============================================================================
#==============================================================================






from matplotlib.image import imread
def grid(ax,st):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlines = False
    gl.ylines = False
    gl.xlocator = mticker.FixedLocator(np.arange(0,360,st))
    gl.ylocator = mticker.FixedLocator(np.arange(-90.,90,st))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size':10, 'color':'gray'}
    gl.ylabel_style = {'size':10, 'rotation':90, 'va':'center', 'color':'gray'}
    return ax




def plot_basemap():
    
    #land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
    #                                        edgecolor='face',
    #                                        facecolor=cfeature.COLORS['land'])

    bodr = cfeature.NaturalEarthFeature(category='cultural', 
        name='admin_0_boundary_lines_land', scale='10m', facecolor='none', alpha=0.7)
    
    
    proj =  ccrs.PlateCarree() #ccrs.Robinson(central_longitude=145)

    fig = plt.figure(figsize=(4, 4))
    ax = plt.axes(projection= proj )
    ax.set_extent([123,150,25, 49])
    ax.coastlines(resolution='10m',lw=.5)
    #ax.gridlines()
    ax.stock_img()
    
    #fname = os.path.join('/Users/doan/working/00_OBS_studies/Global/NE1_50M_SR_W', 'NE1_50M_SR_W.tif')
    
    fname = 'NE2_50M_SR_W/NE2_50M_SR_W.tif'
    if 1:
        ax.imshow(imread(fname), origin='upper', transform=proj, 
              extent=[-180, 180, -90, 90])
    
    #ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5,lw=.5)
    ax.add_feature(bodr, linestyle='-', edgecolor='k', alpha=.5, lw=.5)
    ax.outline_patch.set_linewidth(.5)
    
    return fig, ax
#==============================================================================









#==============================================================================
#==============================================================================
if __name__ == "__main__":
    point = '47646'
    point = '47662'
    point = '5' 
    
    
    
    amedas_file = 'Amedas_list.csv'
    alist = pd.read_csv(amedas_file, index_col=0)
    
    #=== SHimonita
    opath = 'data_download/' 
    point = '354'
    point = '47646'
    date = pd.Timestamp.now() - pd.Timedelta('1 day')  #pd.Timestamp(pd.datetime.now()) 
    
    
    date = pd.Timestamp('2022-02-01')
    
    dat, link = download_amedas(point, date, opath, 'hourly' )
    time.sleep(0.2)
    plot_hourly_temp_hum_wind(dat)
    #======
    sys.exit()

    
    
    
    
    points = ['5', '47646'] # hokkaido, tsukuba
    
    # plot     
    for point in points[1:]:
            
        stid = int(point)
        
        df = pd.read_csv('Amedas_list.csv').set_index('station_id')
        
        '''
        fig, ax = plot_basemap()
        r = df.loc[stid]
        
        clat, clon = r.latitude, r.longitude
        buf = 1
        ax.set_extent([clon -buf,clon +buf,clat -buf, clat + buf ])
        plt.text(clon,clat+0.1, r['station_name_roman'].replace('（',' (').replace('）',')'), 
                 va = 'bottom',ha = 'center',
                 fontsize=15)
        #         + ' ('+rr.country+')') #, transform = ax.transAxes, fontsize=10)
        plt.scatter(clon, clat, color='r',s=50, alpha=1, marker='s')
        grid(ax,.5)
        odir = 'fig/'+point+'/'
        if not os.path.exists(odir): os.makedirs(odir)
        plt.savefig(odir+'lct.png', dpi=100)   
        '''
    


    
    
    gmt = pd.Timedelta('9h')
    now = pd.Timestamp.now()  - gmt
    
    #date = now.floor(freq='12H') + gmt 
    opath = 'data_download/' 
    
        
    for point in points[1:]:
        #for dtype in ['hourly', 'daily'][:]:   
            
        #    da1 = download_amedas(point, date, opath, dtype)
        #    print(da1)    
                

        #==========GET ALL AMEDAS INFORMATION==========================================
        #https://www.jma.go.jp/jma/en/Activities/upper/upper.html

        kansho = [47401, 47412, 47418, 47582, 47600, 47646,
                  47678, 47741, 47778, 47807, 47827, 47909,
                  47918, 47945, 47971, 47991, 89532]
        
        if not int(point) in kansho: continue

        
        point =  '47646'
            
        data = get_data_sonde(point, date, opath)
        time.sleep(0.2)
        i = 0
        
        
        while len(data) == 0:
            data = get_data_sonde(point, date, opath+'/sonde/')
            time.sleep(0.2)
            date = date - pd.Timedelta('12h')
            i=i+1
            if i == 2: break
    
    
        print(data)
    
        df = data['noisuy']
        
        plot_sounding(df,date,odir='fig/')
        
        
        #dat, link = download_amedas(point, date, opath, 'hourly' )
        #time.sleep(0.2)
        #plot_hourly_temp_hum_wind(dat)
            
        

        







































        
        
        
        
        
        
        
        
        

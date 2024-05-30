import time, sys, glob, os
import pandas as pd
import requests
from bs4 import BeautifulSoup  # new to install
import numpy as np



#-------Header function---------------
def get_info(h,att):
    #if h.has_key(att): nu = int(h.get(att))
    if h.has_attr(att): nu = int(h.get(att))
    else: nu = 1
    return nu
#==========


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









#==============================================================================
#==============================================================================
if __name__ == "__main__":
    
    
    opath = 'data_download/' 
    
    # download each point for a given day
    if False:
        
        point = '47646' # Tsukuba station
        date = pd.Timestamp('2022-02-01')
    
        dat, link = download_amedas(point, date, opath, 'hourly' )
        time.sleep(0.2)
        
        from plot import plot_hourly_temp_hum_wind
        plot_hourly_temp_hum_wind(dat)
    
 
    
    # download each point for a given period
    if False:
        
        point = '47646' # Tsukuba station
    
        date_range = pd.date_range('1980-01-01', '2020-12-31', freq='d')
        for date in date_range:
            dat, link = download_amedas(point, date, opath, 'hourly' )
            time.sleep(0.2)
        
        
    if True:
        amedas_file = 'Amedas_list.csv'
        alist = pd.read_csv(amedas_file, index_col=0)   
        
        points = [str(s) for s in alist['station_id'].values]
        date_range = pd.date_range('2020-12-01', '2020-12-03', freq='d')
        
        for point in points[:2]:
            for date in date_range:
                dat, link = download_amedas(point, date, opath, 'hourly' )
                time.sleep(0.2)            
        
    
    
    
    
    
    
    

    


    
    
    
        
            
        

        







































        
        
        
        
        
        
        
        
        

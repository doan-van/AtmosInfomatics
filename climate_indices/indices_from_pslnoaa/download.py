##
import wget, os
import pandas as pd
import numpy as np



#wget.download('https://psl.noaa.gov/data/correlation/pna.data') #,    out='pna1.data')


#https://psl.noaa.gov/data/correlation/amon.sm.data
#https://psl.noaa.gov/data/correlation/amon.sm.long.data

vnames = [ 'pna', 'epo', 'wp', 'ea', 'nao', 'jonesnao', 
          'soi', 'nina3.anom', 'censo.long', 'tna', 'tsa',
          'whwp', 'oni', 'meiv2', 'nina1.anom', 'nina4.anom', 'nina34.anom', 
          'pdo', 'ipotpi.hadisst2', 'noi', 'np', 'tni', 'ao', 'aao', 'pacwarm', 
          'eofpac', 'atltri', 'amon.us', 'ammsst', 'NTA_ersst', 'CAR_ersst', 
          'amon.sm', 'amon.sm.long', 'qbo', 'glaam', 'espi', 'indiamon', 
          'sahelrain', 'swmonsoon', 'brazilrain', 'solar', 'gmsst', 'censo.long']

for vname in vnames[:]:
    
    if vname == 'ipotpi.hadisst2':
        wget.download('https://psl.noaa.gov/data/timeseries/IPOTPI/ipotpi.hadisst2.data')
    elif vname == 'ammsst':
        wget.download('https://psl.noaa.gov/data/timeseries/monthly/AMM/ammsst.data')
    elif vname == 'glaam':
        wget.download('https://psl.noaa.gov/data/correlation/glaam.data.scaled')
    else:
        wget.download('https://psl.noaa.gov/data/correlation/'+vname+'.data') 
      
    if vname == 'glaam': down_file = vname+'.data.scaled'
    else: down_file = vname+'.data'
    
    d = open(down_file).readlines()
    yy =  d[0].strip().split()
    mons = pd.date_range(yy[0], yy[1], freq='m')
    
    
    
    aa = [ a.split() for a in d]
    
    aax = [a for a in aa if len(a) == 13]
    if  vname == 'sahelrain':
        print('****')
        aax = aax[:-1]
        missval = -999.
    elif vname == 'gmsst':
        aax = aax[:-1]
        missval = 9999        
    else:
        missval = float(aa[[i for i, a in enumerate(aa) if len(a) == 13][-1]+1][0])
    
    print(vname, 'missing value: ', missval)
    df = pd.DataFrame(aax).set_index(0)
    cols = df.columns
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
    df.replace(missval,np.nan, inplace=True)
    
    
    df = df.stack(dropna = False).to_frame()
    ind = [ pd.to_datetime(i[0]+ '%.2d'% i[1]+'01' )  for i in df.index]
    
    df['date'] = ind
    df.set_index('date', inplace=True)
    df.columns = [vname]
    odir = 'timeseries/'
    if not os.path.isdir(odir): os.makedirs(odir)
    df.to_csv(odir + vname+'.csv')
    odir = 'raw_timeseries/'
    if not os.path.isdir(odir): os.makedirs(odir)
    os.system('mv '+down_file+' '+odir+'/')




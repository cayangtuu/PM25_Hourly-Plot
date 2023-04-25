import matplotlib as mpl
from pyproj import Transformer, CRS
from mpl_toolkits.basemap import Basemap
import pandas as pd
import numpy as np
import os, datetime, rasterio
from Lib import plot_nan

mpl.use('Agg')

def main():
    global workPath, IOPath, timeH, timeD, powerPlant

    ### 檔案資料夾
    workPath = "/path/to/working/folder"    # Enter your working Directory


    inputFil = pd.read_table(workPath + '/simen.inp', header = None)
    inDir  = inputFil.iloc[0,0]
    adjDir = inputFil.iloc[4,0]
    runDir = inputFil.iloc[5,0]
    powerPlant = inputFil.iloc[6,0]
    
#   IOPath = os.path.join(workPath, 'CALPOST7.1.0', 'public', 'result', inDir, adjDir)
    IOPath = os.path.join(runDir, inDir, adjDir)


    timemid = datetime.datetime.strptime(inputFil.iloc[1,0], '%Y%m%d%H') 
    timerange = [timemid-pd.Timedelta(24,'H'), timemid+pd.Timedelta(47,'H')]
    timeH = pd.date_range(timerange[0], timerange[1], freq='1H').strftime('%Y-%m-%d-%H')
    timeD = pd.date_range(timerange[0], timerange[1], freq='1D').strftime('%Y-%m-%d-%H')


    #執行程式
    PLOTTYPE
    #print('finished')

def Basic():
    ### GRDs檔之邊界與網格數讀取
    GrdFil = os.path.join(workPath, 'grdtitle.inp')
    src = pd.read_fwf(GrdFil, names=['MM', 'LL'])[1:]
    src.index = ['WH', 'Lon', 'Lat']
    src = src.astype('float')
      

    ### GRDs檔的座標轉換  twd97二分帶 -> twd97經緯度
    transformer = Transformer.from_crs(CRS("EPSG:3826"), CRS("EPSG:3824"))
    lllat,lllon = transformer.transform((src.loc['Lon','MM'])*1000, (src.loc['Lat','MM'])*1000)
    urlat,urlon = transformer.transform((src.loc['Lon','LL'])*1000, (src.loc['Lat','LL'])*1000)

    ### var的x,y座標(twd97經緯度)
    width  = int(src.loc['WH', 'MM'])
    height = int(src.loc['WH', 'LL'])
    ix= np.linspace(lllon, urlon, width)
    iy= np.linspace(lllat, urlat, height)

    ### TW地圖設定
    shpFil  = os.path.join(os.getcwd(), 'map', 'COUNTY_MOI_1090820')
    twmap = Basemap(llcrnrlon=lllon, llcrnrlat=lllat, urcrnrlon=urlon, urcrnrlat=urlat,
                    epsg=3824, resolution='f')
    return {'Bt':transformer, 'Bixiy':{'ix':ix, 'iy':iy}, 
            'Bg': [width, height], 'Bs':shpFil, 'Bmap':twmap} 



def Airplot(var):
    from Lib import plot_vars
    dataDir = os.path.join(IOPath, 'GRD')
    siteDir = os.path.join(IOPath, 'DATA', 'SITE')
    outDir  = os.path.join(IOPath, 'PLOT', 'JPG')

    #判斷資料夾內檔案數量是否正確
    DDAmt = (len([name for name in os.listdir(dataDir) \
              if os.path.isfile(os.path.join(dataDir, name))]))
    if (DDAmt == 579):
       State = 'yes'
    else:
       State = 'no'


    ### 設定檔案名稱 及 執行畫圖程式
    if (State == 'yes'):
       pp = plot_vars.Vars(Basic(), powerPlant)
       for tt in timeH:
           tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'
           dataFil = os.path.join(dataDir, tttxt + '_L00_' + var + '_1HR_CONC.GRD')
           siteFil = os.path.join(siteDir, tttxt + '_L00_Site.txt')

           #print(var + '   ' + tt)
           outfig = pp.mainplot(dataFil, siteFil, outDir, var, tt, 'hours')

       if (var == 'TPM2.5'):
          for tt in timeD:
              tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'
              dataFil = os.path.join(dataDir, tttxt + '_L00_' + var + '_24HR_CONC.GRD')

              # 將當日所有Site檔名放置於siteFil的list中
              def toFils(tt):
                  tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'
                  Fil = os.path.join(siteDir, tttxt + '_L00_Site.txt')
                  return Fil
              ttH = [t.strftime('%Y-%m-%d-%H') for t in pd.date_range(start=tt, periods=24,freq='H')]
              siteFil = list(map(toFils, ttH))

              #print(var + '   ' + tt)
              outfig = pp.mainplot(dataFil, siteFil, outDir, var, tt, 'days')
    else:
       pp = plot_nan.Vars(Basic(), powerPlant)
       for tt in timeH:
           tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'
           outfig = pp.vars_mainplot(outDir, var, tt, 'hours')
       if (var == 'TPM2.5'):
          for tt in timeD:
              tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'
              outfig = pp.vars_mainplot(outDir, var, tt, 'days')



def Metplot(type):
    from Lib import plot_winds, plot_mix

    dataDir = os.path.join(IOPath, 'DATA', 'MET')
    siteDir = os.path.join(IOPath, 'DATA', 'SITE')
    outDir  = os.path.join(IOPath, 'PLOT', 'JPG', 'MET')

    if (type == 'Winds'):
       DDAmt = (len([name for name in os.listdir(dataDir) \
                if os.path.isfile(os.path.join(dataDir, name)) \
                if name.endswith('.usp') or name.endswith('.vsp')]))
       if (DDAmt == 144):
          State = 'yes'
          pp = plot_winds.Vars(Basic(), powerPlant)
       else:
          State = 'no'
          pp = plot_nan.Vars(Basic(), powerPlant)

    elif (type == 'Mix'):
       DDAmt = (len([name for name in os.listdir(dataDir) \
                if os.path.isfile(os.path.join(dataDir, name)) \
                if name.endswith('.mix')]))
       if (DDAmt == 72):
          State = 'yes'
          pp = plot_mix.Vars(Basic(), powerPlant)
       else:
          State = 'no'
          pp = plot_nan.Vars(Basic(), powerPlant)

    ### 設定檔案名稱 及 執行畫圖程式
    if (State == 'yes'):
       for tt in timeH:
           tttxt = tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+'00(UTC+0800)'

           if (type == 'Winds'):
              #print('Winds' + '   ' + tt)
              dataFil = {'u':os.path.join(dataDir, tttxt + '_L01_1HR.usp'),
                         'v':os.path.join(dataDir, tttxt + '_L01_1HR.vsp')}
           elif (type == 'Mix'):
              #print('Mix' + '   ' + tt)
              dataFil = os.path.join(dataDir, tttxt + '_L00_1HR.mix')

           siteFil = os.path.join(siteDir, tttxt + '_L00_Site.txt')

           outfig = pp.mainplot(dataFil, siteFil, outDir, tt)

    else:
       for tt in timeH:
           if (type == 'Winds'):
              outfig = pp.winds_mainplot(outDir, tt)
           elif (type == 'Mix'):
              outfig = pp.mix_mainplot(outDir, tt)


if __name__ == '__main__':
    main()

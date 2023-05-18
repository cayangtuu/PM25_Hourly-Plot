import rasterio
import matplotlib as mpl
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import os 
from matplotlib.font_manager import FontProperties

zhfont = FontProperties(fname=os.getcwd()+'/Lib/wqy-microhei.ttc', size=18)

class Vars():
     def __init__(self, Basic, powerPlant):
         self.ixiy = Basic['Bixiy']
         self.grdnb = Basic['Bg']
         self.shpFil = Basic['Bs']
         self.twmap = Basic['Bmap']
         self.transformer = Basic['Bt']
         self.powerPlant = powerPlant

     ### colorbar的參數設定 ###
     def crs(self):
         bounds = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
         rgb = ([255,255,194], [255,243,175], [254,222,128], [254,183,81],
                [253,140,60], [252,78,42], [225,24,29], [188,0,38], [128,0,38])
         colorsmap=np.array(rgb)/255.0
         cmap=mpl.colors.ListedColormap(colorsmap[0:8])
         cmap.set_over(colorsmap[8])
         norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)
         return {'vb':bounds, 'vc':cmap, 'vn':norm}


     ###### 主要畫圖程式 ######
     def mainplot(self, dataFil, siteFil, outDir, tt):
         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20, 12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #self.twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=15)

         #畫contour圖
         src=rasterio.open(dataFil)
         df = np.flip(src.read(1),0)
         dfip, grid_lon, grid_lat = self.twmap.transform_scalar(df, self.ixiy['ix'], self.ixiy['iy'], \
                                    self.grdnb[1]*8, self.grdnb[0]*8, returnxy=True)
         im = self.twmap.pcolormesh(grid_lon, grid_lat, dfip, cmap=self.crs()['vc'], norm=self.crs()['vn'])
         CS = ax.contour(grid_lon, grid_lat, dfip, self.crs()['vb'], colors='gainsboro', linewidths=1.4)
         ax.clabel(CS, CS.levels, inline=True, fmt='%d', fontsize=9, colors='k')

         #畫電廠位置
         if (self.powerPlant == "Taichung"):
           powerLon, powerLat = [120.479653038959, 24.2138311519342]
           powerLabel = '台中電廠位置'
           powerBTA = (8/20, 11/12.5)
         elif (self.powerPlant == "Hsinta"):
           powerLon, powerLat = [120.20173, 22.853955]
           powerLabel = '興達電廠位置'
           powerBTA = (8/20, 2.5/12.5)
         plt.plot(powerLon, powerLat, marker='H', mfc='None', linestyle='None',\
                  mec='k', mew=3, markersize=18, label=powerLabel)
         plt.legend(bbox_to_anchor=powerBTA, prop=zhfont, frameon=False)

         #畫測站資料
         sitedf = pd.read_table(siteFil, sep='\s+')
         stx = sitedf['x']*1000
         sty = sitedf['y']*1000
         stlat, stlon = self.transformer.transform(stx.tolist(),sty.tolist())

         for ii in range(0, len(sitedf)):
             plt.plot(stlon[ii], stlat[ii], marker='^', color='darkblue', markersize=10)

         ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                      tt[11:13]+'00(UTC+0800)', fontsize=25)

         self.Index(fig, ax, im)
         self.Output(fig, outDir, tt)
         return 


     ###### colorbar,文字設置 ######
     def Index(self, fig, ax, im):
         if (self.powerPlant == "Taichung"):
           cax  = fig.add_axes([0.365,0.82,0.16,0.023])
           tx1 = fig.add_axes([0.365,0.85,0.13,0.005])
         elif (self.powerPlant == "Hsinta"):
           cax  = fig.add_axes([0.365,0.14,0.16,0.023])
           tx1 = fig.add_axes([0.365,0.17,0.13,0.005])

         #colorbar
         cbar = plt.colorbar(im, cax, ticks=self.crs()['vb'], 
                             orientation='horizontal', shrink=1, extend='max') 
         cbar.ax.set_xticklabels([str(txt) for txt in self.crs()['vb']])
         cbar.ax.tick_params(labelsize=10)
    
         #文字
         tx1.text(0, 0.1, u'混合層高度(m)', color='k', fontproperties=zhfont)
         tx1.set_axis_off()

         return


     ###### 輸出檔案 ######
     def Output(self, fig, outDir, tt):
         try:
             os.makedirs(outDir)
         except FileExistsError:
             pass
         outFil  = os.path.join(outDir, tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+
                                '00(UTC+0800)_L00_1HR_Mix.JPG')
         plt.savefig(outFil, bbox_inches='tight')
         plt.close(fig)
#        plt.show()
         return

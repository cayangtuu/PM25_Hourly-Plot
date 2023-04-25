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
         colorsmap = np.array([[201/255, 250/255, 202/255], [148/255, 212/255, 164/255], 
                               [95/255, 186/255, 168/255], 'yellow', 'orange',
                               'red', 'blueviolet'], dtype='object')
         cmap = mpl.colors.ListedColormap(colorsmap)
         cmap.set_over('maroon', 30)
         cmap.set_under('white', 0.01)
         bounds = [0.01, 0.1, 1, 3, 5, 10, 20, 30]
         norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)
         return {'vb':bounds, 'vc':cmap, 'vn':norm}

     ### 圖例的參數設定 ###
     def lbs(self):
         Labels = ['0 to 16', '16 to 36', '36 to 55', '55 to 151', '151 to 251', '251 to 500']
         colors  = ['green', 'yellow', 'orange', 'red', 'blueviolet', 'maroon']
         markers = ['o', 's', '^', '*', 'D', (6,1,0)]
         limits = [0, 15.5, 35.5, 54.5, 150.5, 250.5, 500]
         return {'vL':Labels, 'vc':colors, 'vm':markers, 'vl':limits}


     ###### 主要畫圖程式 ######
     def mainplot(self, dataFil, siteFil, outDir, var, tt, type):
         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20, 12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=10.5)

         #畫contour圖
         src=rasterio.open(dataFil)
         df = np.flip(src.read(1),0)
         dfip, grid_lon, grid_lat = self.twmap.transform_scalar(df, self.ixiy['ix'], self.ixiy['iy'], \
                                    self.grdnb[1]*8, self.grdnb[0]*8, returnxy=True)
         im = self.twmap.pcolormesh(grid_lon, grid_lat, dfip, cmap=self.crs()['vc'], norm=self.crs()['vn'])

         #畫電廠位置
         if (self.powerPlant == "Taichung"):
           powerLon, powerLat = [120.479653038959, 24.2138311519342]
         elif (self.powerPlant == "Hsinta"):
           powerLon, powerLat = [120.20173, 22.853955]
         plt.plot(powerLon, powerLat, marker='X', color='k', markersize=10)

         #畫測站資料
         def sitelatlon(sitedf):
            stx = sitedf['x']*1000
            sty = sitedf['y']*1000
            stlat, stlon = self.transformer.transform(stx.tolist(),sty.tolist())
            return stlat, stlon

         if (type == 'hours'):
            sitedf = pd.read_table(siteFil, sep='\s+')
            stlat, stlon = sitelatlon(sitedf)
            stpm = sitedf['PM2.5']
            stpm.replace([9999.0], np.NaN, inplace=True)
            stpm = stpm.tolist()

            ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                         tt[11:13]+'00(UTC+0800)', fontsize=25)

         elif (type == 'days'):
            stlat, stlon = sitelatlon(pd.read_table(siteFil[0], sep='\s+'))
            stpm = pd.DataFrame()
            for fil in siteFil:
               tmp = pd.read_table(fil, sep='\s+')
               stpm = pd.concat([stpm, tmp['PM2.5']], axis=1)
            stpm.replace([9999.0], np.NaN, inplace=True)
            stpm = round(stpm.mean(axis=1, skipna=True), 1)
            stpm = stpm.tolist()

            ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10], fontsize=25)

            # 畫出觀測值最大的位置
            stpm_imax = stpm.index(max(stpm))
            plt.plot(stlon[stpm_imax], stlat[stpm_imax], marker='o', \
                     color='gray', markeredgecolor='gray', markersize=18)
            maxlg = mpl.lines.Line2D([], [], marker='o', color='gray', linestyle='None',\
                             markersize=12, label='測站觀測最大值位置')
            if (self.powerPlant == "Taichung"):
                plt.legend(handles=[maxlg], bbox_to_anchor=(10/20, 8.5/12.5), \
                           prop=zhfont, frameon=False)
            elif (self.powerPlant == "Hsinta"):
                plt.legend(handles=[maxlg], bbox_to_anchor=(10/20, 5/12.5), \
                           prop=zhfont, frameon=False)


         for ii in range(0, len(stpm)):
             PM25  = stpm[ii]
             stLat = stlat[ii]
             stLon = stlon[ii]
             if (np.isnan(PM25)):
                plt.plot(stLon, stLat, marker='+', color='k', markeredgecolor='k', markersize=10)
             else:
                for kk in range(0, len(self.lbs()['vL'])):
                    if (PM25>=self.lbs()['vl'][kk]) and (PM25<self.lbs()['vl'][kk+1]):
                       plt.plot(stLon, stLat, marker=self.lbs()['vm'][kk], \
                                color=self.lbs()['vc'][kk], markeredgecolor='k', markersize=10)
                    else:
                       pass

         self.Index(fig, ax, im)
         self.Output(fig, outDir, var, tt, type)
         return 


     ###### colorbar,文字及圖例設置 ######
     def Index(self, fig, ax, im):
         if (self.powerPlant == "Taichung"):
           bbox_to_anchor = (0.4/20, 10.6/12.5)
           cax  = fig.add_axes([0.365,0.82,0.14,0.023])
           tx1 = fig.add_axes([0.365,0.85,0.11,0.005])
           tx2 = fig.add_axes([0.365,0.77,0.11,0.005])
         elif (self.powerPlant == "Hsinta"):
           bbox_to_anchor=(0.4/20, 3.3/12.5)
           cax  = fig.add_axes([0.365,0.31,0.14,0.023])
           tx1 = fig.add_axes([0.365,0.34,0.11,0.005])
           tx2 = fig.add_axes([0.365,0.26,0.11,0.005])

           
         #圖例
         Legends=[]
         for kk in range(0, len(self.lbs()['vL'])):
             style = mpl.lines.Line2D([], [], marker=self.lbs()['vm'][kk],
                     color=self.lbs()['vc'][kk], linestyle='None', 
                     markeredgecolor='k', markersize=12, label=self.lbs()['vL'][kk])
             Legends.append(style)
             plt.legend(handles=Legends, loc=2, bbox_to_anchor=bbox_to_anchor, 
                        prop={'size': 13}, edgecolor='k')


         #colorbar
         cbar = plt.colorbar(im, cax, ticks=self.crs()['vb'], 
                             orientation='horizontal', shrink=1, extend='both') 
         cbar.ax.set_xticklabels([str(txt) for txt in self.crs()['vb']])
         cbar.ax.tick_params(labelsize=12)

         #文字
         tx1.text(0, 0.1, u'網格模擬濃度($\mu$g/m$^3$)', 
                  color='k', fontproperties=zhfont)
         tx1.set_axis_off()

         plt.text(0, 0.1, u'測站觀測PM$_{2.5}$濃度($\mu$g/m$^3$)', 
                  color='k', fontproperties=zhfont)
         tx2.set_axis_off()

         return


     ###### 輸出檔案 ######
     def Output(self, fig, outDir, var, tt, type):
         outDist = os.path.join(outDir, var)
         try:
             os.makedirs(outDist)
         except FileExistsError:
             pass
         if (type == 'hours'):
            outFil  = os.path.join(outDist, tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+
                                   '00(UTC+0800)_L00_' + var + '_1HR_CONC.JPG')
         elif (type == 'days'):
            outFil  = os.path.join(outDist, tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+
                                   '00(UTC+0800)_L00_' + var + '_24HR_CONC.JPG')
         plt.savefig(outFil, bbox_inches='tight')
         plt.close(fig)
#        plt.show()
         return

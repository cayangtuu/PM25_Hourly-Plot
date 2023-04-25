import rasterio
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import os 
import matplotlib.patches as patches


class Vars():
     def __init__(self, Basic, powerPlant):
         self.ixiy = Basic['Bixiy']
         self.shpFil = Basic['Bs']
         self.twmap = Basic['Bmap']
         self.transformer = Basic['Bt']
         self.powerPlant = powerPlant


     ### 將風速風向轉換為U,V風場 ###
     def wsd2uv(self, stws, stwd):
         stuu=[]
         stvv=[]
         for ii in range(len(stwd)):
             m_wd = 270 - stwd[ii]
             p_wd = m_wd /180 *np.pi
             stuu.append(stws[ii] * np.cos(p_wd))
             stvv.append(stws[ii] * np.sin(p_wd))
         return np.array(stuu), np.array(stvv)

     ###### 主要畫圖程式 ######
     def mainplot(self, dataFil, siteFil, outDir, tt):
         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20,12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=15)

         #畫模擬風場圖
         df_u = np.flip(rasterio.open(dataFil['u']).read(1),0)
         df_v = np.flip(rasterio.open(dataFil['v']).read(1),0)
         ixx, iyy = np.meshgrid(self.ixiy['ix'], self.ixiy['iy'])

         mag = np.sqrt(df_u**2 + df_v**2)
#        nmag = (-1/36 * mag**2) + (3/4 * mag) + 10/36                # 10->2, 5->1.5, 1->1
#        nmag = (-70/5346 * mag**2) + (2453/5346 * mag) + 290/5346    # 10->3, 1->2.0, 0.1->1
         nmag = (-110/3528 * mag**2) + (1689/3528 * mag) + 185/3528   # 5.->3, 1->2.0, 0.1->1
          
         skip = (slice(None, None, 7), slice(None, None, 7))
         arr = ax.quiver(ixx[skip], iyy[skip], df_u[skip]/nmag[skip], df_v[skip]/nmag[skip], 
                         color='fuchsia', units='inches', scale=10., width=0.015, 
                         headwidth=8, pivot='mid', minlength=0.01)

         #畫電廠位置
         if (self.powerPlant == "Taichung"):
           powerLon, powerLat = [120.479653038959, 24.2138311519342]
         elif (self.powerPlant == "Hsinta"):
           powerLon, powerLat = [120.20173, 22.853955]
         plt.plot(powerLon, powerLat, marker='X', color='k', markersize=10)

         #畫測站資料
         sitedf = pd.read_table(siteFil, sep='\s+')
         stx = sitedf['x']*1000
         sty = sitedf['y']*1000
         stlat, stlon = self.transformer.transform(stx.tolist(), sty.tolist())
         stuu, stvv = self.wsd2uv(sitedf['ws'].tolist(), ((-1)*sitedf['wd(-1)']).tolist())

         stmag = np.sqrt(stuu**2 + stvv**2)
         stnmag = (-110/3528 * stmag**2) + (1689/3528 * stmag) + 185/3528   # 5.->3, 1->2.0, 0.1->1
         starr = ax.quiver(stlon, stlat, stuu/stnmag, stvv/stnmag,
                           color='k', scale=10, width=0.015, units='inches', pivot='mid')


         ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                      tt[11:13]+'00(UTC+0800)', fontsize=25)

         self.Index(fig, ax, arr)
         self.Output(fig, outDir, tt)
         return 


     ###### colorbar,文字及圖例設置 ######
     def Index(self, fig, ax, arr):
         if (self.powerPlant == "Taichung"):
           Rectangle = (119.85, 24.96)
           text = [119.875, 25.14]
           qk1_xy = [0.18, 0.89]
           qk2_xy = [0.07, 0.89]
         elif (self.powerPlant == "Hsinta"):
           Rectangle = (119.58, 21.72)
           text = [119.61, 21.9]
           qk1_xy = [0.18, 0.06]
           qk2_xy = [0.07, 0.06]

         #圖例
         ax.add_patch(patches.Rectangle(Rectangle, 0.3, 0.3, edgecolor = 'k', 
                      facecolor = 'w', fill=True))
         ax.text(text[0], text[1], '10M Wind\n   (m/s)', fontsize=15)

         qk1 = ax.quiverkey(arr, qk1_xy[0], qk1_xy[1], 784/135, r'10', labelpos='S',
                            color='fuchsia', coordinates='axes', fontproperties={'size':15})
         qk2 = ax.quiverkey(arr, qk2_xy[0], qk2_xy[1], 1, r'0.1', labelpos='S', 
                            color='fuchsia', coordinates='axes', fontproperties={'size':15})

         return

     ###### 輸出檔案 ######
     def Output(self, fig, outDir, tt):
         try:
             os.makedirs(outDir)
         except FileExistsError:
             pass
         outFil  = os.path.join(outDir, tt[0:4]+'_M'+tt[5:7]+'_D'+tt[8:10]+'_'+tt[11:13]+
                               '00(UTC+0800)_L01_1HR_Wind.JPG')
         plt.savefig(outFil, bbox_inches='tight')
         plt.close(fig)
#        plt.show()
         return

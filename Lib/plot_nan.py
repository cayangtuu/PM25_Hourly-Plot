import rasterio
import matplotlib as mpl
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import os
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties

zhfont = FontProperties(fname=os.getcwd()+'/Lib/wqy-microhei.ttc', size=18)

class Vars():
     def __init__(self, Basic, powerPlant):
         self.shpFil = Basic['Bs']
         self.twmap = Basic['Bmap']
         self.transformer = Basic['Bt']
         self.powerPlant = powerPlant

     ### Vars ###
     ###### 主要畫圖程式 ######
     def vars_mainplot(self, outDir, var, tt, type):

         # colorbar的參數設定 #
         colorsmap = np.array([[201/255, 250/255, 202/255], [148/255, 212/255, 164/255], 
                               [95/255, 186/255, 168/255], 'yellow', 'orange',
                               'red', 'blueviolet'], dtype='object')
         bounds = [0.01, 0.1, 1, 3, 5, 10, 20, 30]
         cmap = mpl.colors.ListedColormap(colorsmap)
         cmap.set_over('maroon', 30)
         cmap.set_under('white', 0.01)
         norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

         # 圖例的參數設定 #
         Labels = ['0 to 16', '16 to 36', '36 to 55', '55 to 151', '151 to 251', '251 to 500']
         colors  = ['green', 'yellow', 'orange', 'red', 'blueviolet', 'maroon']
         markers = ['o', 's', '^', '*', 'D', (6,1,0)]
         limits = [0, 15.5, 35.5, 54.5, 150.5, 250.5, 500]

         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20, 12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=10.5)

         #畫電廠位置
         if (self.powerPlant == "Taichung"):
           powerLon, powerLat = [120.479653038959, 24.2138311519342]
           powerLabel = '台中電廠位置'
           powerBTA = (8/20, 8.5/12.5)
         elif (self.powerPlant == "Hsinta"):
           powerLon, powerLat = [120.20173, 22.853955]
           powerLabel = '興達電廠位置'
           powerBTA = (8/20, 5/12.5)
         plt.plot(powerLon, powerLat, marker='H', mfc='None', linestyle='None',\
                  mec='k', mew=3, markersize=18, label=powerLabel)
         plt.legend(bbox_to_anchor=powerBTA, prop=zhfont, frameon=False)

         # colorbar,文字及圖例設置 #
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
         for kk in range(0, len(Labels)):
             style = mpl.lines.Line2D([], [], marker=markers[kk], color=colors[kk], 
                     linestyle='None', markeredgecolor='k', markersize=12, label=Labels[kk])
             Legends.append(style)
             plt.legend(handles=Legends, loc=2, bbox_to_anchor=bbox_to_anchor, 
                        prop={'size': 13}, edgecolor='k')

         #colorbar
         cbar = plt.colorbar(mpl.cm.ScalarMappable(norm, cmap), cax, ticks=bounds, 
                             orientation='horizontal', shrink=1, extend='both') 
         cbar.ax.set_xticklabels([str(txt) for txt in bounds])
         cbar.ax.tick_params(labelsize=12)
    
         #文字
         tx1.text(0, 0.1, u'網格模擬濃度($\mu$g/m$^3$)', color='k', fontproperties=zhfont)
         tx1.set_axis_off()

         plt.text(0, 0.1, u'測站觀測PM$_{2.5}$濃度($\mu$g/m$^3$)', color='k', fontproperties=zhfont)
         tx2.set_axis_off()

         # 標題 #
         if (type == 'hours'):
            ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                         tt[11:13]+'00(UTC+0800)', fontsize=25)
         elif (type == 'days'):
            ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10], fontsize=25)

         # 輸出檔案 #
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



     ### Mix ###
     ###### 主要畫圖程式 ######
     def mix_mainplot(self, outDir, tt):

         ### colorbar的參數設定 ###
         bounds = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
         rgb = ([255,255,194], [255,243,175], [254,222,128], [254,183,81],
                [253,140,60], [252,78,42], [225,24,29], [188,0,38], [128,0,38])
         colorsmap=np.array(rgb)/255.0
         cmap=mpl.colors.ListedColormap(colorsmap[0:8])
         cmap.set_over(colorsmap[8])
         norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20, 12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #self.twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=15)

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

         # colorbar及文字位置設置
         if (self.powerPlant == "Taichung"):
           cax  = fig.add_axes([0.365,0.82,0.16,0.023])
           tx1 = fig.add_axes([0.365,0.85,0.13,0.005])
         elif (self.powerPlant == "Hsinta"):
           cax  = fig.add_axes([0.365,0.14,0.16,0.023])
           tx1 = fig.add_axes([0.365,0.17,0.13,0.005])

         #colorbar
         cbar = plt.colorbar(mpl.cm.ScalarMappable(norm, cmap), cax, ticks=bounds,
                             orientation='horizontal', shrink=1, extend='max')
         cbar.ax.set_xticklabels([str(txt) for txt in bounds])
         cbar.ax.tick_params(labelsize=10)

         #文字
         tx1.text(0, 0.1, u'混合層高度(m)', color='k', fontproperties=zhfont)
         tx1.set_axis_off()

         #標題
         ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                      tt[11:13]+'00(UTC+0800)', fontsize=25)

         # 輸出檔案 #
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



     ### Winds ###
     ###### 主要畫圖程式 ######
     def winds_mainplot(self, outDir, tt):

         # 畫TW地圖
         fig, ax = plt.subplots(figsize = (20,12.5))
         self.twmap.readshapefile(self.shpFil, 'Taiwan', linewidth=1.0, drawbounds=True)
         #twmap.drawcoastlines()
         self.twmap.drawcountries(linewidth=15) 

         #畫電廠位置
         if (self.powerPlant == "Taichung"):
           powerLon, powerLat = [120.479653038959, 24.2138311519342]
           powerLabel = '台中電廠位置'
           powerBTA = (7.8/20, 10/12.5)
         elif (self.powerPlant == "Hsinta"):
           powerLon, powerLat = [120.20173, 22.853955]
           powerLabel = '興達電廠位置'
           powerBTA = (7.8/20, 3/12.5)
         plt.plot(powerLon, powerLat, marker='H', mfc='None', linestyle='None',\
                  mec='k', mew=3, markersize=18, label=powerLabel)
         plt.legend(bbox_to_anchor=powerBTA, prop=zhfont, frameon=False)
     
         #圖例
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

         ax.add_patch(patches.Rectangle(Rectangle, 0.3, 0.3, 
                      edgecolor = 'k', facecolor = 'w', fill=True))
         ax.text(text[0], text[1], '10M Wind\n   (m/s)', fontsize=15)

         X,Y = np.arange(-1,1,1)
         U, V = np.meshgrid(X,Y)
         arr = ax.quiver(X, Y, U, V,
                         color='white', units='inches', scale=10., width=0.015,
                         headwidth=8, pivot='mid', minlength=0.01)
         qk1 = ax.quiverkey(arr, qk1_xy[0], qk1_xy[1], 784/135, r'10', labelpos='S', 
                            color='fuchsia', coordinates='axes', fontproperties={'size':15})
         qk2 = ax.quiverkey(arr, qk2_xy[0], qk2_xy[1], 1, r'0.1', labelpos='S', 
                            color='fuchsia', coordinates='axes', fontproperties={'size':15})

         #標題
         ax.set_title(tt[0:4]+'/'+tt[5:7]+'/'+tt[8:10]+' '+
                      tt[11:13]+'00(UTC+0800)', fontsize=25)

         # 輸出檔案 #
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

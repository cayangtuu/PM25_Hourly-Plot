# PM25_Hourly-Plot
一個以python開發，使用matplotlib繪製中部/南部區域之calpuff模擬PM2.5逐時等濃度圖及觀測風速、混合層逐時圖。  
<br/>
### 所需工具
Linux
[Anaconda3](https://www.anaconda.com/download/)
### 安裝與執行步驟
1. 打開終端機(Terminal)，將專案clone至本機位置
```
$ git clone https://github.com/cayangtuu/PM25_Hourly-Plot.git
```
2. 進入專案資料夾
```
$ cd PM25_Hourly-Plot
```
3. 修改environment.yml檔案，將prefix路徑修改為anaconda環境路徑
```
prefix: /path/to/anaconda3/envs/pm25plot
```
4. 修改pm2.5plot.py檔案，將workPath修改為模擬結果資料夾路徑
```
workPath = "/path/to/working/folder"
```
5. 修改bashrc檔案，將pwdPath修改為當前資料夾路徑，且將CondaDIR修改為anaconda環境路徑
```
pwdPath=/path/to/current/folder
export CondaDIR=/path/to/anaconda3
```
6. 啟動Anaconda環境，啟動後終端機指令最前端將出現(bash)字樣
```
$ conda activate
```
7. 匯入啟動專案所需環境，完成後終端機指令最前端將出現(pm25plot)字樣
```
$ conda env create -f environment.yml
```
8. 執行程式
```
$ python pm25plot.py
```

### 作者
[Doranne](https://github.com/cayangtuu)

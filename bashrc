#!/bin/bash
pwdPath=/path/to/current/folder

#Anaconda
export CondaDIR=/path/to/anaconda3
export PATH=$CondaDIR/bin:$PATH

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('$CondaDIR/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "$CondaDIR/etc/profile.d/conda.sh" ]; then
        . "$CondaDIR/etc/profile.d/conda.sh"
    else
        export PATH="$CondaDIR/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate pm25plot

sed 's/PLOTTYPE/Airplot('\'NO3\'')/'    pm25plot.py > NO3_PLOT.py
sed 's/PLOTTYPE/Airplot('\'SO4\'')/'    pm25plot.py > SO4_PLOT.py
sed 's/PLOTTYPE/Airplot('\'PM2.5\'')/'  pm25plot.py > PM2.5_PLOT.py
sed 's/PLOTTYPE/Airplot('\'TPM2.5\'')/' pm25plot.py > TPM2.5_PLOT.py
sed 's/PLOTTYPE/Metplot('\'Winds\'')/'  pm25plot.py > Winds_PLOT.py
sed 's/PLOTTYPE/Metplot('\'Mix\'')/'    pm25plot.py > Mix_PLOT.py

python NO3_PLOT.py & python SO4_PLOT.py & \
python PM2.5_PLOT.py & python TPM2.5_PLOT.py & \
python Winds_PLOT.py & python Mix_PLOT.py
wait

/bin/rm -f NO3_PLOT.py SO4_PLOT.py PM2.5_PLOT.py TPM2.5_PLOT.py Winds_PLOT.py Mix_PLOT.py




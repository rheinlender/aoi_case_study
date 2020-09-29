#! /bin/bash
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

import os 
import sys
from glob import glob
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation
from IPython.display import HTML, Image
import cartopy.crs as ccrs

# inputs to animation
inpath ='/cluster/work/users/rheinlender/breakup2013/outputs/breakup2013.ERA5.r10.sticky_ice2/'
#inpath ='/cluster/work/users/rheinlender/breakup2013/outputs/breakup2013.ERA5.r10.Cair_0001/'
outpath_plots = '/cluster/work/users/rheinlender/plots/'
outname = outpath_plots+'sit_Jan-Mar_breakup2013.ERA5.r10.sticky_ice2.gif'

fl = sorted(glob(inpath+'Moorings*.nc'))
print('Opening files: ', *fl, sep = "\n") 

# Open multiple nc files
ds = xr.open_mfdataset(fl, concat_dim='time')

# Select data in Jan-Mar
subset = ds.sel(time=slice('2013-01-01', '2013-03-31'))

# compute daily average SIT 
sit_daily = subset.sit.groupby('time.dayofyear').mean(skipna=True)

# get daily time array
dates = subset['time'].groupby('time.dayofyear').mean()

# Create animation
print('create animation')

def make_figure():
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)  

    return fig, ax

fig, ax = make_figure();

frames = len(dates)        # Number of frames
#frames = 4        # test

# contour levels
clevs = np.arange(0.,3.2,0.2)

def draw(frame):
    var = sit_daily[frame].values
    im = ax.contourf(ds.x, ds.y, sit_daily[frame], clevs,
#                     add_colorbar=False,
                    )
    title = u"%s — %s" % (ds.sit.long_name, str(dates[frame].values)[:10])
    ax.set_title(title)

    return im

def init():
    im = ax.contourf(ds.x, ds.y, sit_daily[0], clevs,
                     #add_colorbar=True,
                    )
    title = u"%s — %s" % (ds.sit.long_name, str(dates[0].values)[:10])
    ax.set_title(title)
    
    add_colorbar(fig, ax, im)
    
    return im 

def add_colorbar(fig, ax, im):
    return fig.colorbar(im, ax=ax, label='[m]')

def animate(frame):
   # ax.clear()
    ax.collections = []  
    return draw(frame)

ani = animation.FuncAnimation(fig, animate, frames, interval=0.01, blit=False,
                              init_func=init, repeat=False)

ani.save(outname, writer='imagemagic', fps=3);

plt.close(fig)

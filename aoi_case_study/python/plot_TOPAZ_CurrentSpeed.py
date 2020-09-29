#! /bin/bash
import cmocean
import cartopy
import matplotlib as plt
import os
import numpy as np
from pynextsim.gmshlib import GmshMesh

import mod_netcdf_utils as mnu
import pynextsim.gridding as png
from pynextsim.netcdf_list import NetcdfList
from pynextsim.irregular_grid_interpolator import IrregularGridInterpolator
import matplotlib.pyplot as plt
from pynextsim.nextsim_bin import NextsimBin
from pynextsim.openers import OpenerVariable, Opener, ProjectionInfo
import datetime as dt
import pynextsim.lib as nsl

from string import Template


# Define functions
class GmshMeshX(GmshMesh):
    def get_grid(self, resolution=10000):
        """
        Parameters:
        -----------
        resolution : float
            resolution in metres

        Returns:
        --------
        grid : pynextsim.gridding.Grid
        """
        return png.Grid.init_from_grid_params(
                dict(
                    xmin = self.boundary.xmin-100000,
                    xmax = self.boundary.xmax,
                    ymin = self.boundary.ymin,
                    ymax = self.boundary.ymax+100000,
                    nx = int(np.ceil((self.boundary.xmax - self.boundary.xmin)/resolution)),
                    ny = int(np.ceil((self.boundary.ymax - self.boundary.ymin)/resolution)),
                    ))

# create TOPAZ opener
class OpenerTopaz4(Opener):
    name = 'TOPAZ4'
    name_mask = 'TOPAZ4/198910_201512/TP4DAILY_%Y%m_30m.nc'
    
    # variables
    variables = dict(
            uvel = OpenerVariable('u'), 
            vvel = OpenerVariable('v'),
            ssh = OpenerVariable('ssh'),
            )
    averaging_period = 1 # daily average

    #def __init__(self, forecast_start_date):
    #    self.name_mask = 'TOPAZ4/198910_201512/TP4DAILY_' + forecast_start_date.strftime('TOPAZ4/198910_201512/TP4DAILY_%Y%m%d_30m.nc')
     #   self.forecast_start_date = forecast_start_date

    @property
    def projection(self):
        '''
        TOPAZ/hyc2proj projection
        '''
        return ProjectionInfo.topaz_np_stere()
    
    
# get TOPAZ data

# input
start = dt.datetime(2013,1,20)
end = dt.datetime(2013,3,21)
delta = end - start

meshfile = os.path.join(os.getenv('NEXTSIM_MESH_DIR'), 'medium_arctic_10km.msh')
plot_res = 10 #km

# get target grid
gmsh = GmshMeshX(meshfile)
grid = gmsh.get_grid(resolution=plot_res*1000)

bbox=[-3499800.489225414, 3691904.3194155763, -4178720.947330964, 2721150.5288251294]

for i in range(delta.days + 1):
    data = []
    dto=start + dt.timedelta(days=i)
    print('Date is: ' + dto.strftime("%Y-%m-%d"))

    for varname in ['u', 'v']:
        op = OpenerTopaz4()
        f=op.find(dto)
        nci = mnu.nc_getinfo(f)
        tind = nci.datetimes.index(dto)
        data += [grid.get_netcdf_data(nci, vlist=[varname], time_index=tind)[varname]]
 
    spd = np.hypot(*data) 
    
    
    # Plot current speed 
    cmap = cmocean.cm.speed
    fig, ax = grid.plot(spd.data*100, cmap=cmap, add_landmask=True, 
                    land_color='grey',
                    land_zorder=1,
                    land_opacity=1,
                    clabel='Current Speed [cm/s]',
                    title=dto, 
                    format='%.0f', 
                    clim=[0,30])
    ax.coastlines(resolution='50m', linewidth=0.5)
    x = grid.xy[0][::10,::10] 
    y = grid.xy[1][::10,::10]
    u = data[0][::10,::10]
    v = data[1][::10,::10]
    u, v = nsl.rotate_lonlat2xy(grid.projection, x, y, u, v)
    #ax.quiver(x, y, u, v, units='xy', angles='xy', color='r')
    #ax.streamplot(x, y, u, v, linewidth=2, density=2)

    # save figure
    outpath_plots = '/cluster/home/rheinlender/projects/aoi_case_study/python/plots/'
    figname = outpath_plots+'TOPAZ4_CurrentSpeed_'+ dto.strftime("%Y-%m-%d")+'.png'
    fig.savefig(figname, dpi=150, bbox_inches='tight')    
        

#! /bin/bash
import os
import numpy as np
from string import Template
import datetime as dt
from matplotlib import pyplot as plt

from pynextsim.gmshlib import GmshMesh
from pynextsim.gridding import Grid
from pynextsim.openers import OpenerVariable, Opener
import mod_netcdf_utils as mnu
import pynextsim.lib as nsl

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
        return Grid.init_from_grid_params(
                dict(
                    xmin = self.boundary.xmin-100000,
                    xmax = self.boundary.xmax,
                    ymin = self.boundary.ymin,
                    ymax = self.boundary.ymax+100000,
                    nx = int(np.ceil((self.boundary.xmax - self.boundary.xmin)/resolution)),
                    ny = int(np.ceil((self.boundary.ymax - self.boundary.ymin)/resolution)),
                    ))

class OpenerEra5(Opener):

    name = 'ERA5'
    name_mask = Template('ERA5/ERA5_${varname}_y%Y.nc')
    varname = 'Atm. forcing'
    variables = dict()
    averaging_period = 0 # snapshots

    def __init__(self, varname):
        self.name_mask = self.name_mask.safe_substitute(dict(varname=varname))
        self.varname = varname
        self.variables = {
                varname : OpenerVariable(varname), #can set any scale and offset here
                }
         
# input
start = dt.datetime(2013,1,20)
end = dt.datetime(2013,3,21)
delta = end - start

#dto = dt.datetime(2013,2,1)
meshfile = os.path.join(os.getenv('NEXTSIM_MESH_DIR'), 'medium_arctic_10km.msh')
plot_res = 10 #km

# get target grid
gmsh = GmshMeshX(meshfile)
grid = gmsh.get_grid(resolution=plot_res*1000)

# Plot wind speed and vectors
for i in range(delta.days + 1):
    data = []
    dto=start + dt.timedelta(days=i)
    print('Date is: ' + dto.strftime("%Y-%m-%d"))
    
    for varname in ['u10', 'v10']:
        # get source file
        op = OpenerEra5(varname)
        f = op.find(dto) # filename for date if it exists
        nci = mnu.nc_getinfo(f)
        tind = nci.datetimes.index(dto)
        data += [grid.get_netcdf_data(nci, vlist=[varname], time_index=tind)[varname]]

    spd = np.hypot(*data) # wind speed
    
    print('Start plotting...')
    kw = dict(figsize=(6,6), clabel='Wind Speed [m/s]', clim=(0,25), title=dto, format='%5.2f')
    fig, ax = grid.plot(spd, cmap='RdYlBu_r', add_landmask=False, **kw)
    ax.coastlines(resolution='50m')
    x = grid.xy[0][::10,::10] 
    y = grid.xy[1][::10,::10]
    u = data[0][::10,::10]
    v = data[1][::10,::10]
    u, v = nsl.rotate_lonlat2xy(grid.projection, x, y, u, v)
    ax.quiver(x, y, u, v, units='xy', angles='xy', color='r')
   
    # save figure
    outpath_plots = '/cluster/home/rheinlender/projects/aoi_case_study/python/plots/era5/'
    figname = outpath_plots+'ERA5_Winds_'+ dto.strftime("%Y-%m-%d")+'.png'
    fig.savefig(figname, dpi=150, bbox_inches='tight') 

    
    
    
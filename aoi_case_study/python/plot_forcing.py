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
                    xmin = self.boundary.xmin,
                    xmax = self.boundary.xmax,
                    ymin = self.boundary.ymin,
                    ymax = self.boundary.ymax,
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

#should be inputs
varname = 'msl'
dto = dt.datetime(2013,2,1)
meshfile = os.path.join(os.getenv('NEXTSIM_MESH_DIR'), 'medium_arctic_10km.msh')
plot_res = 10 #km

# get target grid
gmsh = GmshMeshX(meshfile)
grid = gmsh.get_grid(resolution=plot_res*1000)

if 0:
    #scalar field

    # get source file
    op = OpenerEra5(varname)
    f = op.find(dto) # filename for date if it exists
    nci = mnu.nc_getinfo(f)
    tind = nci.datetimes.index(dto)
    data = grid.get_netcdf_data(nci, vlist=[varname], time_index=tind)[varname]
    fig, ax = grid.plot(data, cmap='viridis', add_landmask=False)
    ax.coastlines(resolution='50m')
    fig.show()
else:
    #wind
    data = []
    for varname in ['u10', 'v10']:
        # get source file
        op = OpenerEra5(varname)
        f = op.find(dto) # filename for date if it exists
        nci = mnu.nc_getinfo(f)
        tind = nci.datetimes.index(dto)
        data += [grid.get_netcdf_data(nci, vlist=[varname], time_index=tind)[varname]]

    spd = np.hypot(*data) 
    fig, ax = grid.plot(spd, cmap='viridis', add_landmask=False)
    ax.coastlines(resolution='50m')
    x = grid.xy[0][::10,::10] 
    y = grid.xy[1][::10,::10]
    u = data[0][::10,::10]
    v = data[1][::10,::10]
    u, v = nsl.rotate_lonlat2xy(grid.projection, x, y, u, v)
    ax.quiver(x, y, u, v, units='xy', angles='xy', color='r')


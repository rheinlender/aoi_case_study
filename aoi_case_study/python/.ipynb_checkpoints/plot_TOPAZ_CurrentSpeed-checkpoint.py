{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "#! /bin/bash\n",
    "import cmocean\n",
    "import cartopy\n",
    "import matplotlib as plt\n",
    "import os\n",
    "import numpy as np\n",
    "from pynextsim.gmshlib import GmshMesh\n",
    "\n",
    "import mod_netcdf_utils as mnu\n",
    "import pynextsim.gridding as png\n",
    "from pynextsim.netcdf_list import NetcdfList\n",
    "from pynextsim.irregular_grid_interpolator import IrregularGridInterpolator\n",
    "import matplotlib.pyplot as plt\n",
    "from pynextsim.nextsim_bin import NextsimBin\n",
    "from pynextsim.openers import OpenerVariable, Opener, ProjectionInfo\n",
    "import datetime as dt\n",
    "import pynextsim.lib as nsl\n",
    "\n",
    "from string import Template\n",
    "\n",
    "\n",
    "# Define functions\n",
    "class GmshMeshX(GmshMesh):\n",
    "    def get_grid(self, resolution=10000):\n",
    "        \"\"\"\n",
    "        Parameters:\n",
    "        -----------\n",
    "        resolution : float\n",
    "            resolution in metres\n",
    "\n",
    "        Returns:\n",
    "        --------\n",
    "        grid : pynextsim.gridding.Grid\n",
    "        \"\"\"\n",
    "        return png.Grid.init_from_grid_params(\n",
    "                dict(\n",
    "                    xmin = self.boundary.xmin-100000,\n",
    "                    xmax = self.boundary.xmax,\n",
    "                    ymin = self.boundary.ymin,\n",
    "                    ymax = self.boundary.ymax+100000,\n",
    "                    nx = int(np.ceil((self.boundary.xmax - self.boundary.xmin)/resolution)),\n",
    "                    ny = int(np.ceil((self.boundary.ymax - self.boundary.ymin)/resolution)),\n",
    "                    ))\n",
    "\n",
    "# create TOPAZ opener\n",
    "class OpenerTopaz4(Opener):\n",
    "    name = 'TOPAZ4'\n",
    "    name_mask = 'TOPAZ4/198910_201512/TP4DAILY_%Y%m_30m.nc'\n",
    "    \n",
    "    # variables\n",
    "    variables = dict(\n",
    "            uvel = OpenerVariable('u'), \n",
    "            vvel = OpenerVariable('v'),\n",
    "            ssh = OpenerVariable('ssh'),\n",
    "            )\n",
    "    averaging_period = 1 # daily average\n",
    "\n",
    "    #def __init__(self, forecast_start_date):\n",
    "    #    self.name_mask = 'TOPAZ4/198910_201512/TP4DAILY_' + forecast_start_date.strftime('TOPAZ4/198910_201512/TP4DAILY_%Y%m%d_30m.nc')\n",
    "     #   self.forecast_start_date = forecast_start_date\n",
    "\n",
    "    @property\n",
    "    def projection(self):\n",
    "        '''\n",
    "        TOPAZ/hyc2proj projection\n",
    "        '''\n",
    "        return ProjectionInfo.topaz_np_stere()\n",
    "    \n",
    "    \n",
    "# get TOPAZ data\n",
    "\n",
    "# input\n",
    "start = dt.datetime(2013,1,20)\n",
    "end = dt.datetime(2013,3,21)\n",
    "delta = end - start\n",
    "\n",
    "meshfile = os.path.join(os.getenv('NEXTSIM_MESH_DIR'), 'medium_arctic_10km.msh')\n",
    "plot_res = 10 #km\n",
    "\n",
    "# get target grid\n",
    "gmsh = GmshMeshX(meshfile)\n",
    "grid = gmsh.get_grid(resolution=plot_res*1000)\n",
    "\n",
    "bbox=[-3499800.489225414, 3691904.3194155763, -4178720.947330964, 2721150.5288251294]\n",
    "\n",
    "for i in range(delta.days + 1):\n",
    "    data = []\n",
    "    dto=start + dt.timedelta(days=i)\n",
    "    print('Date is: ' + dto.strftime(\"%Y-%m-%d\"))\n",
    "\n",
    "    for varname in ['u', 'v']:\n",
    "        op = OpenerTopaz4()\n",
    "        f=op.find(dto)\n",
    "        nci = mnu.nc_getinfo(f)\n",
    "        tind = nci.datetimes.index(dto)\n",
    "        data += [grid.get_netcdf_data(nci, vlist=[varname], time_index=tind)[varname]]\n",
    " \n",
    "    spd = np.hypot(*data) \n",
    "    \n",
    "    \n",
    "    # Plot current speed \n",
    "    cmap = cmocean.cm.speed\n",
    "    fig, ax = grid.plot(spd.data*100, cmap=cmap, add_landmask=True, \n",
    "                    land_color='grey',\n",
    "                    land_zorder=1,\n",
    "                    land_opacity=1,\n",
    "                    clabel='Current Speed [cm/s]',\n",
    "                    title=dto, \n",
    "                    format='%.0f', \n",
    "                    clim=[0,30])\n",
    "    ax.coastlines(resolution='50m', linewidth=0.5)\n",
    "    x = grid.xy[0][::10,::10] \n",
    "    y = grid.xy[1][::10,::10]\n",
    "    u = data[0][::10,::10]\n",
    "    v = data[1][::10,::10]\n",
    "    u, v = nsl.rotate_lonlat2xy(grid.projection, x, y, u, v)\n",
    "    #ax.quiver(x, y, u, v, units='xy', angles='xy', color='r')\n",
    "    #ax.streamplot(x, y, u, v, linewidth=2, density=2)\n",
    "\n",
    "    # save figure\n",
    "    outpath_plots = '/cluster/home/rheinlender/projects/aoi_case_study/python/plots/'\n",
    "    figname = outpath_plots+'TOPAZ4_CurrentSpeed_'+ dto.strftime(\"%Y-%m-%d\")+'.png'\n",
    "    fig.savefig(figname, dpi=150, bbox_inches='tight')    \n",
    "        "
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

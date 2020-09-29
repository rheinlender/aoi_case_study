## List of experiments for the AOI case study of the March sea ice break-up event 


# breakup2013.ERA5.r10 (i.e. ctrl run)

Simulation with Nextsim at 10km resolution (small_arctic_10km). Initialized with CS2-SMOS (v2.0) ice thickness and concentration. The simulation starts in 2012-Nov-15 and ends in 2013-Apr-01 (duration of 137 days). 

Atmospheric forcing is ERA5 (30km resolution)

PARAMETER SETTING:
- Clab=3E6
- Pmax=10E3
- Cair=0.002

# breakup2013.ERA5.r5 (i.e. high res. ctrl run)
Same as above but run at 5km resolution in the sea ice model (NextSim). 

## Tuning 

# Breakup2013.r10.era5_v2

Same as the ctrl run but initialized with CS2SMOS_v2.0 from 2013-01-01. This ensures a better fit to observations at the start of the breakup. In particular, the gradient in ice thickness between Northern Greenland and Point Barrow - i.e. thinner ice along the Alaskan Coast (although still too much compared to CS2SMOS). 

# breakup2013.r10.era5.Cair_0001
similar to ctrl, but ERA5_quad_drag_coef_air is reduced from 0.002 to 0.001

The goal is to prevent thick sea from forming along the Alaskan coast due to ice convergence/divergence  

# breakup2013.r10.era5.Cair_0001_v2
similar to ctrl, but with ERA5_quad_drag_coef_air=0.001 and ocean_drag_coef reduced from 0.0055 to 0.0045. 

The goal is to test the impact of the ocean forcing on fracture location   


# breakup2013.r10.era5.sticky_ice

New ctrl run to test if we can get closer to the observed fracturing. In particular, arch shaped fractures forming at Point Barrow and propagating westward. 

Clab (ice cohesion) is increased to 4.5
Pmax reduced to 5. 
air_drag_coef set to 0.0018
 
# breakup2013.r10.era5.sticky_ice2

same as "sticky_ice" but Clab=5.5 and Pmax=10 (default). This increases the cohesion of the ice, but allows ridging more easily. 

# breakup2013.r10.era5.const_ice

Model initialized with constant ice thickness (1m) and concentration (1) defined by a mask where SST < 2 deg C (IceType::Constant). Default values are set in `options.cpp`
The goal of the simulation is to test if the initial ice thickness matters for the location of the breakup, i.e. biased towards Banks Island rather than Point Barrow.

# breakup2013.r10.era5.topaz_atrest

Same as `breakup2013.r10.era5_v2` but with constant ocean forcing to test if the flow field in TOPAZ is the reason for the wrong location of breakup. 

# breakup2013.r10.era5.cpom

Same as `breakup2013.r10.era5_v2` but with `currents_from_altimeter` (ocean-type=topaz_altimeter) from `Armitage et al., 2017: Arctic geostrophic currents`. 
Compared to "observations" (Armitage et al. 2017) the Beaufort circulation is likely too strong in TOPAZ, which may cause ice to breakup in the wrong place.


## Sensitivity experiments

To test the impact of atmospheric resolution on sea ice break-up we perform a series of sensitivity experiments. 

# breakup2013.WRF_r10.r10
Simulation using the atmospheric forcing from  WRF downscalled to 10km.  This is branched from the ctrl and starts from 2013-02-10 and ends 2013-03-10 (28 days). 

  

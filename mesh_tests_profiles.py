# to run: checkout yt branch, rebuild (since the change is in a .pyx file),
# run this file then copy output to ./on_main or ./on_new (or change the 
# ddir appropriately) 

import yt
import os
from yt.testing import (
    fake_random_ds,
    fake_hexahedral_ds,
    fake_tetrahedral_ds,
    small_fake_hexahedral_ds,
)
import numpy as np

ddir = "."  
fields = ("density", "temperature", "velocity_x", "velocity_y", "velocity_z", "mass")
units = ("g/cm**3", "K", "cm/s", "cm/s", "cm/s", "g")
for ds_type in (fake_random_ds,
    fake_hexahedral_ds):
    
    if ds_type is fake_random_ds: 
        test_ds = ds_type(16, fields=fields, units=units)
        ph_fields = [
             [("gas", "density"), ("gas", "temperature"), ("gas", "mass")],
            [("gas", "density"), ("gas", "velocity_x"), ("gas", "mass")],
            [("index", "radius"), ("gas", "temperature"), ("gas", "velocity_magnitude")],]
        wt_field = ("gas", "mass")
        regions = [test_ds.region([0.5] * 3, [0.4] * 3, [0.6] * 3), test_ds.all_data()]
        
    else: 
        test_ds = ds_type(fields=fields)
        test_ds.force_periodicity()
        ph_fields = [
             [("connect1", "density"), ("connect1", "temperature"), ("connect1", "mass")],
             [("connect1", "density"), ("connect1", "velocity_x"), ("connect1", "mass")],]
        wt_field= ("connect1", "mass")
        regions = [test_ds.region([0.5] * 3, [0.4] * 3, [0.6] * 3), test_ds.all_data()]
        
    
    phases = []
    for ireg, reg in enumerate(regions):
        for x_field, y_field, z_field in ph_fields:
            # set n_bins to [16, 16] since matplotlib's postscript
            # renderer is slow when it has to write a lot of polygons
            phases.append(
                yt.PhasePlot(reg, x_field, y_field, z_field, x_bins=16, y_bins=16, weight_field=wt_field)
            )
            phases.append(
                yt.PhasePlot(
                    reg,
                    x_field,
                    y_field,
                    z_field,
                    fractional=True,
                    accumulation=True,
                    x_bins=16,
                    y_bins=16, 
                    weight_field=wt_field
                )
            )
            p2d = yt.create_profile(reg, [x_field, y_field], z_field, n_bins=[16, 16], weight_field=wt_field)
            phases.append(yt.PhasePlot.from_profile(p2d))
            binned_array = p2d.field_data[z_field]

            fld_str = "_".join([f"{'_'.join(i_field).replace(' ', '_')}" for i_field in (x_field, y_field, z_field)])
            svname = os.path.join(ddir, f"profile2d_array_{ds_type.__name__}_{ireg}_{fld_str}")
            print(f"saving {svname}")
            np.save(svname, binned_array)

        
        
pp = yt.PhasePlot(
    test_ds.all_data(),
    ("gas", "density"),
    ("gas", "temperature"),
    ("gas", "mass"),
)
pp.set_xlim(0.3, 0.8)
pp.set_ylim(0.4, 0.6)
pp._setup_plots()
phases.append(pp)
phases[0]._repr_html_()
for idx, plot in enumerate(phases):
    test_prefix = f"PhasePlot_{plot.plots.keys()}_{idx}"
    plot.save(os.path.join(ddir, test_prefix))
    
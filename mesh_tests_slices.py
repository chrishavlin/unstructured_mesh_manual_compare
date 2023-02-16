# to run: checkout yt branch, rebuild (since the change is in a .pyx file),
# run this file then copy output to ./on_main or ./on_new (or change the 
# ddir appropriately) 

import yt
import os
from yt.testing import (
    # fake_amr_ds,
    fake_hexahedral_ds,
    fake_tetrahedral_ds,
    small_fake_hexahedral_ds,
)
import numpy as np

ddir = "."

for ds_type in (fake_hexahedral_ds, fake_tetrahedral_ds, small_fake_hexahedral_ds):

    ds = ds_type()
    ad = ds.all_data()


    for field in ds.field_list:
        for idir in [0, 1, 2]:
            for annotate in (True, False):
                prefix = f"{ds_type.__name__}_{field[0]}_{field[1]}_{idir}_{int(annotate)}"
                sl = yt.SlicePlot(ds, idir, field)
                if annotate:
                    sl.annotate_mesh_lines()
                sl.set_log("all", False)
                sl.save(os.path.join(ddir, prefix))

                im_vals = sl.frb[field].to_ndarray()
                np.save(os.path.join(ddir, prefix), im_vals)





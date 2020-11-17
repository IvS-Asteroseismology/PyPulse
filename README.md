# PyPulse

A custom-made python package compatible with anaconda, python 3.7 version.
Contains useful functions to make figures, MESA/GYRE grids, and help with data analysis.

This directory should be included in your anaconda installation in the following folder:
$CONDA_PREFIX/lib/python3.7/site-packages/  \
Be sure that $CONDA_PREFIX is set to your conda installation, this should be the case if you ran conda init when installing conda.

This repository is an open-source package, GNU-licensed, and any improvements provided by the users are well accepted. See GNU License in LICENSE.

### Note for contributors
Please submit pull requests to the developer branch instead of the master branch.
The master branch will be updated from time to time when possible conflicts between different pull requests have been resolved.

## contents

1. `pipeline`: Pipeline for the asteroseismic modelling of a star, using the functions within the files in this directory.
1. `templates`: A number of template files; GYRE inlists, bash scripts, VSC submit files.
1. `LICENSE`: GNU general public license
2. `functions_for_gyre.py`: Helpful functions for GYRE input and output.
3. `functions_for_mesa.py`: Helpful functions to process MESA output.
4. `grid_building_slurm.py`: Functions for building MESA and GYRE grids on the SLURM framework.
5. `grid_building_vsc.py`: Functions for building MESA and GYRE grids on the VSC framework.
6. `grid_building_vsc_multiprocess.py`: Same as `grid_building_vsc.py`, but utilising multiprocessing.
7. `lambda.csv`: List with lambda (eigenvalue of laplace tidal equations) and nu (spin parameter) for modes up to degree 3. (TAR approximation)
8. `maximum_likelihood_estimator.py`: Functions to perform different kinds of maximum likelihood estimation for the models in a grid, and make correlation plots.
9. `my_python_functions.py` : Helpful functions in general. Making figures, reading HDF5, processing strings.

### Author
Developed by Mathias Michielsen
```
mathias.michielsen@kuleuven.be
Instituut voor Sterrenkunde
KU Leuven, Belgium
```

### Contributors
May Gade Pedersen, Cole C. Johnston, Jordan Van Beeck

"""Ignore all the models that fall outside an n-sigma spectroscopic error box."""
import glob
from pathlib import Path
import pandas as pd
from foam import maximum_likelihood_estimator as mle
from foam import modelGrid as mg
from foam.pipeline.pipelineConfig import config
################################################################################
# Copy of the list of models, and keep only the models that fall within the specified spectroscopic error box
if config.n_sigma_spectrobox != None:
    observations = config.observations

    params = list(config.free_parameters) # To make a copy and not remove Xc from the config
    params.remove('Xc')
    summary = mg.gridSummary(params)

    if not Path('isocloud_grid.h5').is_file():
        summary.create_summary_file(config.isocloud_grid_directory, columns=['star_age','log_L','log_Teff','log_g'], magnitudes=False, output_name='isocloud_grid.h5', file_ending='hist', files_directory_name='history')
    else:
        print('read sum')
        summary.read_summary_file('isocloud_grid.h5')
        print('done reading')

    isocloud_summary_dict = {}
    for Z in summary.Z_array:
        isocloud_summary_dict.update({Z:{}})
    for Z in summary.Z_array:
        for M in summary.M_array:
            df_MZ = pd.DataFrame()
            for logD in summary.logD_array:
                for aov in summary.aov_array:
                    for fov in summary.fov_array:

                        df = pd.DataFrame( data = summary.grid_data[f'{Z:.3f}'][f'{M:.2f}'][f'{logD:.2f}'][f'{aov:.3f}'][f'{fov:.3f}'])
                        df_MZ = pd.concat([df_MZ, df], ignore_index=True)
            isocloud_summary_dict[Z].update({M : df_MZ })

    for grid in config.grids:
        files = glob.glob(f'extracted_freqs/{config.star}_{grid}*.hdf')
        for file in files:
            output_file = f'{config.n_sigma_spectrobox}sigmaSpectro_{file}'
            if not Path(output_file).is_file():
                mle.spectro_constraint(file, observations, nsigma=config.n_sigma_spectrobox, spectroGrid_file=f'{config.main_directory}/../grid_summary/spectroGrid_{grid}.hdf',
                                    spectro_companion=config.spectro_companion, isocloud_grid_summary=isocloud_summary_dict)
            else:
                config.logger.warning(f'file already existed: {output_file}')

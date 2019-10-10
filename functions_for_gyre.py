# A few helpful functions for GYRE input and output.
# from PyPulse import functions_for_gyre as ffg
import numpy as np
import glob, os
from . import read
from . import my_python_functions as mypy
import pandas
################################################################################
def ledoux_splitting(frequencies, betas, Mstar, Rstar, omega=0, m=1):
    """
    Calculate rotationally shifted frequencies. Aerts 2010, eq 3.357
    ------- Parameters -------
    frequencies, betas: numpy array of floats
        frequency values (cyc/day) en beta values (eq 3.357, Aerts 2010)
    Mstar, Rstar, omega: float
        stellar mass (g), radius (cm) and rotation frequency in units of critical velocity (omega_crit)
    m: int
        azimuthal order

    ------- Returns -------
    shifted_freqs: numpy array of floats
        frequency values as shifted by the ledoux splitting
    """

    G = 6.67428E-8 # gravitational constant (g^-1 cm^3 s^-2)
    omega_crit = (1/(2*np.pi))*(8*G*Mstar/(27*Rstar**3))**0.5
    omega_cycday = omega*omega_crit*86400 # rotation frequency in units of cyc/day

    shifted_freqs = frequencies-m*omega_cycday*(1-betas)
    return shifted_freqs

################################################################################
def calc_scanning_range(gyre_file_path, npg_min=-50, npg_max=-1, l=1, m=1, omega_rot=0.0):
    """
    Calculate the frequency range for the sought radial orders of the g modes. (for non-rotating case)
    ------- Parameters -------
    gyre_file_path: string
        absolute path to the gyre file that needs to be scanned
    n_min, n_max: integer
        lower and upper values of the required range in radial order
    l, m: integer
        degree (l) and azimuthal order (m) of the modes
    omega_rot: float
        rotation frequency of the model [c/d]

    ------- Returns -------
    f_min, f_max: float
        lower and upper bound of frequency range that needs to be scanned in oder
        to retrieve the required range of radial orders
    """
    directory, gyre_file = mypy.split_line(gyre_file_path, 'gyre/')
    Xc_file = float(mypy.substring(gyre_file, 'Xc', '.GYRE'))
    hist_file = glob.glob(f'{directory}*.hist')[0]
    dic_hist  = read.read_multiple_mesa_files([hist_file], is_hist=True, is_prof=False)[0]
    data      = dic_hist['hist']
    P0_values = data['Asymptotic_dP']
    Xc_values = data['center_h1']

    # get the asymptotic period spacing value at the Xc value of the gyre file
    diff = abs(Xc_file - Xc_values)
    xc_index = np.where(diff == np.min(diff))[0]
    P0 = P0_values[xc_index][0]

    # calculate the scanning range a bit broader than the purely asymptotic values, just to be safe.
    n_max_used = abs(npg_min-3)
    n_min_used = abs(min(-1, npg_max+3))

    if omega_rot==0:
        f_min = np.sqrt(l*(l+1)) / (n_max_used*P0)
        f_max = np.sqrt(l*(l+1)) / (n_min_used*P0)
    else:
        # Make a pandas dataframe
        df = pandas.read_csv(os.path.expandvars('$CONDA_PREFIX/lib/python3.7/site-packages/PyPulse/lambda.csv'), sep=',')
        # select nu (Spin parameter) and Lambda (eigenvalues) column when values in l and m column correspond to requested values
        NuLambda = df.loc[(df['l'] == l) & (df['m'] == m)][['nu', 'Lambda']]

        nu = NuLambda['nu'].to_numpy()
        Lambda = NuLambda['Lambda'].to_numpy()

        diff_max = nu/(2.*omega_rot) - P0*n_max_used/np.sqrt(Lambda)
        diff_min = nu/(2.*omega_rot) - P0*n_min_used/np.sqrt(Lambda)
        index_max = np.where(abs(diff_max) == np.min(abs(diff_max)))[0]
        index_min = np.where(abs(diff_min) == np.min(abs(diff_min)))[0]
        f_min = (np.sqrt(Lambda[index_max]) / (P0*n_max_used) + m*omega_rot)[0]
        f_max = (np.sqrt(Lambda[index_min]) / (P0*n_min_used) + m*omega_rot)[0]
    return f_min, f_max

################################################################################
################################################################################
# Functions adapted from Cole Johnston
################################################################################
def chisq_longest_sequence(tperiods,orders,operiods,operiods_errors):
    """
    Method made by Cole to extract the theoretical pattern that best matches the observed one

    ------- Parameters -------
    tperiods, orders : list of floats, integers
        theroretical periods and their radial orders
    operiods, operiods_errors : list of floats
        observational periods and their errors

    ------- Returns -------
    series_chi2: float
        chi2 value of the selected theoretical frequencies
    final_theoretical_periods: np array of floats
        the selected theoretical periods that best match the observed pattern
    corresponding_orders: list of integers
        the radial orders of the returned theoretical periods
    """
    if len(tperiods)<len(operiods):
        return 1e16, [-1. for i in range(len(operiods))], [-1 for i in range(len(operiods))]
    else:
        # Generate two series
        dP,e_dP = generate_obs_series(operiods,operiods_errors)
        deltaP  = generate_thry_series(tperiods)

        # Find the best matches per observed period
        pairs_orders = []
        for ii,period in enumerate(operiods):
            chisqs = np.array([ ( (period-tperiod)/operiods_errors[ii] )**2 for tperiod in tperiods  ])

            ## Locate the theoretical frequency (and accompanying order) with the best chi2
            min_ind = np.where( chisqs == min( chisqs ) )[0]
            best_match = tperiods[min_ind][0]
            best_order = orders[min_ind][0]

            ## Toss everything together for bookkeeping
            pairs_orders.append([period,best_match,int(best_order),chisqs[min_ind]])

        pairs_orders = np.array(pairs_orders)

        plt.figure(1,figsize=(6.6957,6.6957))
        plt.subplot(211)
        plt.plot(pairs_orders[:,0],pairs_orders[:,1],'o')
        plt.ylabel('$\\mathrm{Period \\,[d]}$',fontsize=20)
        plt.subplot(212)
        plt.plot(pairs_orders[:,0],pairs_orders[:,2],'o')
        plt.ylabel('$\\mathrm{Radial \\, Order}$',fontsize=20)
        plt.xlabel('$\\mathrm{Period \\,[d]}$',fontsize=20)

        # plt.show()


        sequences = []
        ## Look through all pairs of obs and theoretical frequencies and
        ## check if the next obs freqency has a corresponding theoretical frequency
        ## with the consecutive radial order
        current = []
        lp = len(pairs_orders[:-1])
        for ii,sett in enumerate(pairs_orders[:-1]):
            if abs(sett[2]) == abs(pairs_orders[ii+1][2])+1:
                current.append(sett)
            else:
               	current.append(sett)
                sequences.append(np.array(current).reshape(len(current),4))
                current = []
            if (ii==lp-1):
                current.append(sett)
                sequences.append(np.array(current).reshape(len(current),4))
                current = []
        len_list = np.array([len(x) for x in sequences])
        longest = np.where(len_list == max(len_list))[0] #[0]

        ## Test if there really is one longest sequence
        if len(longest) == 1:
            lseq = sequences[longest[0]]

        ## if not, pick, of all the sequences with the same length, the best based on chi2
        else:
            scores = [ np.sum(sequences[ii][:,-1])/len(sequences[ii]) for  ii in longest]
            min_score = np.where(scores == min(scores))[0][0]
            lseq = sequences[longest[min_score]]

        obs_ordering_ind = np.where(operiods == lseq[:,0][0])[0][0]
        thr_ordering_ind = np.where(tperiods == lseq[:,1][0])[0][0]

        ordered_theoretical_periods   = []
        corresponding_orders          = []

        thr_ind_start = thr_ordering_ind - obs_ordering_ind
        thr_ind_current = thr_ind_start

        for i,oper in enumerate(operiods):
            thr_ind_current = thr_ind_start + i
            if (thr_ind_current < 0):
                tper = -1
                ordr = -1
            elif (thr_ind_current >= len(tperiods)):
                tper = -1
                ordr = -1
            else:
                tper = tperiods[thr_ind_current]
                ordr = orders[thr_ind_current]
            ordered_theoretical_periods.append(tper)
            corresponding_orders.append(ordr)

        #final_theoretical_periods = np.sort(np.hstack([ordered_theoretical_periods_a,ordered_theoretical_periods_b]))[::-1]
        final_theoretical_periods = np.array(ordered_theoretical_periods)

        obs_series,obs_series_errors = generate_obs_series(operiods,operiods_errors)
        thr_series = generate_thry_series(final_theoretical_periods)

        obs_series        = np.array(obs_series)
        obs_series_errors = np.array(obs_series_errors)
        thr_series        = np.array(thr_series)

        series_chi2 = np.sum( (obs_series-thr_series)**2 /obs_series_errors**2 ) / len(obs_series)
        # print 'orders: %i - %i'%(corresponding_orders[0],corresponding_orders[-1])

        fig = plt.figure(2,figsize=(6.6957,6.6957))
        fig.suptitle('$\mathrm{Longest \\ Sequence}$',fontsize=20)
        axT = fig.add_subplot(211)
        # axT.errorbar(operiods[1:],obs_series,yerr=obs_series_errors,marker='x',color='black',label='Obs')
        # axT.plot(final_theoretical_periods[1:],thr_series,'rx-',label='Theory')
        axT.errorbar(list(range(len(obs_series))),obs_series,yerr=obs_series_errors,marker='x',color='black',label='Obs')
        axT.plot(list(range(len(thr_series))),thr_series,'rx-',label='Theory')
        axT.set_ylabel('$\mathrm{Period \\ Spacing \\ (s)}$',fontsize=20)
        axT.legend(loc='best')
        axB = fig.add_subplot(212)
        axB.errorbar(operiods[1:],obs_series-thr_series,yerr=obs_series_errors,marker='',color='black')
        axB.set_ylabel('$\mathrm{Residuals \\ (s)}$',fontsize=20)
        axB.set_xlabel('$\mathrm{Period \\ (d^{-1})}$',fontsize=20)
        axB.text(0.75,0.85,'$\chi^2 = %.2f$'%series_chi2,fontsize=15,transform=axB.transAxes)

        plt.show()

        for ii,oper in enumerate(operiods):
            print((oper, final_theoretical_periods[ii], corresponding_orders[ii]))

        series_chi2 = np.sum( ( (obs_series-thr_series) /obs_series_errors )**2 ) / len(obs_series)
        return series_chi2,final_theoretical_periods,corresponding_orders

################################################################################
def generate_obs_series(periods,errors):
    """
    Generate the observed period spacing series (delta P = p_n - p_(n+1) )
    ------- Parameters -------
    periods, errors: list of floats
        observational periods and their errors in units of days
    ------- Returns -------
    observed_spacings, observed_spacings_errors: list of floats
        period spacing series (delta P values) and its errors in untits of seconds
    """
    observed_spacings        = []
    observed_spacings_errors = []
    for kk,prd_k in enumerate(periods[:-1]):
        prd_k_p_1 = periods[kk+1]
        observed_spacings.append( abs( prd_k - prd_k_p_1 )*86400. )
        observed_spacings_errors.append(np.sqrt( errors[kk]**2 + errors[kk+1]**2  )*86400.)
    return observed_spacings,observed_spacings_errors

################################################################################
def generate_thry_series(periods):
    """
    Generate the theoretical period spacing series (delta P = p_n - p_(n+1) )
    ------- Parameters -------
    periods: list of floats
        theoretical periods in units of days
    ------- Returns -------
    theoretical_spacings: list of floats
        period spacing series (delta P values) in units of seconds
    """
    theoretical_spacings = []
    for kk,prd_k in enumerate(periods[:-1]):
        prd_k_p_1 = periods[kk+1]
        theoretical_spacings.append( abs(prd_k-prd_k_p_1)*86400. )
    return theoretical_spacings

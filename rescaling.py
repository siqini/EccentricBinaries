import numpy as np
import h5py
from pycbc import types 
import lal

def rescale (simulation_path, total_mass, real, new_time_interval = 1.0/4096):
    rh_file = simulation_path 
    rh_data = h5py.File(rh_file, 'r')

    idx = 'Extrapolated_N4.dir/Y_l2_m2.dat'
    ret_time = rh_data[idx][:,0]
    rh = rh_data[idx][:,1] + 1j*rh_data[idx][:,2]
    rh_data.close()
    if real:
        rh_reals = np.real(rh)
    else: 
        rh_reals = np.imag(rh)

    scaler = lal.MTSUN_SI

    factor = scaler*total_mass 

    rescaled_ret_time = ret_time*factor 
    ret_time_len = len(rescaled_ret_time)
    delta_num = ret_time_len-1


    t0 = np.amin(rescaled_ret_time)
    tf = np.amax(rescaled_ret_time)
    t_range = tf-t0
    sample_num = int((t_range/new_time_interval)) + 2

    new_y_values = []
    squared_rescaled_time = []
    for i in range(0, sample_num):
        if (i <= (sample_num-2)):
            ti = t0 + i*new_time_interval
            diffs = abs(rescaled_ret_time - ti)
            matched_ind = np.argmin(diffs)
            y_value = rh_reals[matched_ind]
            new_y_values.append(y_value)
            squared_rescaled_time.append(ti)
        else:
            ti = tf
            y_value = rh_reals[len(rh_reals)-1]
            new_y_values.append(y_value)
            squared_rescaled_time.append(ti)

    new_y_values = np.asarray(new_y_values)
    squared_rescaled_time = np.asarray(squared_rescaled_time)

    sp = types.timeseries.TimeSeries(initial_array = new_y_values, delta_t = new_time_interval)
    return sp

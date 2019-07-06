import argparse
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pycbc
import pycbc.psd
import h5py
import sys

parser = argparse.ArgumentParser(description='Compute matches between non-ecc injections and non-ecc template bank')
parser.add_argument('-t', '--templates', type=str, required=True, dest='tbank_filename', help='filename of the template bank')
parser.add_argument('-p', '--psd', type=str, required=True, dest='psd_filename',help='filename of psd')
parser.add_argument('-b', '--batch', type=int, required=True, dest='batch_num')
args = parser.parse_args()

start = datetime.now()
print ("Start time: %s" % start)



def GenTemplate (mass1, mass2, apx, ecc, lan, inc, f_low=30., freq_step=4):
    hptilde,hctilde = get_fd_waveform(approximant=apx,
                           mass1=mass1,
                           mass2=mass2,
                           eccentricity = ecc,
                           long_asc_nodes = lan,
                           inclination = inc,
                           f_lower=f_low,
                           delta_f=1.0/freq_step)
    return hptilde

# Generate injections
# Mass range: 1.1-1.6
# f_low = 30 (default)
# apx = "TaylorF2" (default)

masses2 = masses1 = np.linspace(1.1, 1.6, num=10)




# Grab non-eccentric template bank, COMMENT OUT FOR NOW

f_necc = h5py.File(args.tbank_filename, 'r')
necc_mass1 = f_necc['mass1'][:]
necc_mass2 = f_necc['mass2'][:]
necc_apx = f_necc['approximant'][:]




"""
GetMatch
Input: template0 injection waveform (restricted to one polarization)
       template1 template waveform (restricted to one polarization)
       psd_file string (default to "H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt")
       f_low float
Output: match between these two waveforms, float
"""

def GetMatch (template0,template1, psd_file =args.psd_filename, f_low=30):
    #resize two templates
    flen = max(len(template0),len(template1))
    #template1=template1.copy()
    template1.resize(flen)
    #template0=template0.copy()
    template0.resize(flen)

    #grab and use the psd file
    #df = 1.0/template1.duration
    my_psd = pycbc.psd.read.from_txt(filename = psd_file,
                                    length = flen,
                                    delta_f = 1.0/4,
                                    low_freq_cutoff = f_low,
                                    is_asd_file = False)

    #calculate match
    m,i = match(template0,template1,psd=my_psd,low_frequency_cutoff=f_low)
    return m

"""
GetGlobalMatch
Input: i_waveform0, j_waveform0 int double index of the injection waveform (restricted to one polarization)
       tp_apx list of strs
       tp_m1, tp_m2, tp_ecc, tp_lan, temp_inc np.array of float
       searching_radius float (only iterate through templates within a closed ball of mchirp of the injection;
                               given as a percentage of mchirp of the injection)
       f_low float threshold frequency
Output: maximum match in the bank for the given injection waveform0, float
"""

def GetGlobalMatch(i_waveform0, j_waveform0, tp_apx, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc, searching_radius, f_low=30.):
    waveform0_m1 = masses1[i_waveform0]
    waveform0_m2 = masses2[j_waveform0]
    waveform0_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(waveform0_m1, waveform0_m2) #compute mchirp of waveform0
    waveform0 = GenTemplate(mass1=waveform0_m1, mass2=waveform0_m2,
                           apx = 'TaylorF2',
                           ecc = 0.,
                           lan = 0.,
                           inc = 0.,
                           f_low = 30,
                           freq_step = 4)
    local_matches = np.zeros(len(tp_m1))
    rev_temp_counter = 0
    #iterate through the given template bank
    for k in range(0,len(tp_m1)):
        this_tp_m1 = tp_m1[k]
        this_tp_m2 = tp_m2[k]
        this_tp_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(this_tp_m1, this_tp_m2) #compute mchirp of one template
        diff_mchirp = abs(waveform0_mchirp-this_tp_mchirp)
        prozent_diff = diff_mchirp/waveform0_mchirp
        if (prozent_diff > searching_radius):
            local_matches[k] = 0.
        else:
            # generate templates as needed
            rev_temp_counter += 1
            one_relevant_temp = GenTemplate(mass1 = this_tp_m1, mass2 = this_tp_m2, apx = tp_apx[k],
                                                   ecc = tp_ecc[k], lan = tp_lan[k],
                                                   inc = tp_inc[k], f_low=30, freq_step=4)
            one_local_match = GetMatch(waveform0, one_relevant_temp)
            local_matches[k] = one_local_match
    global_match = np.amax(local_matches)
    return global_match


inj_counter = 0
# iterate through all injections
print ("inj_num, inj_mass1, inj_mass2, fitting_factor")
this_inj_mass1 = masses1[args.batch_num]
for j in range(0,len(masses2)):
    inj_counter += 1
    #print ("Injection number: %s" % inj_counter)
    this_global_match = GetGlobalMatch(i_waveform0 = args.batch_num,
                                        j_waveform0 = j,
                                        tp_apx = necc_apx,
                                        tp_m1 = necc_mass1,
                                        tp_m2 = necc_mass2,
                                        tp_ecc = np.zeros(len(necc_mass1)),
                                        tp_lan = np.zeros(len(necc_mass1)),
                                        tp_inc = np.zeros(len(necc_mass1)),
                                        searching_radius = 0.05)
    this_inj_mass2 = masses2[j]
    print ("%d, %f, %f, %f" % (inj_counter, this_inj_mass1, this_inj_mass2, this_global_match))
    


end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)

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

f_ecc = h5py.File(args.tbank_filename, 'r')
ecc_mass1 = f_ecc['mass1'][:]
ecc_mass2 = f_ecc['mass2'][:]
ecc_eccentricity = f_necc['eccentricity'][:]
ecc_lan = f_ecc['long_asc_nodes'][:]
ecc_inc = f_ecc['inclination'][:]
ecc_apx = np.empty(len(ecc_mass1), object)
for i_apx in range(0, len(ecc_apx)):
    ecc_apx[i_apx] = 'EccentricFD'





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
    print ("injection mass 1: %s" % waveform0_m1)
    print ("injection mass 2: %s" % waveform0_m2)
    waveform0_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(waveform0_m1, waveform0_m2) #compute mchirp of waveform0
    print ("injection mchirp: %s" % waveform0_mchirp)
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
            if rev_temp_counter ==1:
                print ("First relevant counter found at k= %s " %k)
                print ("With mass1 = %s" % this_tp_m1)
                print ("With mass2 = %s" % this_tp_m2)
                print ("With mchirp = %s" % this_tp_mchirp)
                print ("With percentage mchirp difference = %s" % prozent_diff)
                print ("With match = %s" % one_local_match)
            print ("This is a nice template: %s" % k)
            print ("This local match is: %s" % local_matches[k])
    global_match = np.amax(local_matches)
    return global_match


global_matches = np.empty([len(masses1), len(masses2)])
inj_counter = 0
# iterate through all injections
for i in range(0,len(masses1)):
    if i == 5:
        first_qtr_runtime = datetime.now()-start
        print ("Halfway through! It took us %s" % first_qtr_runtime)
    for j in range(0,len(masses2)):
        inj_counter += 1
        print ("Injection number: %s" % inj_counter)
        this_global_match = GetGlobalMatch(i_waveform0 = i,
                                           j_waveform0 = j,
                                           tp_apx = ecc_apx,
                                           tp_m1 = necc_mass1,
                                           tp_m2 = necc_mass2,
                                           tp_ecc = ecc_eccentricity,
                                           tp_lan = ecc_lan,
                                           tp_inc = ecc_inc,
                                           searching_radius = 0.05)
        global_matches[i][j] = this_global_match
        print ("Fitting factor: %s" % this_global_match)

#coutour plot
fig = plt.figure()
plt.contourf(masses1,masses2,global_matches, cmap="plasma")
plt.colorbar()
plt.xlabel('mass 1 (solar mass)')
plt.ylabel('mass 2 (solar mass)')
plt.title('Fitting factor contour plot for 10*10 non-eccentric injections with the eccentric template bank')
fig.savefig('ecc_contour.png')
end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)

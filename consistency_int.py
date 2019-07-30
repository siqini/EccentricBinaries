import argparse
from pycbc.waveform import get_fd_waveform
from pycbc.filter.matchedfilter import match
import numpy as np
from datetime import datetime
import pycbc
import pycbc.psd
import h5py

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--templates', type=str, required=True, dest='tbank_filename', help='filename of the template bank')
parser.add_argument('-p', '--psd', type=str, required=True, dest='psd_filename',help='filename of psd')
# injection parameter space
parser.add_argument('--mass_min', type=float, required=True, dest='mass_min')
parser.add_argument('--mass_max', type=float, required=True, dest='mass_max')
parser.add_argument('--mass_num', type=int, required=True, dest='mass_num')
parser.add_argument('--ecc_min', type=float, required=False, dest='ecc_min', default=0.)
parser.add_argument('--ecc_max', type=float, required=False, dest='ecc_max', default=0.)
parser.add_argument('--ecc_num', type=int, required=False, dest='ecc_num', default=1)
parser.add_argument('--lan_min', type=float, required=False, dest='lan_min', default=0.)
parser.add_argument('--lan_max', type=float, required=False, dest='lan_max', default=0.)
parser.add_argument('--lan_num', type=int, required=False, dest='lan_num', default=1)
parser.add_argument('--inc_min', type=float, required=False, dest='inc_min', default=0.)
parser.add_argument('--inc_max', type=float, required=False, dest='inc_max', default=0.)
parser.add_argument('--inc_num', type=int, required=False, dest='inc_num', default=0.)
parser.add_argument('--radius', type=float, required=True, dest='radius')
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

# Grab injection parameter space info
injection_apx = 'EccentricFD'
masses2 = masses1 = np.linspace(args.mass_min, args.mass_max, num=args.mass_num)
eccs = np.linspace(args.ecc_min, args.ecc_max, num=args.ecc_num)
lans = np.linspace(args.lan_min, args.lan_max, num=args.lan_num)
incs = np.linspace(args.inc_min, args.inc_max, num=args.inc_num)
tot_inj = ((args.mass_num)**2)*args.ecc_num*args.lan_num*args.inc_num
print ('Total injection number: %d' % tot_inj)

# Grab info from the template bank, and slice it up 
f_bank = h5py.File(args.tbank_filename, 'r')
bank_mass1 = f_bank['mass1'][:]
bank_mass2 = f_bank['mass2'][:]
bank_ecc = f_bank['eccentricity'][:]
bank_lan = f_bank['long_asc_nodes'][:]
bank_inc = f_bank['inclination'][:]
bank_apx = f_bank['approximant'][:]

f_bank.close()



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

def GetGlobalMatch(i_waveform0, j_waveform0, waveform0_apx, ecc_index0, lan_index0, inc_index0, tp_apx, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc, searching_radius, f_low=30.):
    waveform0_m1 = masses1[i_waveform0]
    waveform0_m2 = masses2[j_waveform0]
    waveform0_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(waveform0_m1, waveform0_m2) #compute mchirp of waveform0

    waveform0_ecc = eccs[ecc_index0]
    waveform0_lan = lans[lan_index0]
    waveform0_inc = incs[inc_index0]

    waveform0 = GenTemplate(mass1=waveform0_m1, mass2=waveform0_m2,
                           apx = waveform0_apx,
                           ecc = waveform0_ecc,
                           lan = waveform0_lan,
                           inc = waveform0_inc,
                           f_low = 30.,
                           freq_step = 4)

    local_matches = np.zeros(len(tp_m1))
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
            one_relevant_temp = GenTemplate(mass1 = this_tp_m1, mass2 = this_tp_m2, apx = tp_apx[k], ecc = tp_ecc[k], lan = tp_lan[k],inc = tp_inc[k], f_low=30, freq_step=4)
            one_local_match = GetMatch(waveform0, one_relevant_temp)
            local_matches[k] = one_local_match
    global_match = np.amax(local_matches)
    return global_match


inj_counter = 0
# iterate through all injections
print ("inj_num, inj_mass1, inj_mass2, inj_ecc, inj_lan, inj_inc, fitting_factor")
for i in range(0,len(masses1)): 
    for j in range(0,len(masses2)):
        for ecc_ind in range(0,len(eccs)):
            for lan_ind in range(0,len(lans)):
                for inc_ind in range(0,len(incs)):
                    inj_counter += 1
                    this_global_match = GetGlobalMatch(i_waveform0 = i,
                                        j_waveform0 = j,
                                        waveform0_apx = 'EccentricFD',
                                        ecc_index0 = ecc_ind,
                                        lan_index0 = lan_ind,
                                        inc_index0 = inc_ind,
                                        tp_apx = bank_apx,
                                        tp_m1 = bank_mass1,
                                        tp_m2 = bank_mass2,
                                        tp_ecc = bank_ecc,
                                        tp_lan = bank_lan,
                                        tp_inc = bank_inc,
                                        searching_radius = args.radius)
                    this_inj_mass1 = masses1[i]
                    this_inj_mass2 = masses2[j]
                    this_inj_ecc = eccs[ecc_ind]
                    this_inj_lan = lans[lan_ind]
                    this_inj_inc = incs[inc_ind]
                    print ("%d, %f, %f, %f, %f, %f, %f" % (inj_counter, this_inj_mass1, this_inj_mass2, this_inj_ecc, this_inj_lan, this_inj_inc, this_global_match))


end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)

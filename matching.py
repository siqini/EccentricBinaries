import argparse

from pycbc.filter.matchedfilter import match
from pycbc.waveform import get_td_waveform
import pycbc
import pycbc.psd
import numpy as np
import h5py 
import requests
import json
import sys

from datetime import datetime

import rescaling

parser = argparse.ArgumentParser()
parser.add_argument('--sxs_id', type=str, required=True, dest='sxs_id')
parser.add_argument('--simulation', type=str, required=True, dest='simulation_path')
parser.add_argument('--total_mass', type=float, required=True, dest='total_mass')
parser.add_argument('--template_bank', type=str, required=True, dest='template_bank' )
parser.add_argument('--psd', type=str, required=False, dest='psd_filename', default = 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt')
parser.add_argument('--radius', type=float, required=True, dest='radius')

args = parser.parse_args()

start = datetime.now()
print ("Start time: %s" % start)

print ('SXS ID: ' + args.sxs_id)
sys.stdout.flush()

# Rescale the given simulation waveform to the chosen total mass 
sp = rescaling.rescale(simulation_path = args.simulation_path, total_mass = args.total_mass, real = True)
sc = rescaling.rescale(simulation_path = args.simulation_path, total_mass = args.total_mass, real = False)

# Grab the template bank info 
f_bank = h5py.File(args.template_bank, 'r')
bank_mass1 = f_bank['mass1'][:]
bank_mass2 = f_bank['mass2'][:]
bank_ecc = f_bank['eccentricity'][:]
bank_lan = f_bank['long_asc_nodes'][:]
bank_inc = f_bank['inclination'][:]
bank_apx = f_bank['approximant'][:]
f_bank.close()

# Get the reference mass ratio of the simulation
request = requests.get("https://data.black-holes.org/catalog.json", headers={'accept': 'application/citeproc+json'})
sxs_full_json = request.json()
sxs_catalog_json = sxs_full_json['simulations']
mass_ratio = sxs_catalog_json[args.sxs_id]['reference_mass_ratio']
eccentricity_str = sxs_catalog_json[args.sxs_id]['reference_eccentricity']

print ('Simulation mass ratio: %s' % mass_ratio)
print ('Simulation eccentricity: ' + eccentricity_str)

# Compute the component masses 
sim_m2 = args.total_mass/(mass_ratio+1.)
sim_m1 = args.total_mass - sim_m2

print ('Component mass1: %s' % sim_m1)
print ('Component mass2: %s' % sim_m2)

sys.stdout.flush()

def GetMatch (template0,template1, psd_file =args.psd_filename, f_low=30):
    #resize two templates
    tlen = max(len(template0),len(template1))
    template1.resize(tlen)
    template0.resize(tlen)

    #grab and use the psd file
    my_psd = pycbc.psd.read.from_txt(filename = psd_file,
                                    length = tlen,
                                    delta_f = template0.delta_f,
                                    low_freq_cutoff = f_low,
                                    is_asd_file = False)

    #calculate match
    m,i = match(template0,template1,psd=my_psd,low_frequency_cutoff=f_low)
    return m

def GetFittingFactor(comp_mass1, comp_mass2, waveform0, tp_apx, tp_m1, tp_m2, tp_ecc, tp_lan, tp_inc, radius, f_low=30):
    waveform0_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(comp_mass1, comp_mass2)
    matches = []
    for k in range(0, len(tp_m1)):
        template_m1 = tp_m1[k]
        template_m2 = tp_m2[k]
        template_mchirp = pycbc.conversions.mchirp_from_mass1_mass2(template_m1, template_m2)
        diff = abs(waveform0_mchirp - template_mchirp)
        percentage_diff = diff/waveform0_mchirp
        if (percentage_diff > radius):
            matches.append(0.)
        else: 
            hp, hc = get_td_waveform(approximant = 'EccentricTD',
                                    mass1 = tp_m1[k],
                                    mass2 = tp_m2[k],
                                    eccentricity = tp_ecc[k],
                                    long_asc_nodes = tp_lan[k],
                                    inclination = tp_inc[k],
                                    f_lower = f_low,
                                    delta_t = waveform0.delta_t)
            this_match = GetMatch(waveform0, hp)
            matches.append(this_match)
            print ('Found a nontrivial match: at template %d:  %s' % (k, this_match))
    matches = np.asarray(matches)
    fitting_factor = np.amax(matches)
    return fitting_factor

ff = GetFittingFactor(comp_mass1 = sim_m1, 
                      comp_mass2 = sim_m2,
                      waveform0 = sp,
                      tp_apx = bank_apx,
                      tp_m1 = bank_mass1,
                      tp_m2 = bank_mass2,
                      tp_ecc = bank_ecc,
                      tp_lan = bank_lan,
                      tp_inc = bank_inc,
                      radius = args.radius)

print ('Fitting factor: %s' % ff)
sys.stdout.flush()
end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)

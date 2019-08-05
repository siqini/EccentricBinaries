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
parser.add_argument('--sxs_ids_file', type=str, required=True, dest='sxs_ids_file')
parser.add_argument('--total_mass', type=float, required=True, dest='total_mass')
parser.add_argument('--template_bank', type=str, required=True, dest='template_bank' )
parser.add_argument('--psd', type=str, required=False, dest='psd_filename', default = 'H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt')
parser.add_argument('--radius', type=float, required=True, dest='radius')

args = parser.parse_args()

start = datetime.now()
print ("Start time: %s" % start)
sys.stdout.flush()

# Grab the template bank info 
f_bank = h5py.File(args.template_bank, 'r')
bank_mass1 = f_bank['mass1'][:]
bank_mass2 = f_bank['mass2'][:]
bank_ecc = f_bank['eccentricity'][:]
bank_lan = f_bank['long_asc_nodes'][:]
bank_inc = f_bank['inclination'][:]
bank_apx = f_bank['approximant'][:]
f_bank.close()

request = requests.get("https://data.black-holes.org/catalog.json", headers={'accept': 'application/citeproc+json'})
sxs_full_json = request.json()
sxs_catalog_json = sxs_full_json['simulations']

sxs_ids = np.loadtxt(fname = args.sxs_ids_file, 
                    dtype = str,
                    delimiter = " ")

paths = []
for sxs_id in sxs_ids:
    folder_name = sxs_id.replace(":", "_")
    path = folder_name + '/rhOverM_Asymptotic_GeometricUnits_CoM.h5'
    paths.append(path)

number_injections = len(paths)
print ('Number of simulations: %d' % number_injections)
print ('Total mass: %s' % args.total_mass)
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
            #print ('Found a nontrivial match: at template %d:  %s' % (k, this_match))
    matches = np.asarray(matches)
    fitting_factor = np.amax(matches)
    return fitting_factor

print ("Simulation number, SXS ID, Simulation mass ratio, Simulation eccentricity, Component mass1, Component mass2, Fitting factor")
sys.stdout.flush()
for i in range(0, number_injections):
    sxs_id = sxs_ids[i]
    path = paths[i]

    # Rescale the waveform to the chosen total mass
    sp = rescaling.rescale(simulation_path = args.simulation_path, total_mass = args.total_mass, real = True)
    sc = rescaling.rescale(simulation_path = args.simulation_path, total_mass = args.total_mass, real = False)
    # Get the reference mass ratio and eccentricity of the simulation
    mass_ratio = sxs_catalog_json[args.sxs_id]['reference_mass_ratio']
    eccentricity_str = sxs_catalog_json[args.sxs_id]['reference_eccentricity']
    if eccentricity_str.startswith('<'):
        eccentricity = 0.
    else:
        eccentricity = float(eccentricity_str)

    # Compute the component masses 
    sim_m2 = args.total_mass/(mass_ratio+1.)
    sim_m1 = args.total_mass - sim_m2

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
    
    print ("%d, " % (i+1) + sxs_id + ", %f, %f, %f, %f, %f" % (mass_ratio, eccentricity, sim_m1, sim_m2, ff))
    sys.stdout.flush()


end=datetime.now()
total_runtime = end-start
print ("Ending time: %s" % end)
print ("Runtime: %s" % total_runtime)

source env/bin/activate
export LAL_DATA_PATH = '/atlas/recent/cbc/ROM_data/'

tar -zxvf targets.tar.gz
python chisq_prototype.py --sxs_id 'SXS:BBH:0012' --sim_path 'targets/SXS_BBH_0012/rhOverM_Asymptotic_GeometricUnits_CoM.h5' --total_mass 20.0 --seed 678 --tbank 'bank0729_atlas1_new6.hdf' --radius 0.05 

deactivate
rm -rf targets 
rm targets.tar.gz
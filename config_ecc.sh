Universe = vanilla
Executable = main_ecc.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/logs/ecc2.err
Output = /work/siqi.ni/logs/ecc2.out
Log = /work/siqi.ni/logs/ecc2.log

should_transfer_files = YES
transfer_input_files = main_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt
transfer_output_files = ecc_contour.png, ecc_fitting_factor.out
WhenToTransferOutput = ON_EXIT

RequestCpus = 8
RequestMemory = 5000
Queue 1

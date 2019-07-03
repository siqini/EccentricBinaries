Universe = vanilla
Executable = main.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/logs/necc2.err
Output = /work/siqi.ni/logs/necc2.out
Log = /work/siqi.ni/logs/necc2.log

should_transfer_files = YES
transfer_input_files = main.py, env.tar.gz, stand.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
transfer_output_files = necc_contour.png, fitting_factor.out
WhenToTransferOutput = ON_EXIT

RequestCpus = 6
RequestMemory = 5000
Queue 1

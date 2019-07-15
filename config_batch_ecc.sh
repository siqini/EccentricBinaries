Universe = vanilla
Executable = main_batch_ecc.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/stand_einj0715/stand_einj_$(Process).err
Output = /work/siqi.ni/out/stand_einj0715/stand_einj_$(Process).out
Log = /work/siqi.ni/logs/stand_einj0715/stand_einj_$(Process).log

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, stand.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = $(Process)
RequestCpus = 6
RequestMemory = 6000
Queue 1089

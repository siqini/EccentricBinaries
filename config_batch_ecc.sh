Universe = vanilla
Executable = main_batch_ecc.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/batchfy_bank/batch_ebank_ninj_$(Process).err
Output = /work/siqi.ni/out/batchfy_bank/batch_ebank_ninj_$(Process).out
Log = /work/siqi.ni/logs/batchfy_bank/batch_ebank_ninj_$(Process).log

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = $(Process)
RequestCpus = 5
RequestMemory = 5000
Queue 1001

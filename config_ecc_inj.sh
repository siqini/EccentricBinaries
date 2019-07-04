Universe = vanilla
Executable = main_ecc_inj.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/ecc_inj_$(Process).err
Output = /work/siqi.ni/out/ecc_inj_$(Process).out

Log = /work/siqi.ni/logs/ecc_inj_$(Process).log

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py
transfer_output_files = ecc_inj*out
WhenToTransferOutput = ON_EXIT

Arguments = 0
RequestCpus = 4
RequestMemory = 5000
Queue 1

Arguments = 1
RequestCpus = 4
RequestMemory = 5000
Queue 1

Arguments = 2
RequestCpus = 4
RequestMemory = 5000
Queue 1

Arguments = 3
RequestCpus = 4
RequestMemory = 5000
Queue 1

Arguments = 4
RequestCpus = 4
RequestMemory = 5000
Queue 1

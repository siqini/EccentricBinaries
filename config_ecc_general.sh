Universe = vanilla
Executable = main_ecc_general.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/ecc_inj_$(Process).err
Output = /work/siqi.ni/out/ecc_inj_$(Process).out

Log = /work/siqi.ni/logs/ecc_inj_$(Process).log

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output0.txt
transfer_output_files = ecc_inj_output0.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1 0 0.0 0.08
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output1.txt
transfer_output_files = ecc_inj_output1.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1 1 0.0 0.08
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output2.txt
transfer_output_files = ecc_inj_output2.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1 2 0.0 0.08
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output3.txt
transfer_output_files = ecc_inj_output3.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1 3 0.0 0.08
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = eccentric_injections.py, env.tar.gz, stand.hdf, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt, EccStudy.py, ecc_inj_output4.txt
transfer_output_files = ecc_inj_output4.txt
WhenToTransferOutput = ON_EXIT

Arguments = 1 4 0.0 0.08
RequestCpus = 5
RequestMemory = 5000
Queue 1

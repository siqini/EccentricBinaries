Universe = vanilla
Executable = main_batch_ecc.sh
accounting_group = aei.prod.cbc.bns

Error = /work/siqi.ni/error/batch_en_$(Process).err
Output = /work/siqi.ni/out/batch_en_$(Process).out
Log = /work/siqi.ni/logs/batch_en_$(Process).log

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 0
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 1
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 2
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 3
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 4
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 5
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 6
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 7
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 8
RequestCpus = 5
RequestMemory = 5000
Queue 1

should_transfer_files = YES
transfer_input_files = main_batch_ecc.py, env.tar.gz, ebank.hdf, H1L1-O1_C02_HARM_MEAN_PSD-1126051217-11203200.txt   
WhenToTransferOutput = ON_EXIT

Arguments = 9
RequestCpus = 5
RequestMemory = 5000
Queue 1
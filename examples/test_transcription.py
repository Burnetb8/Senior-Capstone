import nemo.collections.asr as nemo_asr


#test citrinet model
model = nemo_asr.models.EncDecCTCModelBPE.restore_from(restore_path="ft100epoch_stt_en_citrinet_512.nemo")

paths = []
paths.append("/root/Nemo-Project/Senior-Capstone/examples/utils/data/S0293/speechdata/MN/IT/IFAF/IFAF_007_MN.wav")
paths.append("/root/Nemo-Project/Senior-Capstone/examples/utils/data/S0293/speechdata/MN/IT/IFAF/IFAF_017_MN.wav")
paths.append("/root/Nemo-Project/Senior-Capstone/examples/utils/data/S0293/speechdata/MN/IT/IFAF/IFAF_027_MN.wav")


out = model.transcribe(paths2audio_files=paths, batch_size=8, logprobs=False)

for o in out:
    print(o)
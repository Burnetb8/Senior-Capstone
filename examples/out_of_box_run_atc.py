# NeMo's "core" package
import os
# NeMo's ASR collection - this collections contains complete ASR models and
# building blocks (modules) for ASR
import nemo.collections.asr as nemo_asr

data_dir = '.'

# This line will download pre-trained QuartzNet15x5 model from NVIDIA's NGC cloud and instantiate it for you
quartznet = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="QuartzNet15x5Base-En")

files = [os.path.join(data_dir, '/home/john/Documents/Projects/Senior-Capstone/examples/atc0_comp/atc_short.wav')]
#files = './home/john/Documents/Projects/Senior-Capstone/examples/atc0_comp/atc_short.wav'
for fname, transcription in zip(files, quartznet.transcribe(paths2audio_files=files)):
  print(f"Audio in {fname} was recognized as: {transcription}")

#https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local
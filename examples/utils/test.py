import torch
import nemo.collections.asr as nemo_asr

print("Available Models")
print(nemo_asr.models.EncDecCTCModel.list_available_models())
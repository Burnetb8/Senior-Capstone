import torch
import nemo.collections.asr as nemo_asr

print("Is torch working")
print(torch.cuda.is_available())

print("Available Models")
print(nemo_asr.models.EncDecCTCModel.list_available_models())
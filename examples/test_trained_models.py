import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
from ruamel.yaml import YAML
from omegaconf import DictConfig
from omegaconf import OmegaConf, open_dict

config_path = 'config/citrinet_512_tokenizer.yaml'
model_check_point = 'ft100epoch_stt_en_citrinet_512_tokenizer.nemo'
validation_manifest = 'utils/manifests/atcc_validation.json'
#this is a model found by running test.py looking for EncDecoCTCModelBPE
tokenizer_model = 'tokenizers/tokenizer_spe_bpe_v400/'

trainer = pl.Trainer(gpus=[0], max_epochs=100)
params = OmegaConf.load(config_path)

params.model.tokenizer.dir = tokenizer_model
params.model.tokenizer.type = 'bpe'

#params.model.train_ds.manifest_filepath = train_manifest
params.model.validation_ds.manifest_filepath = validation_manifest

#base_model = nemo_asr.models.EncDecCTCModelBPE(cfg=params.model, trainer=trainer)

base_model = nemo_asr.models.EncDecCTCModelBPE.restore_from(model_check_point)

base_model._wer.log_prediction = False
base_model.cuda()
base_model.eval()


#need to construct a predictions list and a targets list to give to this from 
"""
base_model._wer.update(

    predictions = 
    targets = 
    target_lengths = 

)
"""
wer_result = base_model._wer.compute()

base_model._wer.reset()
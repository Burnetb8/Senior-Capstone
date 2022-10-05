import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
from ruamel.yaml import YAML
from omegaconf import DictConfig

config_path = 'config/config.yaml'
train_manifest = 'manifest/train.json'
validation_manifest = 'manifest/valid.json'
base_model_name = "stt_en_citrinet_256"
save_as = 'ft100epoch_stt_en_citrinet_256.nemo'

with open(config_path, 'r') as f:
    config = YAML(typ='safe').load(f)

torch.cuda.empty_cache()
gc.collect()

config['model']['train_ds']['manifest_filepath'] = train_manifest
config['model']['train_ds']['batch_size'] = 8
config['model']['validation_ds']['manifest_filepath'] = validation_manifest
config['model']['validation_ds']['batch_size'] = 8
config['model']['optim']['lr'] = 0.001

base_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name=base_model_name)

base_model.setup_optimization(optim_config=DictConfig(config['model']['optim']))
base_model.setup_training_data(train_data_config=DictConfig(config['model']['train_ds']))
base_model.setup_validation_data(val_data_config=DictConfig(config['model']['validation_ds']))

trainer = pl.Trainer(gpus=[0], max_epochs=100)
trainer.fit(base_model)

base_model.save_to(save_as)

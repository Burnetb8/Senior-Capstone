import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
from ruamel.yaml import YAML
from omegaconf import DictConfig

config_path = 'config/config.yaml'
train_manifest = 'utils/manifests/atcc_train.json'
valid_manifest = 'utils/manifests/atcc_validation.json'
checkpoint_name = '100epoch_quartznet_scratch.nemo'

torch.cuda.empty_cache()
gc.collect()

with open(config_path, 'r') as f:
    config = YAML(typ='safe').load(f)

config['model']['train_ds']['manifest_filepath'] = train_manifest
config['model']['train_ds']['batch_size'] = 8
config['model']['validation_ds']['manifest_filepath'] = valid_manifest
config['model']['validation_ds']['batch_size'] = 8

model = nemo_asr.models.EncDecCTCModel(cfg=DictConfig(config['model']))
model.setup_training_data(DictConfig(config['model']['train_ds']))
model.setup_validation_data(DictConfig(config['model']['validation_ds']))

#trainer = pl.Trainer(gpus=[0], max_epochs=100)
trainer = pl.Trainer(max_epochs=1)
#trainer.fit(model)

model.save_to(checkpoint_name)


data_loader = model._setup_dataloader_from_config(validation_manifest)
predictions = trainer.predict(model=base_model, dataloaders=data_loader, return_predictions=False)


base_model.save_to(save_as)



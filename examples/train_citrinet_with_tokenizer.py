import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
from ruamel.yaml import YAML
from omegaconf import DictConfig

config_path = 'config/citrinet_512_tokenizer.yaml'
train_manifest = 'utils/manifests/atcc_train.json'
validation_manifest = 'utils/manifests/atcc_validation.json'
#this is a model found by running test.py looking for EncDecoCTCModelBPE
base_model_name = 'stt_en_citrinet_512'
save_as = 'ft100epoch_stt_en_citrinet_512_tokenizer.nemo'

with open(config_path, 'r') as f:
    config = YAML(typ='safe').load(f)

torch.cuda.empty_cache()
gc.collect()


config['model']['train_ds']['manifest_filepath'] = train_manifest

config['model']['validation_ds']['manifest_filepath'] = validation_manifest

config['model']['optim']['lr'] = 0.001

config['model']['tokenizer']['dir'] = "test_tokenizer.model"

config['model']['tokenizer']['type'] = "bpe"

trainer = pl.Trainer(gpus=[0], max_epochs=100)

base_model = nemo_asr.models.EncDecCTCModelBPE(cfg = DictConfig(config['model']))
#base_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(base_model_name)

base_model.change_vocabulary(new_tokenizer_dir = DictConfig(config['model']['tokenizer']['dir']), new_tokenizer_type = DictConfig(config['model']['tokenizer']['type']))

base_model.setup_optimization(optim_config=DictConfig(config['model']['optim']))
base_model.setup_training_data(train_data_config=DictConfig(config['model']['train_ds']))
base_model.setup_validation_data(val_data_config=DictConfig(config['model']['validation_ds']))


trainer.fit(base_model)

base_model.save_to(save_as)
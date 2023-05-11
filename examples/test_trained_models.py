import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
import json
from ruamel.yaml import YAML
from omegaconf import DictConfig
from omegaconf import OmegaConf, open_dict
from nemo.collections.asr.metrics.wer import word_error_rate

config_path = "config/citrinet_512_tokenizer.yaml"
model_check_point = "ft100epoch_stt_en_citrinet_512_tokenizer.nemo"
validation_manifest = "utils/manifests/atcc_validation.json"
# this is a model found by running test.py looking for EncDecoCTCModelBPE
tokenizer_model = "tokenizers/tokenizer_spe_bpe_v400/"


trainer = pl.Trainer(gpus=[0], max_epochs=100)
params = OmegaConf.load(config_path)

params.model.tokenizer.dir = tokenizer_model
params.model.tokenizer.type = "bpe"

# params.model.train_ds.manifest_filepath = train_manifest
params.model.validation_ds.manifest_filepath = validation_manifest

# base_model = nemo_asr.models.EncDecCTCModelBPE(cfg=params.model, trainer=trainer)

base_model = nemo_asr.models.EncDecCTCModelBPE.restore_from(model_check_point)

base_model._wer.log_prediction = False
base_model.cuda()
base_model.eval()

# preping the validation file

validation_file = open(validation_manifest, "r")

nice_validation_data = []
validation_files_paths = []
validation_targets = []

# loading in validation data from json file
for l in validation_file:
    nice_validation_data.append(json.loads(l))

# Getting file paths and getting hypothesis
for l in nice_validation_data:
    validation_files_paths.append(l["audio_filepath"])
    validation_targets.append(l["text"].lower())

validation_predictions = base_model.transcribe(
    paths2audio_files=validation_files_paths, batch_size=1
)

wer = word_error_rate(
    hypotheses=validation_targets, references=validation_predictions, use_cer=False
)

print("Word error rate for model")
print(str(wer))

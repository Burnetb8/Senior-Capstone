import nemo.collections.asr as nemo_asr
import pytorch_lightning as pl
import torch
import gc
from ruamel.yaml import YAML
from omegaconf import DictConfig
from omegaconf import OmegaConf, open_dict




class Transcribe_ATC:


    def __init__(self):
        #EncDecCTCModelBPE is for citrinet models you will need to change this depending
        #on the model we are using 
        #EncDecCTCModel is for quartznet and jasper
        self.model_check_point = 'ft100epoch_stt_en_citrinet_512_2.nemo'
        try:
            self.base_model = nemo_asr.models.EncDecCTCModelBPE.restore_from(self.model_check_point)
        except:
            self.base_model = nemo_asr.models.EncDecCTCModel.restore_from(self.model_check_point)

    def transcribe_audio(self,file_name):
        files = [file_name]
        self.base_model.transcribe(paths2audio_files=files, batch_size=1) 





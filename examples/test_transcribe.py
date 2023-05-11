from transcribe_given_audio_file import Transcribe_ATC


test_file = "utils/data/atc0_comp/atc0_bos/data/audio/log_f1_3.wav"

test_trans = Transcribe_ATC()

test_trans.transcribe_audio(test_file)

from transcribe_given_audio_file import Transcribe_ATC
import numpy as np
import pydub
import requests

transcription = ""

#this object does the transcription
transcribe = Transcribe_ATC()

def fetch_stream():
    # Read stream, save to wav 
    stream_url = "http://d.liveatc.net/kdab_del_gnd"
    return requests.get(stream_url, stream=True)

def block_to_wav(block):
    a = pydub.AudioSegment(block, sample_width=2, frame_rate=11025, channels=1)
    a.export(f"stream.wav", format="wav")

def transcribe_audio():
    #give this object a file path and it returns a string
    return transcribe.transcribe_audio('stream.wav')

def get_transcription_array(block):
    a = pydub.AudioSegment(block, sample_width=2, frame_rate=11025, channels=1)
    a_temp = a.get_array_of_samples()
    return transcribe.transcribe_audio_array(a_temp)

def audio_fetch_and_transcribe():
    global transcription

    r = fetch_stream()

    for block in r.iter_content(20480):
        type(block)
        #block_to_wav(block)
        transcription = get_transcription_array(block)
        print(transcription)

def get_latest_transcription():
    return transcription

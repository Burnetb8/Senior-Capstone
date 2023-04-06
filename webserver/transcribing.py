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

def get_transcription_array(filename):
    # Load the file into PyDub AudioSegment
    audio_segment = pydub.AudioSegment.from_file(file=filename, format="mp3")

    # Get array of samples (signals) from the audio segment
    samples = audio_segment.get_array_of_samples()

    # Pass array to model, get transcription result 
    return transcribe.transcribe_audio_array(np.array(samples))

def audio_fetch_and_transcribe():
    global transcription

    r = fetch_stream()
    filename = "stream.mp3"

    for block in r.iter_content(20480):
        # Write 10 seconds of streamed data to the file
        with open(filename, 'wb') as f:
            f.write(block)
        f.close()

        # Transcribe
        transcription = get_transcription_array(filename)
        print(f'transcription: {transcription}')

def get_latest_transcription():
    return transcription

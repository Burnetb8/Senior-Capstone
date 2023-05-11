"""
This file contains the code nessicary to properly format and organize the data from the two provided datasets of ATC communication.
"""
import os
import glob
import subprocess
import json
from lisp_parser import parse
from typing import Union, List, Dict, Tuple
from pathlib import Path
from pydub import AudioSegment
import io
import librosa
from typing import List, Union


"""
These functions are responsible for formatting the Hiwire dataset
"""
d2w = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


def _reformat_labels(labels: List[str]) -> List[str]:
    output = []
    # modified from https://github.com/eraus/pfiga_sperega/blob/main/1pj/nemo_asr_development/alterManifest.ipynb
    for label in labels:
        words = label.split()
        for i, word in enumerate(words):
            if word.isupper():
                word = " ".join([char for char in word])
            # word = word.lower()
            words[i] = word
        temp = " ".join(words)

        debug = False
        for char in ["-", "/"]:
            if "/" in temp:
                print(temp)
                debug = True
            temp = temp.replace(char, " ")
            if debug:
                print(temp)
                debug = False

        for num in d2w.keys():
            if num in temp:
                temp = temp.replace(num, d2w[num])
        output.append(temp)
    return output


def build_hiwire_manifest(root_path: Union[Path, str]) -> List[str]:
    assert isinstance(root_path, Path) or isinstance(
        root_path, str
    ), f"root_path mus be a string of Path type"
    if isinstance(root_path, str):
        assert os.path.exists(root_path), "path does not exist"
    else:
        assert root_path.exists(), "path does not exist"

    manifest_data = []

    search_string = os.path.join(root_path, "**/list.txt")
    transcripts = glob.glob(search_string, recursive=True)
    transcripts = [Path(path) for path in transcripts]

    for transcript in transcripts:
        wav_files = sorted(
            [
                file.absolute()
                for file in transcript.parent.iterdir()
                if file.suffix == ".wav"
            ],
            key=lambda x: x.name,
        )

        with transcript.open("r") as f:
            labels = f.readlines()[1:]
            labels = [label[: label.find("(")].strip() for label in labels]
            labels = _reformat_labels(labels)

        for wav, label in zip(wav_files, labels):
            manifest_data.append(
                json.dumps(
                    {
                        "audio_filepath": str(wav),
                        "text": label,
                        "duration": float(librosa.get_duration(filename=str(wav))),
                    }
                )
            )

    return manifest_data


"""
These are the functions needed to format the ATC dataset 
"""


def enumerate_files(
    root_path: Union[Path, str]
) -> Union[Tuple[List[Path], List[Path]], Tuple[List[str], List[str]]]:
    """
    Enumerates the audio and corresponding transcript files in the dataset and performs the file conversion from the NIST Sphere
    format (`sph`)to WAV format (`wav`). **Note**: `ffmpeg` must be installed for the file conversion to work.
    Arguments:
    ----------
    `root_path`: string or pathlib.Path object, path to the root of the dataset e.g. /data/atc0_ldc94s14a
    Returns:
    --------
    `(audio_paths, transcript_paths)`: Tuple of pathlib.Path objects or strings, depending on input type, that contains the audio and
    transcript file paths.
    """
    assert isinstance(root_path, str) or isinstance(
        root_path, Path
    ), f"root_path must be a string or Path type"
    if isinstance(root_path, str):
        assert os.path.exists(root_path), "path does not exist"
    else:
        assert root_path.exists(), "path does not exist"

    # convert to pathlib object to make system path ops easier
    root = Path(root_path).absolute()

    # if ffmpeg_present:
    # check if sphere files need to be converted
    sphere_paths = glob.glob(str(root.joinpath("**/audio/*.sph")), recursive=True)
    if len(sphere_paths) > 0:
        convert_sph_to_wav(sphere_paths)

    # audio and transcript globs
    audio = sorted(glob.glob(str(root.joinpath("**/audio/*.wav")), recursive=True))
    transcripts = sorted(
        glob.glob(str(root.joinpath("**/transcripts/*.txt")), recursive=True)
    )

    assert len(audio) == len(transcripts)

    # return tuple of types to match input type i.e. return Path objects for an input of a Path object
    # and strings for an input of a string
    if isinstance(root_path, Path):
        # string paths
        return audio, transcripts
    else:
        # pathlib paths
        return [str(x) for x in audio], [str(x) for x in transcripts]


def build_atcc_manifests(
    audio_paths: Union[List[Path], List[str]],
    transcript_paths: Union[List[Path], List[str]],
) -> List[str]:
    """
    Parses transcripts and converts it into NeMo manifest format.
    Arguments:
    ----------
    `audio_paths`: Either a list of pathlib.Path object or a list of strings containing the paths to the audio files
    (see ~`enumerate_files`).
    `transcript_paths`: Either a list of pathlib.Path object or a list of strings containing the paths to the transcript files
    (see ~`enumerate_files`).
    Returns:
    -------
    `manifest_data`: A list of JSON formatted strings with the info necessary for NeMo to process and use the data.
    """
    manifest_lines = []

    for audio, transcript in zip(audio_paths, transcript_paths):
        audio = Path(audio)

        with open(transcript, "r", encoding="utf-8") as f:
            transcript_info = parse(f.readlines())

        for item in transcript_info:
            try:
                duration = round(item["TIMES"]["end"] - item["TIMES"]["start"], 3)

                if duration <= float(1 / 16000):
                    print(str(audio))

                if item["TEXT"] != "":
                    manifest_lines.append(
                        json.dumps(
                            {
                                "audio_filepath": str(audio.absolute()),
                                "text": item["TEXT"].lower(),
                                "offset": item["TIMES"]["start"],
                                "duration": duration,
                            }
                        )
                    )
            except KeyError:
                continue

    return manifest_lines


def convert_sph_to_wav(paths: Union[List[Path], List[str]]):
    """
    Converts NIST Sphere formatted files to WAV format.
    Arguments:
    ----------
    `paths`: paths to the Sphere files to reformat.
    Returns:
    --------
    `None`
    """
    for file in paths:
        if not isinstance(file, Path):
            file = Path(file).absolute()
        subprocess_cmd = [
            "sox",
            str(file),
            # "-r",
            # "16000",
            str(file).replace(".sph", ".wav"),
        ]
        # print(subprocess_cmd)
        subprocess.run(subprocess_cmd)


"""
This function is used to split into a test and train manifest
"""


def split_json(
    all_manifest: str,
    hiwire_manifest: str,
    train_manifest: str,
    validation_manifest: str,
):
    """

    load atcc_all.json and hiwire_all.json from file then combine and split them into test and train files
    split ratio is train/total so a split_ratio = 0.75 would mean 75% goes to train and 25% to validation

    """

    split_ratio = 0.75

    # atcc_all_json = open(all_manifest, "r")
    # to remove the first not nessicary line
    # print(atcc_all_json.readline())

    with open(all_manifest) as f:
        atcc_all_json = f.read().splitlines()

    with open(hiwire_manifest) as f:
        hiwire_all_json = f.read().splitlines()

    atcc_all_json += hiwire_all_json

    x = 3

    # print(type(atcc_all_json))
    # print(atcc_all_json[x])
    # print(type(json.loads(atcc_all_json[x])))
    # print(type(json.loads(atcc_all_json[x])['duration']))

    # Removing clips with duration less than 1 cause that is causing errors
    mininum_duration = 1

    for atc in atcc_all_json:
        if json.loads(atc)["duration"] < mininum_duration:
            atcc_all_json.remove(atc)

    # creating training set
    training_length = int(len(atcc_all_json) * split_ratio)
    train_list = atcc_all_json[1:training_length]

    with open(train_manifest, "w") as manifest:
        # manifest.write("[\n")
        manifest.write("\n".join(train_list))
        # manifest.write("]")

    # creating validation set
    data_len = int(len(atcc_all_json))
    validation_list = atcc_all_json[training_length + 1 : data_len]

    with open(validation_manifest, "w") as manifest:
        # manifest.write("[ \n")
        manifest.write("\n".join(validation_list))
        # manifest.write("]")


if __name__ == "__main__":
    # using the above defined functions to format Hiwire dataset
    manifest_all = build_hiwire_manifest("data/S0293/speechdata")
    os.makedirs("manifests", exist_ok=True)
    with open("manifests/hiwire_all.json", "w") as manifest:
        manifest.write("\n".join(manifest_all))

    # Using the above defined functions to format the ATC dataset
    # list of audio and transcripts
    audio, transcripts = enumerate_files("data/atc0_comp")
    # manifest format (array or strings, each string corresponds to one line)
    # this is all of the data before being split into train/test/validation
    manifest_all = build_atcc_manifests(audio, transcripts)

    # store manifest json in 'manifests' directory
    os.makedirs("manifests", exist_ok=True)
    with open("manifests/atcc_all.json", "w", encoding="utf-8") as manifest:
        manifest.write("\n".join(manifest_all))

    # spliting into test and training datasets
    all_manifest = "manifests/atcc_all.json"
    hiwire_manifest = "manifests/hiwire_all.json"
    train_manifest = "manifests/atcc_train.json"
    validation_manifest = "manifests/atcc_validation.json"
    split_json(all_manifest, hiwire_manifest, train_manifest, validation_manifest)

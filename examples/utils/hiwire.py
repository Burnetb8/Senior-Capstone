"""
This file contains the functions necessary to preprocess
"""
import os
import json
import glob
import librosa
from pathlib import Path
from typing import List, Union


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


if __name__ == "__main__":
    manifest_all = build_hiwire_manifest("data/S0293/speechdata")
    os.makedirs("manifests", exist_ok=True)
    with open("manifests/hiwire_all.json", "w") as manifest:
        manifest.write("\n".join(manifest_all))

"""
This file contains the necessary functions to preprocess the audio and
transcript data of the Air Traffic Control Complete dataset and transform
it into the NeMo manifest format.
"""
import os
import glob
import subprocess
import json
from lisp_parser import parse
from typing import Union, List, Dict, Tuple
from pathlib import Path
from pydub import AudioSegment

# If I could make this a one-liner I would, but I'm not sure how or if it is possible
# ffmpeg_present = subprocess.run(["command", "-v", "ffmpeg"])
# ffmpeg_present = not bool(ffmpeg_present.returncode)


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


if __name__ == "__main__":
    # list of audio and transcripts
    audio, transcripts = enumerate_files("data/atc0_comp")
    # manifest format (array or strings, each string corresponds to one line)
    # this is all of the data before being split into train/test/validation
    manifest_all = build_atcc_manifests(audio, transcripts)

    # store manifest json in 'manifests' directory
    os.makedirs("manifests", exist_ok=True)
    with open("manifests/atcc_all.json", "w", encoding="utf-8") as manifest:
        manifest.write("\n".join(manifest_all))

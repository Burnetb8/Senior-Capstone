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


def enumerate_files(
    root_path: Union[Path, str]
) -> Union[Tuple[List[Path], List[Path]], Tuple[List[str], List[str]]]:
    """
    Arguments:
    Returns:
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

    # check if sphere files need to be converted
    sphere_paths = glob.glob(root.join(["**", "audio", "*.sph"]), recursive=True)
    if len(sphere_paths) > 0:
        convert_sph_to_wav(sphere_paths)

    # audio and transcript globs
    audio = glob.glob(root.join(["**", "audio", "*.wav"]), recursive=True)
    transcripts = glob.glob(root.join(["**", "transcripts", "*.txt"]), recursive=True)

    # return tuple of types to match input type i.e. return Path objects for an input of a Path object
    # and strings for an input of a string
    if isinstance(root_path, Path):
        # string paths
        return audio, transcripts
    else:
        # pathlib paths
        return [str(x) for x in audio], [str(x) for x in transcripts]


def build_manifests(files: Union[Path, str]) -> List[str]:
    manifest_lines = []
    for file in files:
        with open(file, "r") as f:
            transcript_info = parse(f.readlines())
        manifest_lines.append(
            json.dumps(
                {
                    "audio_filepath": file,
                    "text": transcript_info["TEXT"],
                    "offset": transcript_info["TIMES"]["start"],
                    "duration": round(
                        transcript_info["TIMES"]["end"]
                        - transcript_info["TIMES"]["start"],
                        3,
                    ),
                }
            )
        )
    return manifest_lines


def convert_sph_to_wav(paths: List[str]):
    for file in paths:
        file = Path(file).absolute()
        ffmpeg_command = ["ffmpeg", f"-i {str(file)}", f"{str(file.name)}.wav"]
        subprocess.run(ffmpeg_command)

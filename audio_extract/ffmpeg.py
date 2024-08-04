# Other modules
import subprocess
import os
import sys
# Local modules
from audio_extract.validators import AudioExtractValidator

if 'ANDROID_ARGUMENT' in os.environ or 'P4A_BOOTSTRAP' in os.environ:
    from jnius import autoclass
    from jnius import *
    FFMPEG_BINARY = autoclass('com.sahib.pyff.ffpy')
else:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()


def extract_audio(input_path: str, output_path: str = "./audio.mp3", output_format: str = "mp3",
                  start_time: str = "00:00:00",
                  duration: float = None,
                  overwrite: bool = False):
    validator = AudioExtractValidator(input_path, output_path, output_format, duration, start_time, overwrite)
    platform = None
    if 'ANDROID_ARGUMENT' in os.environ or 'P4A_BOOTSTRAP' in os.environ:
        platform = 'android'
    elif os.name == 'nt':
        platform = 'win'
    android_local = bool(platform == "android")
    duration_local = False

    result = validator.validate()
    cleaned_input_path = result["input_path"]
    cleaned_output_path = result["output_path"]
    cleaned_output_format = result["output_format"]
    cleaned_start_time = result["start_time"]

    if not android_local:
        command = [FFMPEG_BINARY,
                   '-i', cleaned_input_path,
                   '-ss', cleaned_start_time,
                   '-f', cleaned_output_format,
                   '-y', cleaned_output_path]

    if cleaned_duration := result["duration"]:
        duration_local = True
        if not android_local:
            command.insert(3, "-t")
            command.insert(4, cleaned_duration)

    if platform == "win":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=si)
    elif not android_local:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    else:
        print('Running android FFMPEG')
        if not duration_local:
            command = f'-i "{cleaned_input_path}" -ss {cleaned_start_time} -f {cleaned_output_format} -y "{cleaned_output_path}"'
        else:
            command = f'-i "{cleaned_input_path}" -ss {cleaned_start_time} -t {cleaned_duration} -f {cleaned_output_format} -y "{cleaned_output_path}"'
        d = FFMPEG_BINARY.Run(str(command))
        print(d)
    if type(result) != dict:
        if result.returncode == 0:
            return f"Success : audio file has been saved to \"{cleaned_output_path}\"."
        error = result.stderr.decode().strip().split("\n")[-1]
        return f"Failed : {error}."

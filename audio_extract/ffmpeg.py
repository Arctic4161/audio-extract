# Other modules
import subprocess
import platform
from kivy import platform
android_local = False
duration_local = False

# Local modules
from audio_extract.validators import AudioExtractValidator

if platform != "android":
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
    print(FFMPEG_BINARY)
else:
    android_local = True
    from jnius import autoclass
    from jnius import *
    FFMPEG_BINARY = autoclass('com.sahib.pyff.ffpy')


def extract_audio(input_path: str, output_path: str = "./audio.mp3", output_format: str = "mp3",
                  start_time: str = "00:00:00",
                  duration: float = None,
                  overwrite: bool = False):
    validator = AudioExtractValidator(input_path, output_path, output_format, duration, start_time, overwrite)
    result = validator.validate()

    cleaned_input_path = result["input_path"]
    cleaned_output_path = result["output_path"]
    cleaned_output_format = result["output_format"]
    cleaned_start_time = result["start_time"]
    if android_local is False:
        print(android_local)
        command = [FFMPEG_BINARY,
                   '-i', cleaned_input_path,
                   '-ss', cleaned_start_time,
                   '-f', cleaned_output_format,
                   '-y', cleaned_output_path]
    if cleaned_duration := result["duration"]:
        duration_local = True
        if android_local is False:
            command.insert(3, "-t")
            command.insert(4, cleaned_duration)

    if platform == "win":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=si)
    if android_local is False:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    else:
        if duration_local is False:
            FFMPEG_BINARY.Run(str(
                f'-i {cleaned_input_path} -ss {cleaned_start_time} -f {cleaned_output_format} -y {cleaned_output_path}'))
        else:
            FFMPEG_BINARY.Run(str(
                f'-i {cleaned_input_path} -ss {cleaned_start_time} -t {cleaned_duration} -f {cleaned_output_format} -y {cleaned_output_path}'))

    if result.returncode == 0:
        print(f"Success : audio file has been saved to \"{cleaned_output_path}\".")
    error = result.stderr.decode().strip().split("\n")[-1]
    return f"Failed : {error}."

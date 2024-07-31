# Other modules
import subprocess
import imageio_ffmpeg
import platform

# Local modules
from audio_extract.validators import AudioExtractValidator

FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()


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
    command = [FFMPEG_BINARY,
               '-i', cleaned_input_path,
               '-ss', cleaned_start_time,
               '-f', cleaned_output_format,
               '-y', cleaned_output_path]

    if cleaned_duration := result["duration"]:
        command.insert(3, "-t")
        command.insert(4, cleaned_duration)

    if platform.system() == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=si)
    else:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    if result.returncode == 0:
        return f"Success : audio file has been saved to \"{cleaned_output_path}\"."
    error = result.stderr.decode().strip().split("\n")[-1]
    return f"Failed : {error}."

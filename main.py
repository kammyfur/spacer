import argparse
import os
from constants import *
import shutil
import subprocess
import json

parser = argparse.ArgumentParser(
    prog='surrounder',
    description='Turning stereo music into surround',
    epilog='Copyright (c) Equestria.dev Developers')

parser.add_argument('input')
parser.add_argument('scene')
parser.add_argument('-o', '--output')

args = _args = parser.parse_args()

if not os.path.exists(args.input):
    print(f'Input file {args.input} not found')
    exit(1)

if os.path.isdir(args.input):
    print(f"Notice: {args.input} is a directory, using the first file in this directory as the reference input.")
    args.input = list(os.scandir(args.input))[0].path

if not os.path.exists(args.scene):
    print(f'Scene file {args.scene} not found')
    exit(1)

if args.output is not None and os.path.exists(args.output):
    print(f'Output file {args.output} already exists')
    exit(1)

with open(args.scene, 'r') as f:
    file = f.read()
    constants = sorted(list(Constants.items()), key=lambda x: len(x[0]), reverse=True)

    for (name, value) in constants:
        file = file.replace(name, str(value))

    lines = list(filter(lambda x: x.strip() != "" and not x.strip().startswith("'"), file.splitlines()))

if not lines[0].startswith("%Srdr-"):
    print("Invalid signature in scene file")
    exit(1)

version = lines[0].split("-")[1]
print(f"Surrounder Scene version: {version}")

if version not in Versions:
    print(f"This version of Surrounder does not support this Scene file. Supported versions: {', '.join(Versions)}")
    exit(1)

operations = []

for line in lines[1:]:
    operation_name = line.split(":")[0]
    parameters = list(map(lambda x: x.strip(), line.split(":")[1].split(";")))
    operations.append((operation_name, parameters))

channels = 0
bit_depth = 0
sample_rate = 0
sample_format = "s16"
layout = None

if os.path.exists("./srdr_work"):
    shutil.rmtree('./srdr_work')
os.mkdir('./srdr_work')
os.mkdir('./srdr_work/channels')

input_metadata = json.loads(subprocess.run([
    "ffprobe",
    "-v",
    "quiet",
    "-print_format",
    "json",
    "-show_format",
    "-show_streams",
    args.input
], stdout=subprocess.PIPE).stdout)

streams = list(filter(lambda x: x['codec_type'] == "audio", input_metadata['streams']))

if len(streams) < 1:
    print("The input file does not contain audio streams.")
    exit(1)

if len(streams) > 1:
    print("Warning: The input file contains multiple audio streams, only the first one will be used.")
    exit(1)

source = streams[0]
if 'bit_rate' in source:
    print(f"Input: {source['codec_long_name']}, "
          f"{int(source['sample_rate']) / 1000} kHz, "
          f"{int(source['bit_rate']) / 1000} kbps, "
          f"{source['duration']} seconds")
else:
    print(f"Input: {source['codec_long_name']}, "
          f"{int(source['sample_rate']) / 1000} kHz, "
          f"{source['duration']} seconds")

for (name, parameters) in operations:
    match name:
        case "Chs":
            if len(parameters) != 3:
                print(f"Expected 3 parameters but got {len(parameters)}.")
                exit(2)

            try:
                channels = int(parameters[0])

                if not 2 < channels < 65536:
                    print(f"Invalid number of channels {channels}, there must be between 3 and 65535 channels.")
                    exit(2)

                print(f"Channels: {channels}")
            except ValueError:
                print(f"Invalid number for channel number: {parameters[0]}")
                exit(2)

            try:
                bit_depth = int(parameters[1])

                if bit_depth != 16 and bit_depth != 24 and bit_depth != 32:
                    print(f"Invalid bit depth {bit_depth}, bit depth must be 16, 24 or 32.")
                    exit(2)

                match bit_depth:
                    case 16:
                        sample_rate = "s16"
                    case 24:
                        sample_rate = "s32p"
                    case 32:
                        sample_rate = "s32"

                print(f"Bit depth: {bit_depth} bit")
            except ValueError:
                print(f"Invalid number for bit depth: {parameters[1]}")
                exit(2)

            try:
                sample_rate = int(parameters[2])

                if not 22050 <= sample_rate <= 384000:
                    print(f"Invalid sample rate {sample_rate}, sample rate must be between 22050 and 384000 Hz.")
                    exit(2)

                print(f"Sample rate: {sample_rate} Hz ({sample_rate / 1000} kHz)")
            except ValueError:
                print(f"Invalid number for bit depth: {parameters[1]}")
                exit(2)

            print("Processing input...")

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", f"{_args.input}",
                "-ar", f"{sample_rate}",
                "-c:a", f"pcm_s{bit_depth}le",
                f"./srdr_work/input.wav"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            for i in range(channels):
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-f", "lavfi",
                    "-i", f"anullsrc=channel_layout=mono:sample_rate={sample_rate}",
                    "-t", f"{source['duration']}",
                    "-c:a", f"pcm_s{bit_depth}le",
                    f"./srdr_work/channels/{i}.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        case "Sep":
            if len(parameters) != 1:
                print(f"Expected 1 parameter but got {len(parameters)}.")
                exit(2)

            if not os.path.exists(f"./srdr_work/input.wav"):
                print(f"Separation is not ready: not configured.")
                exit(2)

            args = ["--float32", "-n", "htdemucs_6s", "-o", "./srdr_work/stems_tmp"]

            try:
                stem_format = int(parameters[0])
            except ValueError:
                print(f"Invalid stem format value: {parameters[0]}")
                exit(2)

            if stem_format == -2:
                if not os.path.exists(f"./stems"):
                    print("Could not find stems in a 'stems' folder.")
                    exit(2)

                shutil.copytree(f"./stems", f"./srdr_work/stems")
            elif stem_format == -1:
                pass
            elif stem_format != 0:
                match stem_format:
                    case 1:
                        print("Isolating vocals")
                        args += ["--two-stems", "vocals"]
                    case 2:
                        print("Isolating bass")
                        args += ["--two-stems", "bass"]
                    case 3:
                        print("Isolating piano")
                        args += ["--two-stems", "piano"]
                    case 4:
                        print("Isolating guitar")
                        args += ["--two-stems", "guitar"]
                    case 5:
                        print("Isolating drums")
                        args += ["--two-stems", "drums"]
                    case 6:
                        print("Isolating other")
                        args += ["--two-stems", "other"]
                    case _:
                        print(f"Invalid separation configuration: {stem_format}")
                        exit(2)

            args += ["./srdr_work/input.wav"]

            if stem_format > -1:
                import demucs.separate
                print("Separating using machine learning, this might take a while.")
                demucs.separate.main(args)
                os.rename("./srdr_work/stems_tmp/htdemucs_6s/input", "./srdr_work/stems")
                shutil.rmtree('./srdr_work/stems_tmp')
            elif stem_format == -1:
                os.mkdir("./srdr_work/stems")
                subprocess.run([
                    "sox",
                    "./srdr_work/input.wav",
                    "./srdr_work/stems/other.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run([
                    "sox",
                    "./srdr_work/input.wav",
                    "./srdr_work/stems/vocals.wav",
                    "highpass", "300",
                    "lowpass", "3500"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists("./srdr_work/stems/vocals.wav"):
                os.rename("./srdr_work/stems/vocals.wav", "./srdr_work/stems/1.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/1.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/8.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/9.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("./srdr_work/stems/bass.wav"):
                os.rename("./srdr_work/stems/bass.wav", "./srdr_work/stems/2.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/2.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/10.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/11.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("./srdr_work/stems/piano.wav"):
                os.rename("./srdr_work/stems/piano.wav", "./srdr_work/stems/3.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/3.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/12.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/13.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("./srdr_work/stems/guitar.wav"):
                os.rename("./srdr_work/stems/guitar.wav", "./srdr_work/stems/4.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/4.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/14.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/15.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("./srdr_work/stems/drums.wav"):
                os.rename("./srdr_work/stems/drums.wav", "./srdr_work/stems/5.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/5.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/16.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/17.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("./srdr_work/stems/other.wav"):
                os.rename("./srdr_work/stems/other.wav", "./srdr_work/stems/6.wav")
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/stems/6.wav",
                    "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                    "-map", "[left]",
                    "./srdr_work/stems/18.wav",
                    "-map", "[right]",
                    "./srdr_work/stems/19.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run([
                "sox",
                "./srdr_work/input.wav",
                "./srdr_work/stems/7.wav",
                "remix", "1,2",
                "lowpass", "120"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", "./srdr_work/stems/7.wav",
                "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                "-map", "[left]",
                "./srdr_work/stems/20.wav",
                "-map", "[right]",
                "./srdr_work/stems/21.wav"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        case "Map":
            if len(parameters) != 3:
                print(f"Expected 3 parameters but got {len(parameters)}.")
                exit(2)

            try:
                stem = int(parameters[0])
            except ValueError:
                print(f"Invalid stem value: {parameters[0]}")
                exit(2)

            try:
                channel = int(parameters[1])
            except ValueError:
                print(f"Invalid channel value: {parameters[1]}")
                exit(2)

            try:
                gain = float(parameters[2])
            except ValueError:
                print(f"Invalid gain value: {parameters[2]}")
                exit(2)

            if not os.path.exists(f"./srdr_work/channels/{channel}.wav"):
                print(f"Invalid or nonexistent channel: {channel}")
                exit(2)

            if not os.path.exists(f"./srdr_work/stems/{stem}.wav"):
                print(f"Invalid or nonexistent stem: {stem}")
                exit(2)

            if stem < 8:
                print(f"Stem {stem} is stereo and cannot be mapped to a channel.")
                exit(2)

            if layout is not None:
                print(f"Mapping: Stem {stem} ({value_to_constant(stem, 'STEMS_')}) -> Channel {channel} ({layout[channel]})")
            else:
                print(f"Mapping: Stem {stem} ({value_to_constant(stem, 'STEMS_')}) -> Channel {channel}")

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", f"./srdr_work/stems/{stem}.wav",
                "-af", f"volume={gain}",
                f"./srdr_work/stems/{stem}_2.wav"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", f"./srdr_work/channels/{channel}.wav",
                "-i", f"./srdr_work/stems/{stem}_2.wav",
                "-filter_complex", "amix=inputs=2:duration=longest",
                f"./srdr_work/channels/{channel}_2.wav",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.unlink(f"./srdr_work/channels/{channel}.wav")
            os.unlink(f"./srdr_work/stems/{stem}_2.wav")
            os.rename(f"./srdr_work/channels/{channel}_2.wav", f"./srdr_work/channels/{channel}.wav")
        case "Dis":
            if version == "1.0":
                print(f"This Scene file does not support the Dis instruction.")
                exit(2)

            if len(parameters) != 2:
                print(f"Expected 2 parameters but got {len(parameters)}.")
                exit(2)

            try:
                channel1 = int(parameters[0])
            except ValueError:
                print(f"Invalid channel value: {parameters[0]}")
                exit(2)

            try:
                channel2 = int(parameters[1])
            except ValueError:
                print(f"Invalid channel value: {parameters[1]}")
                exit(2)

            if not os.path.exists(f"./srdr_work/channels/{channel1}.wav"):
                print(f"Invalid or nonexistent channel: {channel1}")
                exit(2)

            if not os.path.exists(f"./srdr_work/channels/{channel2}.wav"):
                print(f"Invalid or nonexistent channel: {channel2}")
                exit(2)

            if layout is not None:
                print(f"Distance: Channel {channel1} ({layout[channel1]}) <-> Channel {channel2} ({layout[channel2]})")
            else:
                print(f"Distance: Channel {channel1} <-> Channel {channel2}")

            subprocess.run([
                "sox",
                "-M",
                f"./srdr_work/channels/{channel1}.wav",
                f"./srdr_work/channels/{channel2}.wav",
                f"./srdr_work/channels/_2.wav",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.run([
                "sox",
                f"./srdr_work/channels/_2.wav",
                f"./srdr_work/channels/_3.wav",
                "remix", "1v-0.8718,2v0.4898", "1v0.4898,2v-0.8718",
                "delay", "0.15"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", "./srdr_work/channels/_3.wav",
                "-filter_complex", "[0:0]pan=1|c0=c0[left];[0:0]pan=1|c0=c1[right]",
                "-map", "[left]",
                f"./srdr_work/channels/{channel1}_2.wav",
                "-map", "[right]",
                f"./srdr_work/channels/{channel2}_2.wav",
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.unlink(f"./srdr_work/channels/{channel1}.wav")
            os.unlink(f"./srdr_work/channels/{channel2}.wav")
            os.unlink(f"./srdr_work/channels/_2.wav")
            os.unlink(f"./srdr_work/channels/_3.wav")
            os.rename(f"./srdr_work/channels/{channel1}_2.wav", f"./srdr_work/channels/{channel1}.wav")
            os.rename(f"./srdr_work/channels/{channel2}_2.wav", f"./srdr_work/channels/{channel2}.wav")
        case "Lay":
            layout = parameters

            for channel in layout:
                if channel not in Channels:
                    print(f"Invalid audio channel label: {channel}")
                    exit(2)

            print(f"Channel layout: {', '.join(layout)}")
        case "Out":
            if len(parameters) != 1:
                print(f"Expected 1 parameter but got {len(parameters)}.")
                exit(2)

            if not os.path.exists(f"./srdr_work/input.wav"):
                print(f"Output is not ready: not configured.")
                exit(2)

            try:
                output_format = int(parameters[0])
            except ValueError:
                print(f"Invalid output format value: {parameters[0]}")
                exit(2)

            match output_format:
                case 0:  # WAV
                    print("Output format: RIFF WAVE")
                    extension = ".wav"
                case 1:  # FLAC
                    print("Output format: Free Lossless Audio Codec")
                    if channels > 8:
                        print(f"Free Lossless Audio Codec only supports up to 8 channels, but {channels} are used.")
                        exit(2)
                    extension = ".flac"
                case 2:  # AC-3
                    print("Output format: Dolby AC-3")
                    if channels > 8:
                        printf(f"Dolby AC-3 only supports up to 8 channels, but {channels} are used.")
                        exit(2)
                    extension = ".ac3"
                case 3:  # E-AC-3
                    print("Output format: Dolby E-AC-3")
                    if channels > 16:
                        printf(f"Dolby E-AC-3 only supports up to 16 channels, but {channels} are used.")
                        exit(2)
                    extension = ".eac3"
                case 4:  # AC-4
                    print("Output format: Dolby AC-4")
                    if channels > 16:
                        printf(f"Dolby AC-4 only supports up to 16 channels, but {channels} are used.")
                        exit(2)
                    extension = ".ac4"
                case 5:  # AC-4
                    print("Output format: Advanced Audio Coding")
                    if channels > 48:
                        printf(f"Advanced Audio Coding only supports up to 48 channels, but {channels} are used.")
                        exit(2)
                    extension = ".m4a"
                case _:
                    print(f"Invalid or unsupported output format: {output_format}")
                    exit(2)

            args = ["sox", "-M"]

            for i in range(channels):
                args.append(f"./srdr_work/channels/{i}.wav")

            args += [
                "-r", str(sample_rate),
                "-b", str(bit_depth),
                f"./srdr_work/output.wav"
            ]

            subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if layout is not None:
                audio_filter = "join=inputs=1:channel_layout="

                for channel in layout:
                    audio_filter += f"{channel}+"

                audio_filter = audio_filter[:-1]
                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i", "./srdr_work/output.wav",
                    "-filter_complex", audio_filter,
                    "./srdr_work/output_2.wav"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                os.unlink("./srdr_work/output.wav")
                os.rename("./srdr_work/output_2.wav", "./srdr_work/output.wav")

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", "./srdr_work/output.wav",
                f"./srdr_work/final{extension}"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        case _:
            print(f"Invalid or unsupported command in this version: {name}")
            exit(2)

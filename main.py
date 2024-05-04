import os
import sys
import subprocess
import json
import time

#Function to get the Video Infomation HDR or SDR using FFprobe
def get_video_color_transfer(input_file):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "v:0", input_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        stream_info = json.loads(result.stdout)
        if "streams" in stream_info and len(stream_info["streams"]) > 0:
            color_transfer = stream_info["streams"][0].get("color_primaries")
            return color_transfer
    else:
        print("Error executing ffprobe command:")
        print(result.stderr)
    return None

#Encode the Video into different variant based on input parameter and insert the image for SDR format
def transcode_video(input_file, output_file, resolution, overlay_image):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-i', overlay_image,
        '-filter_complex', f"[1:v]scale=-1:'ih*0.05':flags=lanczos[wm];[0:v][wm]overlay=W-w-10:H-h-10,format=yuv420p,scale=-2:{resolution}",
        '-c:v', 'libx265',
        '-crf', '28',
        '-preset', 'medium',
        '-hide_banner',
        output_file
    ]
    subprocess.run(command)

#Encode the Video into different variant based on input parameter and insert the image for HDR format
def transcode_video_HDR(input_file, output_file, resolution, overlay_image):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-i', overlay_image,
        '-filter_complex', f"[1:v]scale=120:120:flags=lanczos[wm];[0:v][wm]overlay=W-w-10:10,format=yuv420p,scale=-2:{resolution}",
        '-c:v', 'libx265',
        '-crf', '28',
        '-preset', 'medium',
        '-hide_banner',
        output_file
    ]
    subprocess.run(command)

#Encode the Video into different variant based on input parameter and insert the image
#Covert the HDR video into SDR format
def transcode_video_to_SDR(input_file, output_file, resolution, overlay_image):
    command = [
    'ffmpeg', 
    '-i', input_file, 
    '-i', overlay_image,
    '-filter_complex', f"[0:v]zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p[v];[1:v]scale=-1:\'ih*0.05\':flags=lanczos[wm];[v][wm]overlay=W-w-10:H-h-10,scale=-2:{resolution}",
    '-c:v', 'libx265', 
    '-crf', '28', 
    '-preset', 'fast', 
    '-tune', 'fastdecode',
    '-c:a', 'copy', 
    output_file
    ]
    subprocess.run(command)


#Fragmenting an MP4 file involves breaking it into smaller
def frag_dash(output_file,segment_duration=7000):
    command = [
        'mp4fragment',
        '--fragment-duration', str(segment_duration),
        output_file,
        'temp.mp4'
    ]
    subprocess.run(command)

#Using mp4dash preparing MP4 content for DASH streaming format
def package_dash(output_dir):
    command = [
        'mp4dash',
        '-o', output_dir,
        'temp.mp4'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error:", stderr.decode())
    else:
        print("Package created successfully.")
    os.remove('temp.mp4')

#main func Usage python script.py sdr_sample_vide.mp4
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py sdr_sample_vide.mp4")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print("Error: Input file does not exist.")
        sys.exit(1)

    color_primaries = get_video_color_transfer(input_file)
    segment_duration = 7000
    if color_primaries=="bt2020":
        overlay_image = "green_circle.png"
        resolutions = {'360p': 360, '480p': 480, '720p': 720, '1080p': 1080}
        for resolution, height in resolutions.items():
            output_file = f"{os.path.splitext(input_file)[0]}_{resolution}.mp4"
            transcode_video_HDR(input_file, output_file, height, overlay_image)
            output_dir = f"{resolution}_HDR_dash"
            frag_dash(output_file)
            package_dash(output_dir)
            os.remove(output_file)  #Remove the temporary MP4 file after packaging
        overlay_image = "white_circle.png"
        resolutions = {'360p': 360, '480p': 480, '720p': 720, '1080p': 1080}
        for resolution, height in resolutions.items():
            output_file = f"{os.path.splitext(input_file)[0]}_{resolution}.mp4"
            transcode_video_to_SDR(input_file, output_file, height, overlay_image)
            output_dir = f"{resolution}_SDR_dash"
            frag_dash(output_file, segment_duration)
            package_dash(output_dir)
            os.remove(output_file) #Remove the temporary MP4 file after packaging
    else:
        overlay_image = "white_circle.png"
        resolutions = {'360p': 360, '480p': 480, '720p': 720, '1080p': 1080}
        for resolution, height in resolutions.items():
            output_file = f"{os.path.splitext(input_file)[0]}_{resolution}.mp4"
            transcode_video(input_file, output_file, height, overlay_image)
            output_dir = f"{resolution}_dash"
            frag_dash(output_file, segment_duration)
            package_dash(output_dir)
            os.remove(output_file)  # Remove the temporary MP4 file after packaging

if __name__ == "__main__":
    main()

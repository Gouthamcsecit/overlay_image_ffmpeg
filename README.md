# Video Transcoding and Packaging Script

This script facilitates transcoding of videos into different variants and packaging them for DASH streaming format.

## Requirements
* FFMPEG
* Bento4

## Usage 

```
python main.py hdr_sample_video.mp4
```

## Features

* Transcodes videos into different resolutions and formats.
* Inserts overlay images for both HDR and SDR formats.
* Converts HDR videos into SDR format.
* Fragments MP4 files for DASH streaming.
* Packages MP4 content for DASH streaming format.

## Functions
1. get_video_color_transfer(input_file)
    * Retrieves video information regarding color_primaries (HDR or SDR) using FFprobe.

2. transcode_video(input_file, output_file, resolution, overlay_image)
    * Encodes the video into different variants based on input parameters and inserts an overlay image for SDR format.
3. transcode_video_HDR(input_file, output_file, resolution, overlay_image)
    * Encodes the video into different variants based on input parameters and inserts an overlay image for HDR format.
4. transcode_video_to_SDR(input_file, output_file, resolution, overlay_image)
    * Encodes the video into different variants based on input parameters and inserts an overlay image. 

    * Converts HDR video into SDR format.
5. frag_dash(output_file, segment_duration=7000)
    * Fragments an MP4 file into smaller segments for DASH streaming.
6. package_dash(output_dir)
    * Prepares MP4 content for DASH streaming format.

## Main Function
* Parses command-line arguments to determine input file.

* Determines whether the input video is in HDR or SDR format.

* Transcodes the video accordingly into various resolutions and formats.

* Fragments and packages the transcoded videos for DASH streaming.

### NOTE
* This script is supported for both HDR and SDR formats.

from pathlib import Path
import subprocess

# Project paths
BASE_DIR = Path(__file__).resolve().parent

SOURCE_DIR = BASE_DIR / "dataset_selected"
OUTPUT_DIR = BASE_DIR / "dataset_selected_h264"

# FFmpeg executable
FFMPEG = Path(
    r"C:\Users\nm\Downloads\ffmpeg-9.0.2-essentials_build\bin\ffmpeg.exe"
)

# Find all MP4 videos
videos = list(SOURCE_DIR.rglob("*.mp4"))

print(f"Found {len(videos)} videos.")

success = 0
failed = []

for index, video in enumerate(videos, start=1):

    # Preserve the original folder structure
    relative_path = video.relative_to(SOURCE_DIR)
    output_path = OUTPUT_DIR / relative_path

    # Create the required output folder
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        str(FFMPEG),
        "-y",
        "-i", str(video),
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(output_path)
    ]

    print(f"\n[{index}/{len(videos)}] Converting: {relative_path}")

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        success += 1
        print("Successfully converted!")
    else:
        failed.append(str(relative_path))
        print("Conversion failed!")

print("\n========== SUMMARY ==========")
print(f"Total videos: {len(videos)}")
print(f"Successfully converted: {success}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed files:")
    for file in failed:
        print(file)

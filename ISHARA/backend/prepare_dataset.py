
from pathlib import Path
import shutil

# Project paths
project_dir = Path(__file__).resolve().parent.parent

source_dir = project_dir / "dataset - rebirth copy"
output_dir = project_dir / "dataset_selected"

output_dir.mkdir(exist_ok=True)

selected_count = 0
empty_folders = []

for word_folder in source_dir.iterdir():

    if not word_folder.is_dir():
        continue

    videos = list(word_folder.glob("*.mp4"))

    if not videos:
        empty_folders.append(word_folder.name)
        continue

    # Select the largest video
    selected_video = max(videos, key=lambda file: file.stat().st_size)

    # Create one folder per word
    destination_folder = output_dir / word_folder.name
    destination_folder.mkdir(exist_ok=True)

    # Copy selected video
    shutil.copy2(
        selected_video,
        destination_folder / selected_video.name
    )

    selected_count += 1

    print(f"{word_folder.name}: {selected_video.name}")

print("\nDataset preparation completed!")
print("Selected words:", selected_count)
print("Empty folders:", empty_folders)

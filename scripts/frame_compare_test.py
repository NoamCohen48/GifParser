import os
from PIL import Image, ImageSequence


def compare_frames(original_dir: str, result_dir: str):
    for original_file in os.listdir(original_dir):
        if original_file.endswith(".gif"):
            result_file = "result_" + original_file
            original_path = os.path.join(original_dir, original_file)
            result_path = os.path.join(result_dir, result_file)

            if os.path.isfile(result_path):
                original_frames = ImageSequence.Iterator(Image.open(original_path))
                result_frames = ImageSequence.Iterator(Image.open(result_path))

                for frame_num, (original_frame, result_frame) in enumerate(zip(original_frames, result_frames), start=1):
                    if original_frame.tobytes() != result_frame.tobytes():
                        print(f"Differences found in frame {frame_num} of {original_file} and {result_file}")
                else:
                    print(f"No differences found between frames in {original_file} and {result_file}")
            else:
                print(f"Result file not found for {original_file}")


if __name__ == '__main__':
    original_gif_dir = "../Test_gifs"
    result_gif_dir = "../results"
    compare_frames(original_gif_dir, result_gif_dir)

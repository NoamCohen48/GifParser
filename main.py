# from decoder import decode_gif
# from gif_objects import Gif
# from writer import write_gif
#
#
# def main(filename: str, *, show_image: bool = False):
#     with open(filename, "rb") as gif_file:
#         gif: Gif = decode_gif(gif_file)
#         print("decoded")
#
#     if show_image:
#         print("showing images (first 5)")
#         for image in gif.images[:5]:
#             image.img.show()
#
#     res = write_gif(gif)
#     with open("result.gif", "wb") as f:
#         res.to_file(f)
#     print("saved")
#
#
# if __name__ == '__main__':
#     main("gif_tests/test4.gif", show_image=False)
import os
from decoder import decode_gif
from gif_objects import Gif
from writer import write_gif


def main(gif_dir: str, *, show_image: bool = False):
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)

    for filename in os.listdir(gif_dir):
        if filename.endswith(".gif"):
            gif_path = os.path.join(gif_dir, filename)
            with open(gif_path, "rb") as gif_file:
                try:
                    gif: Gif = decode_gif(gif_file)
                    print(f"Decoded {filename} successfully")
                    print(f"Number of images at {filename}: {len(gif.images)}")
                except:
                    print(f"Failed to decode {filename}")
                    continue

            if show_image:
                print(f"Showing images of {filename} (first 5)")
                for image in gif.images[:5]:
                    image.img.show()

            try:
                res = write_gif(gif)
                result_path = os.path.join(result_dir, f"result_{filename}")
                with open(result_path, "wb") as f:
                    res.to_file(f)
                print(f"Saved result of {filename} as {result_path}")
            except:
                print(f"Failed to write the result for {filename}")


if __name__ == '__main__':
    main("Test_gifs", show_image=False)


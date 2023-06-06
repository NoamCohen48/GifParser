import pickle
from pathlib import Path
import time

from decoder import decode_gif
from gif_objects import Gif
from writer import write_gif


def load_gif_from_pickle(path: Path) -> Gif:
    with open(path.with_suffix('.pickle'), 'rb') as pickle_file:
        gif = pickle.load(pickle_file)
    print("loaded from pickle")
    return gif


def save_gif_to_pickle(path: Path, gif: Gif) -> None:
    with open(path.with_suffix('.pickle'), 'wb') as pickle_file:
        pickle.dump(gif, pickle_file)
    print("saved new pickle")


def read_gif(path: Path, create_images: bool) -> Gif:
    with open(path.with_suffix(".gif"), "rb") as gif_file:
        gif = decode_gif(gif_file, create_images)
    print("decoded gif")
    return gif


def write_gif2(path: Path, gif: Gif) -> None:
    with open(path.with_stem(f"{path.stem}-result").with_suffix(".gif"), "wb") as gif_file:
        res = write_gif(gif)
        res.to_file(gif_file)
    print("wrote gif")


def main(filename: str, *, show_image: bool = False, create_images: bool = False):
    path = Path(filename)

    if path.with_suffix(".pickle").exists():
        choice = input("would you like to open saved pickle file? [y/n]: ")
        if choice == "y":
            gif = load_gif_from_pickle(path)
        elif choice == "n":
            gif = read_gif(path, create_images)
            save_gif_to_pickle(path, gif)
        else:
            print("write y or n in lower case, bro")
            return
    else:
        gif = read_gif(path, create_images)
        save_gif_to_pickle(path, gif)

    if show_image:
        print("showing images (first 5)")
        for image in gif.images[:5]:
            image.img.show()

    write_gif2(path, gif)


if __name__ == '__main__':
    start_time = time.time()

    for i in ["all disposal 2 and shifted.gif"]:
        main("gif_tests/" + i, show_image=False, create_images=True)

    # Your program code here

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Program execution time: {execution_time} seconds")
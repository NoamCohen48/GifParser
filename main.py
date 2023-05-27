from decoder import decode_gif
from gif_objects import Gif
from writer import write_gif


def main(filename: str, *, show_image: bool = False):
    with open(filename, "rb") as gif_file:
        gif: Gif = decode_gif(gif_file)
        print("decoded")

    if show_image:
        print("showing images (first 5)")
        for image in gif.images[:5]:
            image.img.show()

    with open("result.gif", "wb") as f:
        res = write_gif(gif)
        res.to_file(f)
        print("saved")


if __name__ == '__main__':
    main("gif_tests/test4.gif", show_image=False)

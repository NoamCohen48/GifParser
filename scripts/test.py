import io
import pickle
from pathlib import Path
from typing import Literal

import writer
from decoder import decode_gif
from gif_objects import Gif


def check_write(path: Path):
    with open(path.with_suffix('.pickle'), 'rb') as pickle_file:
        saved_gif: Gif = pickle.load(pickle_file)

    saved_gif_bytes = writer.write_gif(saved_gif)
    as_io = io.BytesIO(saved_gif_bytes._stream.bytes)
    gif = decode_gif(as_io)

    saved_gif.print_diff(gif)
    print(f"checked write for {path.stem}")


def check_read(path: Path):
    with open(path.with_suffix('.pickle'), 'rb') as pickle_file:
        saved: Gif = pickle.load(pickle_file)

    with open(path, "rb") as gif_file:
        current: Gif = decode_gif(gif_file)

    print(f"file {path.stem} correctness: {current == saved}")




def save_file(path: Path):
    try:
        with open(path, "rb") as gif_file:
            gif: Gif = decode_gif(gif_file)

        with open(path.with_suffix('.pickle'), 'wb') as pickle_file:
            pickle.dump(gif, pickle_file)

        print(f"{path.stem} was saved")
    except Exception as e:
        print(f"couldn't save {path.stem}")
        print(e)


def test_gifs(*, mode: Literal['save', 'check_read', 'check_write'], files: list[str] = None):
    if files or files == []:
        path_list = [Path('../gif_tests', str).with_suffix('.gif') for str in files]
    else:
        path_list = Path('../gif_tests/').rglob('*.gif')

    for path in path_list:
        if mode == 'check_read':
            if path.with_suffix('.pickle').exists():
                check_read(path)
            else:
                print(f"file {path.stem} has no pickle")

        if mode == 'check_write':
            if path.with_suffix('.pickle').exists():
                check_write(path)
            else:
                print(f"file {path.stem} has no pickle")
        elif mode == 'save':
            save_file(path)


if __name__ == '__main__':
    test_gifs(mode='save', files=['giphy2'])

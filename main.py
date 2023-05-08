from pprint import pprint
import math
from decoder import decode_gif
from gif_objects import Gif
from lzw import *
from decoder import *
import bitstring


def index_from_data(image_data, color_table):
    size_of_index = math.ceil(math.log(len(color_table), 2)) + 1
    indexes = [convert_int_to_bits(color_table.index(color), size_of_index) for color in image_data]
    res = b''.join(indexes)
    hex_string ='0x' + hex(int(res.decode('utf-8'), 2))[2:]
    return hex_string




def main():
    with open("gif_tests/test1.gif", "rb") as gif_file:
        gif: Gif = decode_gif(gif_file)
    image = gif.images[0]
    data = index_from_data(gif.images[0].image_data, gif.global_color_table)
    encode(data, len(gif.global_color_table))


if __name__ == '__main__':
    main()

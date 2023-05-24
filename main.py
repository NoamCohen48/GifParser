import pprint
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
    # hex_string ='0x' + hex(int(res.decode('utf-8'), 2))[2:]
    #
    binary_string = res.decode('utf-8')
    hex_string = '0x' + format(int(binary_string, 2), '0{0}x'.format(len(binary_string) // 4))

    return hex_string




def main():
    with open("gif_tests/test.gif", "rb") as gif_file:
        gif: Gif = decode_gif(gif_file)
    image = gif.images[0]

    #  create data as we want to get in the encode
    data = index_from_data(gif.images[0].image_data, gif.global_color_table)
    # calling encode
    encode_hex = encode(data, len(gif.global_color_table))

    full_len = len(encode_hex)/4
    #  convert data to hexa'
    hex_str = binascii.hexlify(int(encode_hex, 2).to_bytes((len(encode_hex) + 7) // 8, 'big')).decode()
    res = bytes.fromhex(hex_str)
    if full_len != len(hex_str):
        hex_str.zfill(int(full_len))

    # print(hex_str.upper())

    hex_string = "".join(["{:02x}".format(x) for x in image.image_compres_data])
    for i in range(max(len(hex_str), len(hex_string))):
        if hex_str[i] != hex_string[i]:
            print(i)

if __name__ == '__main__':
    main()
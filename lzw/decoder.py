import io
import math

from bitstring import ConstBitStream

MAX_WRITING_SIZE = 12

# the example we using here:
#       https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
#       https://giflib.sourceforge.net/whatsinagif/lzw_image_data.html

def initialize_code_table(color_table_size: int) -> dict[int,str]:
    """
    init dict which keys are int from 0 to size.
    @param color_table_size: size of color table
    @return:
    """

    # init table with dict, clear code and eof
    return {i: str(i) for i in range(color_table_size + 2)}


def get_decode_element(stream: ConstBitStream, reading_size: int) -> int:
    if stream.pos - reading_size < 0:
        reading_size = stream.pos

    stream.pos -= reading_size
    value: int = stream.read(f'uint{reading_size}')
    stream.pos -= reading_size
    return value


def index_to_binary(element: str, writing_size: int):
    return bytes(''.join([bin(int(val))[2:].zfill(writing_size) for val in element.split(',')]), 'utf-8')


def update_code_size_decode(table_size: int, code_size: int):
    if table_size == int(math.pow(2, code_size)) and code_size < MAX_WRITING_SIZE:
        return code_size + 1
    return code_size


def get_first_element(concats_colors: str):
    comma_index = concats_colors.find(",")
    if comma_index != -1:
        result = concats_colors[:comma_index]
    else:
        result = concats_colors
    return result


def lzw_decode(compressed_data: bytes, lzw_minimum_code_size: int):
    """
    using lzw algorithm for compress data ang gif images
    the table code look like this:
    _____|______
      0  |  '0'
      1  |  '1'
      2  |  '2'
      3  |  '3'
    ...
     297 | '3','89'
     """

    writing_size = lzw_minimum_code_size
    reading_size = writing_size + 1
    color_table_size = int(math.pow(2, lzw_minimum_code_size))
    table = initialize_code_table(color_table_size)
    reading_size = update_code_size_decode(len(table), reading_size)

    # add the start of reading
    clear_code = int(table[len(table) - 2])

    #  add the enf of reading
    end_of_information_code = int(table[(len(table) - 1)])

    stream = ConstBitStream(compressed_data[::-1])

    decompressed_data = io.BytesIO()

    stream.pos = stream.length
    curr_el = get_decode_element(stream, reading_size)
    # if the gif start with clear_code we need continue to the next value
    if curr_el == clear_code:
        curr_el = get_decode_element(stream, reading_size)

    decompressed_data.write(index_to_binary(table[curr_el], writing_size))
    while True:
        next_el = get_decode_element(stream, reading_size)
        if next_el == end_of_information_code:
            break
        if next_el == clear_code:
            table = initialize_code_table(color_table_size)
            reading_size = lzw_minimum_code_size + 1
            curr_el = get_decode_element(stream, reading_size)
            decompressed_data.write(index_to_binary(table[curr_el], writing_size))

            continue

        if next_el in table:
            k = get_first_element(table[next_el])
            decompressed_data.write(index_to_binary(table[next_el], writing_size))
        else:
            k = get_first_element(table[curr_el])
            decompressed_data.write(index_to_binary(table[curr_el] + "," + k, writing_size))

        table[len(table)] = table[curr_el] + "," + k
        reading_size = update_code_size_decode(len(table), reading_size)
        curr_el = next_el

    return decompressed_data.getvalue(), writing_size

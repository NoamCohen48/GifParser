import io
import math

import bitstring
from bitstring import ConstBitStream, BitArray
import binascii


# the example we using here:
#       https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
#       https://giflib.sourceforge.net/whatsinagif/lzw_image_data.html

def write_compressed_data(result: [str], code_size: int):
    output = ""
    for m in result:
        output += m.zfill(code_size)
    return bytes(output, "utf-8")


def insert_to_stream(stream: BitArray, value: int, bits: int) -> None:
    stream.prepend(f"uint:{bits}={value}")


def initialize_code_table(color_table_size, is_decode):
    # init table with dict, clear code and eof
    if is_decode:
        return {i: str(i) for i in range(color_table_size + 2)}
    else:
        return {str(i): i for i in range(color_table_size + 2)}


def update_code_size(table_size, code_size):
    """
    check if we need to increase the writing window if the table size +1 is representing binary more than the
    current writing window size
    :param table_size:
    :param writing_size:
    :return: writing_size:
    """
    if table_size >= int(math.pow(2, code_size)) + 1:
        return code_size + 1
    return code_size


def flip_data(compress_data):
    """
    flip the data doing reverse to the compressed data - ךooking at each element of size 8 bits

    :param compress_data:
    :return: fliped_data
    """
    fliped_data = ''
    length = len(compress_data) / 8
    for i in range(int(length)):
        fliped_data += compress_data[-8:]
        compress_data = compress_data[:-8]

    return fliped_data.encode("utf-8")


def get_encode_element(stream, reading_size):
    """
    the next element represent in as string number . the riding size in constant
    :param stream:
    :param reading_size:
    :return: element
    """
    value: int = stream.read(f"uint:{reading_size}")
    return str(value)


def fill_zero_bytes(compress_data):
    """
    fill the data with zero in start that will divide by 8 - for hexa representing
    :param: compress_data:
    :return: compress_data
    """
    if zero_fill := len(compress_data) % 8:
        compress_data = insert_to_stream(0, 8 - zero_fill) + compress_data
    return compress_data


def encode(uncompressed_data, color_table_size):
    """
    using lzw algorithm for compress data ang gif images
    the table code look like this:

    str   |  int
    __|___
      #0  |  0
      #1  |  1
      #2  |  2
      #3  |  3

    :param uncompressed_data:
    :param color_table_size:
    :return: compress_data:
    """
    # change data to be ConstBitStream object for reading
    # we got  1,1,1,1,1,2,2,.. that represent by '0x2492924.."
    stream = ConstBitStream(uncompressed_data)

    # the window size riding is the log of the size table plus 1
    # color table size +1 => it's for the end_of_information_code and clear_code,
    # (color table size +1) + 1 => it's for situations that the number isn't pow of two then we need added a bit for
    # riding the numbers (in our example = 3).
    # notice the reding size in constant - not change
    reading_size = math.ceil(math.log2(color_table_size)) + 1

    table = initialize_code_table(color_table_size, False)

    # if the next item in the table will need to be writen with more bit change now the writing size
    # because we're adding more indexes to the table, and now we need more bits to represent the numbers
    writing_size = update_code_size(len(table), reading_size)

    # add the start of reading (in our example = 4)
    clear_code = table[str(len(table) - 2)]
    #  add the enf of reading (in our example = 5)
    end_of_information_code = table[str(len(table) - 1)]
    compress_data = BitArray()
    #  add clear code according the reading size (in our example = 4)
    insert_to_stream(compress_data, clear_code, writing_size)

    length = stream.length

    # the first item
    curr_el = get_encode_element(stream, reading_size)

    while stream.pos != length:
        # reading the next item
        next_el = get_encode_element(stream, reading_size)
        current_and_next = curr_el + "," + next_el

        # if it is in the table continue
        if current_and_next in table:
            curr_el = current_and_next
        else:
            if len(table) == 4096:
                insert_to_stream(compress_data, table[curr_el], 12)
                insert_to_stream(compress_data, clear_code, 12)
                reading_size = math.ceil(math.log2(color_table_size)) + 1
                table = initialize_code_table(color_table_size, False)
                writing_size = update_code_size(len(table), reading_size)
                curr_el = next_el
                continue
            # add the new concat to the table
            table[current_and_next] = len(table)
            # write the compressed value to the output
            insert_to_stream(compress_data, table[curr_el], writing_size)

            # checking if to change the writing size
            writing_size = update_code_size(len(table), writing_size)
            curr_el = next_el

    # add the last element to the output
    insert_to_stream(compress_data, table[curr_el], writing_size)

    # add the end to the output - for inform that is the end ot the data
    insert_to_stream(compress_data, end_of_information_code, writing_size)

    # fill zeros to align pos to 8
    insert_to_stream(compress_data, 0, 8 - compress_data.len % 8)

    compress_data.byteswap()

    return compress_data.bytes


def get_decode_element(stream, reading_size) -> int:
    stream.pos -= reading_size
    value: int = stream.read(f'uint{reading_size}')
    stream.pos -= reading_size
    return value


def index_to_binary(element, writing_size):
    return bytes(''.join([bin(int(val))[2:].zfill(writing_size) for val in element.split(',')]), 'utf-8')


def fill_zero_hexa(hexa_data, binary_data_len):
    """
    fill the data with zero in start that will divide by 8 - for hexa representing
    :param hexa_data:
    :return: binary_data_len
    """
    while len(hexa_data[2:]) < binary_data_len / 4:
        hexa_data = '0x0' + hexa_data[2:]
    return hexa_data


def update_code_size1(table_size, code_size):
    """
    check if we need to increase the writing window if the table size +1 is representing binary more than the
    current writing window size
    :param table_size:
    :param writing_size:
    :return: writing_size:
    """
    if table_size == int(math.pow(2, code_size)) and code_size < 12:
        return code_size + 1
    return code_size


def get_first_element(concats_colors):
    comma_index = concats_colors.find(",")
    if comma_index != -1:
        result = concats_colors[:comma_index]
    else:
        result = concats_colors
    return result


def decode_lzw(compressed_data, lzw_minimum_code_size):
    """
    using lzw algorithm for compress data ang gif images
    the table code look like this:
    _____|______
      0  |  #0
      1  |  #1
      2  |  #2
      3  |  #3

    :param compressed_data:
    :param color_table_size:
    :return: compress_data:
    """
    writing_size = lzw_minimum_code_size
    reading_size = writing_size + 1
    color_table_size = math.pow(2, lzw_minimum_code_size)
    table = initialize_code_table(int(color_table_size), True)
    reading_size = update_code_size1(len(table), reading_size)

    # add the start of reading
    clear_code = int(table[len(table) - 2])

    #  add the enf of reading
    end_of_information_code = int(table[(len(table) - 1)])

    stream = ConstBitStream(compressed_data[::-1])

    # bits = bitstring.BitArray(compressed_data)
    # for bit_index in range(0, bits.length, 8):
    #     bits.reverse(bit_index, bit_index + 8)
    # stream2 = ConstBitStream(bits)

    stream.pos = stream.length
    first_element = get_decode_element(stream, reading_size)

    if first_element != clear_code:
        print("the image was corrupted")
        return -1

    decompressed_data = io.BytesIO()
    curr_el = get_decode_element(stream, reading_size)
    decompressed_data.write(index_to_binary(table[curr_el], writing_size))
    while True:
        next_el = get_decode_element(stream, reading_size)
        if next_el == end_of_information_code:
            break
        if next_el == clear_code:
            table = initialize_code_table(int(color_table_size), True)
            reading_size = lzw_minimum_code_size + 1
            curr_el = get_decode_element(stream, reading_size)
            decompressed_data.write(index_to_binary(table[curr_el], writing_size))

            continue

        if next_el in table:
            decompressed_data.write(index_to_binary(table[next_el], writing_size))
            k = get_first_element(table[next_el])
        else:
            k = get_first_element(table[curr_el])
            decompressed_data.write(index_to_binary(table[curr_el] + "," + k, writing_size))

        table[len(table)] = table[curr_el] + "," + k
        reading_size = update_code_size1(len(table), reading_size)
        curr_el = next_el

    return decompressed_data.getvalue(), writing_size

import math

from bitstring import ConstBitStream
import binascii


# the example we using here:
#       https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
#       https://giflib.sourceforge.net/whatsinagif/lzw_image_data.html

def write_compressed_data(result: [str], code_size: int):
    output = ""
    for m in result:
        output += m.zfill(code_size)
    return bytes(output, "utf-8")


def convert_int_to_bits(number, code_size):
    return bytes((bin(number)[2:]).zfill(code_size), 'utf-8')


def initialize_code_table(color_table_size, is_decode):
    """
    creating the base table for the known value
    :param color_table_size:
    :return: table
    """
    table_size = color_table_size
    table = {str(i): i for i in range(color_table_size)}
    # adding the number for clear code
    table[str(table_size)] = table_size
    table_size += 1
    # adding the number for end_of_information
    table[str(table_size)] = table_size
    table_size += 1

    # in decode we need to flip the table for the opposite process
    if is_decode:
        table = {val: key for key, val in table.items()}

    return table


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
    flip the data doing reverse to the compressed data - looking at each element of size 8 bits

    :param compress_data:
    :return: fliped_data
    """
    fliped_data = ''
    length = len(compress_data) / 8
    for i in range(int(length)):
        fliped_data += compress_data[-8:]
        compress_data = compress_data[:-8]

    bytes_object = fliped_data.encode("utf-8")

    return bytes_object


def get_encode_element(stream, reading_size):
    """
    the next element represent in as string number . the riding size in constant
    :param stream:
    :param reading_size:
    :return: element
    """
    element = stream.read('bin' + str(reading_size))
    return str(int(element, 2))


def fill_zero_bytes(compress_data):
    """
    fill the data with zero in start that will divide by 8 - for hexa representing
    :param: compress_data:
    :return: compress_data
    """
    if zero_fill := len(compress_data) % 8:
        compress_data = convert_int_to_bits(0, zero_fill) + compress_data
    return compress_data


def encode(uncompressed_data, color_table_size):
    """
    using lzw algorithm for compress data ang gif images
    the table code look like this:

    str   |  int
    ______|_____
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
    reading_size = math.ceil(math.log(color_table_size + 1)) + 1

    #  at start as reading later this will change
    writing_size = reading_size

    table = initialize_code_table(color_table_size, False)

    # if the next item in the table will need to be writen with more bit change now the writing size
    # because we're adding more indexes to the table, and now we need more bits to represent the numbers
    writing_size = update_code_size(len(table), writing_size)

    # add the start of reading (in our example = 4)
    clear_code = table[str(len(table) - 2)]
    #  add the enf of reading (in our example = 5)
    end_of_information_code = table[str(len(table) - 1)]

    compress_data = b''
    #  add clear code according the reading size (in our example = 4)
    compress_data += convert_int_to_bits(clear_code, reading_size)

    length = stream.length

    # the first item
    curr_el = get_encode_element(stream, reading_size)

    while stream.pos != length:

        # reading the next item
        next_el = get_encode_element(stream, reading_size)
        current_and_next = next_el + "," + curr_el

        # if it is in the table continue
        if current_and_next in table:
            curr_el = current_and_next
        else:
            # write the compressed value to the output
            compress_data = convert_int_to_bits(table[curr_el], writing_size) + compress_data
            # add the new concat to the table
            table[current_and_next] = len(table)
            # checking if to change the writing size
            writing_size = update_code_size(len(table), writing_size)
            curr_el = next_el

    # add the last element to the output
    compress_data = convert_int_to_bits(table[curr_el], writing_size) + compress_data

    # add the end to the output - for inform that is the end ot the data
    compress_data = convert_int_to_bits(end_of_information_code, writing_size) + compress_data

    # fill zeros to be represented by 8 bits and flip the data
    x = flip_data(fill_zero_bytes(compress_data).decode('utf-8'))
    return x


def get_decode_element(stream, reading_size, pos):
    """
    the next element represent in as string number
    :param stream:
    :param reading_size:
    :return: element
    """
    stream.pos = pos
    element = stream.read('bin' + str(reading_size))
    return int(element, 2)


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
    #!!!!!!!!!!!!!!! int the origin was writing_size = lzw_minimum_code_size + 1 and reading_size = writing_size
    reading_size = writing_size + 1
    color_table_size = math.pow(2, lzw_minimum_code_size)
    table = initialize_code_table(int(color_table_size), True)
    reading_size = update_code_size1(len(table), reading_size)

    # add the start of reading
    clear_code = int(table[len(table) - 2])

    #  add the enf of reading
    end_of_information_code = int(table[(len(table) - 1)])

    #bytes_object = bytes.fromhex(compressed_data)
    bytes_object = compressed_data

    # Convert bytes object to binary string with leading zeros
    binary_string = ''.join(format(byte, '08b') for byte in bytes_object)

    compressed_data = flip_data(binary_string)
    data_length = len(compressed_data)
    compressed_data = hex(int(compressed_data, 2))
    compressed_data = fill_zero_hexa(compressed_data, data_length)
    stream = ConstBitStream(compressed_data)
    pos = stream.length - reading_size
    first_element = get_decode_element(stream, reading_size, pos)
    pos = pos - reading_size

    if first_element != clear_code:
        print("the image was corrupted")
        return -1

    decompressed_data = b''
    curr_el = get_decode_element(stream, reading_size, pos)
    pos = pos - reading_size
    decompressed_data += index_to_binary(table[curr_el], writing_size)
    while True:
        next_el = get_decode_element(stream, reading_size, pos)
        if next_el == end_of_information_code:
            break
        if next_el == clear_code:
            # need to check what happend with the current elemend and to add limitation of 12 size writing size
            # k = table[curr_el][0]
            decompressed_data += index_to_binary(table[curr_el][0], writing_size)

            table = initialize_code_table(int(color_table_size), True)
            reading_size = lzw_minimum_code_size + 1
            pos = pos - reading_size
            curr_el = get_decode_element(stream, reading_size, pos)
            pos = pos - reading_size

            continue

        if next_el in table:
            decompressed_data += index_to_binary(table[next_el], writing_size)
            k = get_first_element(table[next_el])
        else:
            k =get_first_element(table[curr_el])
            decompressed_data += index_to_binary(table[curr_el] + "," + k, writing_size)

        table[len(table)] = table[curr_el] + "," + k
        reading_size = update_code_size1(len(table), reading_size)
        pos = pos - reading_size
        curr_el = next_el

    return decompressed_data, writing_size


if __name__ == '__main__':
    # Open the file in binary mode -  after the data compressed
    input_bytes = '0x24929248924A492249292489200092248002492400049490001252491249492449252491249'

    print("0x{:x}".format(int(encode(input_bytes, 4), 2)))

    # the output will be the indexes of the colors in color table in this example the index's length will be 3
    # therefore, we expect to see:"001 001 001 001 001 010 010 010 ..." equivalent to 1,1,1,1,1,2,2,2..
    val = bytes('0x8c2d99872a1cdc33a00275ec95faa8de608c04914c01', 'utf-8')
    print(decode_lzw(val, 4))

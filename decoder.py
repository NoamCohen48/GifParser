import binascii
import math
import typing

import bitstring
from PIL import Image as Image_PIL

from BitStream import BitStreamReader
from enums import BlockPrefix
from gif_objects import Gif, GraphicControlExtension, Image, ApplicationExtension, PlainTextExtension, \
    IncorrectFileFormat, CommentExtension
from lzw import decode_lzw

LAST_ELEMENT = -1
TRANSPARENT_VALUE = -1
PENULTIMATE = -2


def decode_gif(io: typing.BinaryIO) -> Gif:
    gif_object: Gif = Gif()
    gif_stream: BitStreamReader = BitStreamReader(bitstring.ConstBitStream(io))

    decode_header(gif_stream, gif_object)
    decode_logical_screen_descriptor(gif_stream, gif_object)

    # There is no global color table if the size is 0.
    if gif_object.global_color_table_size != 0:
        decode_global_color_table(gif_stream, gif_object)

    # Read the first byte to check if the next block is extension or image descriptor.
    while (prefix := BlockPrefix(gif_stream.read_bytes(1))) != BlockPrefix.Trailer:
        if prefix is BlockPrefix.Extension:
            # Check which type of extension is the next block.
            extension_label: bytes = gif_stream.read_bytes(1)
            prefix = BlockPrefix(extension_label)

            if prefix is BlockPrefix.ApplicationExtension:
                decode_application_extension(gif_stream, gif_object)

            elif prefix is BlockPrefix.GraphicControlExtension:
                decode_graphic_control_extension(gif_stream, gif_object)

            elif prefix is BlockPrefix.CommentExtension:
                decode_comment_extension(gif_stream, gif_object)

            elif prefix is BlockPrefix.PlainTextExtension:
                decode_plain_text(gif_stream, gif_object)

        elif prefix is BlockPrefix.ImageDescriptor:
            decode_image_descriptor(gif_stream, gif_object)

            # Check if there is a Local color table for this image.
            if gif_object.images[LAST_ELEMENT].local_color_table_flag:
                decode_local_color_table(gif_stream, gif_object)

            decode_image_data(gif_stream, gif_object)

            last_graphic_control_index = gif_object.images[LAST_ELEMENT].index_graphic_control_ex
            last_graphic_control_disposal = gif_object.graphic_control_extensions[last_graphic_control_index].disposal
            if last_graphic_control_disposal == 3:
                gif_object.images.append(gif_object.images[PENULTIMATE])
            elif last_graphic_control_disposal == 2:
                add_background_frame(gif_object)

        elif prefix is BlockPrefix.NONE:
            raise Exception("prefix is incorrect")

    return gif_object


def decode_header(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    gif_object.version = gif_stream.read_decoded(6)


def decode_logical_screen_descriptor(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    gif_object.width = gif_stream.read_unsigned_integer(2, 'bytes')
    gif_object.height = gif_stream.read_unsigned_integer(2, 'bytes')

    global_color_table_exist = gif_stream.read_bool()

    # both not relevant
    gif_object.color_resolution = gif_stream.read_unsigned_integer(3, 'bits')
    gif_object.sort_flag = gif_stream.read_bool()

    global_color_table_size_value = gif_stream.read_unsigned_integer(3, 'bits')
    if global_color_table_exist:
        gif_object.global_color_table_size = pow(2, global_color_table_size_value + 1)
    else:
        gif_object.global_color_table_size = 0

    gif_object.background_color_index = gif_stream.read_unsigned_integer(1, 'bytes')

    pixel_ratio_value = gif_stream.read_unsigned_integer(1, 'bytes')
    gif_object.pixel_aspect_ratio = (pixel_ratio_value + 15) / 64


def decode_global_color_table(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    """
    Decode global color table.
    We read the number of bytes we received in the flag in Logical Screen Descriptor,
    and divided into triplets of bytes pairs, each triplet representing RGB of a color.
    """
    gif_object.global_color_table = [gif_stream.read_bytes(3) for _ in range(
        int(gif_object.global_color_table_size))]


def add_background_frame(gif_object: Gif):
    prev_image = gif_object.images[-1]
    current_image = Image()
    current_image.index_graphic_control_ex = None

    current_image.left = prev_image.left
    current_image.top = prev_image.top
    current_image.width = prev_image.width
    current_image.height = prev_image.height

    current_image.local_color_table_flag = False
    current_image.interlace_flag = False
    current_image.sort_flag = False
    current_image.reserved = 0
    current_image.size_of_local_color_table = 0

    background_color: bytes = gif_object.global_color_table[gif_object.background_color_index]
    current_image.image_data = [background_color] * prev_image.width * prev_image.height

    gif_object.images.append(current_image)


def decode_application_extension(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    app_ex = ApplicationExtension()

    block_size = gif_stream.read_unsigned_integer(1, 'bytes')
    if block_size != 11:
        raise IncorrectFileFormat(f'application extension block size should be 11 not {block_size}')

    app_ex.application_name = gif_stream.read_bytes(8).decode("utf-8")
    app_ex.identify = gif_stream.read_bytes(3).decode("utf-8")

    application_data = b''
    while (number_of_sub_block_bytes := gif_stream.read_unsigned_integer(1, 'bytes')) != 0:
        sub_block = gif_stream.read_bytes(number_of_sub_block_bytes)
        application_data += sub_block

    app_ex.data = application_data
    gif_object.add_application_extension(app_ex)
    gif_object.structure.append(app_ex)


def decode_graphic_control_extension(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    graphic_control_ex = GraphicControlExtension()

    # always 4 bytes
    block_size = gif_stream.read_unsigned_integer(1, "bytes")
    if block_size != 4:
        raise IncorrectFileFormat(f'graphic control extension size should be 4 not {block_size}')

    # flags from Packed Fields
    graphic_control_ex.reserved = gif_stream.read_unsigned_integer(3, "bits")
    graphic_control_ex.disposal = gif_stream.read_unsigned_integer(3, "bits")
    graphic_control_ex.user_input_flag = gif_stream.read_bool()
    graphic_control_ex.transparent_color_flag = gif_stream.read_bool()

    graphic_control_ex.delay_time = gif_stream.read_unsigned_integer(2, "bytes")
    graphic_control_ex.transparent_index = gif_stream.read_unsigned_integer(1, "bytes")

    block_terminator = gif_stream.read_unsigned_integer(1, "bytes")

    # Check block terminator
    if block_terminator != 0:
        raise IncorrectFileFormat(f'Should be block terminator(0) but we read {block_terminator}')

    gif_object.graphic_control_extensions.append(graphic_control_ex)
    gif_object.structure.append(graphic_control_ex)


def decode_image_descriptor(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    current_image = Image()
    current_image.index_graphic_control_ex = len(gif_object.graphic_control_extensions) - 1

    current_image.left = gif_stream.read_unsigned_integer(2, 'bytes')
    current_image.top = gif_stream.read_unsigned_integer(2, 'bytes')
    current_image.width = gif_stream.read_unsigned_integer(2, 'bytes')
    current_image.height = gif_stream.read_unsigned_integer(2, 'bytes')

    current_image.local_color_table_flag = gif_stream.read_bool()
    current_image.interlace_flag = gif_stream.read_bool()
    current_image.sort_flag = gif_stream.read_bool()
    current_image.reserved = gif_stream.read_unsigned_integer(2, 'bits')
    current_image.size_of_local_color_table = gif_stream.read_unsigned_integer(3, 'bits')

    gif_object.images.append(current_image)
    gif_object.structure.append(current_image)


def decode_local_color_table(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    current_image = gif_object.images[LAST_ELEMENT]
    size_of_color_table = math.pow(2, current_image.size_of_local_color_table + 1)

    colors_array = [gif_stream.read_bytes(3) for _ in range(int(size_of_color_table))]
    gif_object.local_color_tables.append(colors_array)
    current_image.local_color_table = colors_array


def decode_image_data(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    res = b''
    current_image = gif_object.images[LAST_ELEMENT]
    current_image.lzw_minimum_code_size = gif_stream.read_unsigned_integer(1, 'bytes')

    compressed_sub_block = b''
    while (number_of_sub_block_bytes := gif_stream.read_unsigned_integer(1, 'bytes')) != 0:
        compressed_sub_block += gif_stream.read_bytes(number_of_sub_block_bytes)
    if not compressed_sub_block:
        current_image.img = None
        return

    res, index_length = decode_lzw(compressed_sub_block, current_image.lzw_minimum_code_size)

    current_image.raw_indexes = compressed_sub_block

    if current_image.local_color_table_flag:
        local_color_table = gif_object.local_color_tables[LAST_ELEMENT]
    else:
        local_color_table = gif_object.global_color_table

    for pos in range(0, len(res), index_length):
        current_index = int((res[pos:pos + index_length]), 2)

        if (current_index == gif_object.graphic_control_extensions[LAST_ELEMENT].transparent_index and
                gif_object.graphic_control_extensions[LAST_ELEMENT].transparent_color_flag):
            # current_image.image_indexes.append(gif_object.images[-2].image_indexes[int(pos / index_length)])
            # if the index it transparent we put -1 and in the future we will change it to correct color
            current_image.image_data.append(TRANSPARENT_VALUE)
        else:
            # current_image.image_indexes.append(current_index)
            current_image.image_data.append(local_color_table[current_index])
        current_image.raw_data.append(local_color_table[current_index])

    current_image.img = create_img(gif_object, current_image.image_data, current_image.width, current_image.height)


def create_img(gif_object: Gif, image_data: list[str], width: int, height: int) -> Image_PIL.Image:
    current_image = gif_object.images[LAST_ELEMENT]
    #  for all the images except the first
    gif_size = current_image.width * current_image.height
    assert gif_size == len(
        image_data), f"size mismatch: gif_size {gif_size} does not match the length of image_information {len(image_data)}"

    if len(gif_object.images) > 1:
        # create new image with -1
        arr = [TRANSPARENT_VALUE] * gif_object.width * gif_object.height
        start_current_image = current_image.top * gif_object.width + current_image.left

        # add the colors from the image data that we extract from lzw
        rows = 0
        for pos in range(0, len(image_data), width):
            arr[start_current_image + rows: start_current_image + rows + width] = image_data[pos:pos + width]
            rows += gif_object.width
        pos = pos + width
        #  complete the lats line - what is left from the image data
        arr[start_current_image + rows: start_current_image + len(image_data) - pos] = image_data[pos:len(image_data)]
        rows += gif_object.width

        # for all the indexes that don't have value or transparent-value , we take the data from the last image
        last_image = gif_object.images[PENULTIMATE]
        current_image.image_data = (
            [arr[i] if arr[i] != TRANSPARENT_VALUE else last_image.image_data[i] for i in range(len(arr))]
        )

    img = Image_PIL.new('RGB', (gif_object.width, gif_object.height))
    rgb_array = ["#" + binascii.hexlify(b).decode('utf-8').upper() for b in current_image.image_data]

    # Set the pixel values of the image using the RGB array
    pixels = img.load()

    ''' 
    for each pixel - we take specific color ("#FF0000") and divide it to 3 parts("FF","00","00") of RGB.
    then convert it from hex(16) to int (255,0,0), in the end we get tuple of three numbers that represent the color
    The code iterates over each pixel in an image represented as a two-dimensional array of hex color codes.
    It then extracts the red, green, and blue color components of each pixel by converting the hex codes to integers
    and stores them as a tuple of three integers
    '''
    for row in range(gif_object.width):
        for column in range(gif_object.height):
            hex_color = rgb_array[column * gif_object.width + row]
            r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            pixels[row, column] = (r, g, b)
    return img


def decode_comment_extension(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    """decode comment extension"""
    comment_ex = CommentExtension()
    data = b''
    # every sub block start with a bye that present the size of it.
    sub_block_size = gif_stream.read_unsigned_integer(1, "bytes")
    while sub_block_size != 0:  # Change to Block Terminator enum
        data += gif_stream.read_bytes(sub_block_size)
        sub_block_size = gif_stream.read_unsigned_integer(1, "bytes")

    comment_ex.data = data
    gif_object.comments_extensions.append(comment_ex)
    gif_object.structure.append(comment_ex)


def decode_plain_text(gif_stream: BitStreamReader, gif_object: Gif) -> None:
    plain_text_ex = PlainTextExtension()

    # Read the block size (always 12)
    block_size = gif_stream.read_unsigned_integer(1, "bytes")
    if block_size != 12:
        raise IncorrectFileFormat(f'plain text extension block size should be 12 not {block_size}')

    plain_text_ex.left = gif_stream.read_unsigned_integer(2, "bytes")
    plain_text_ex.top = gif_stream.read_unsigned_integer(2, "bytes")
    plain_text_ex.width = gif_stream.read_unsigned_integer(2, "bytes")
    plain_text_ex.height = gif_stream.read_unsigned_integer(2, "bytes")
    plain_text_ex.char_width = gif_stream.read_unsigned_integer(1, "bytes")
    plain_text_ex.char_height = gif_stream.read_unsigned_integer(1, "bytes")
    plain_text_ex.text_color = gif_stream.read_unsigned_integer(1, "bytes")
    plain_text_ex.background_color = gif_stream.read_unsigned_integer(1, "bytes")

    data = b''
    # every data sub block start with a bye that present the size of it.
    sub_block_size = gif_stream.read_unsigned_integer(1, "bytes")
    while sub_block_size != 0:  # Change to Block Terminator enum
        data += gif_stream.read_bytes(sub_block_size)
        sub_block_size = gif_stream.read_unsigned_integer(1, "bytes")

    plain_text_ex.data = data
    gif_object.plain_text_extensions.append(plain_text_ex)
    gif_object.structure.append(plain_text_ex)

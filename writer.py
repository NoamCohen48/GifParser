import math

from BitStream import BitStreamWriter
from enums import BlockPrefix
from gif_objects import Gif, ApplicationExtension, GraphicControlExtension, Image, CommentExtension, PlainTextExtension
from lzw import insert_to_stream, encode
from utils import chunker

ApplicationExtensionBlockSize = 11
GraphicControlExtensionBlockSize = 4
PlainTextExtensionBlockSize = 4

def convert_int_to_bits(number, code_size):
    return bytes((bin(number)[2:]).zfill(code_size), 'utf-8')


def index_from_data(image_data, color_table):
    size_of_index = math.ceil(math.log(len(color_table), 2)) + 1
    # TODO: switch to use bitstring.stream
    indexes = [convert_int_to_bits(color_table.index(color), size_of_index) for color in image_data]
    res = b''.join(indexes)
    hex_string = '0x' + hex(int(res.decode('utf-8'), 2))[2:]
    return hex_string


def write_gif(gif_object: Gif) -> BitStreamWriter:
    gif_stream = BitStreamWriter()

    write_header(gif_stream, gif_object)
    write_logical_screen_descriptor(gif_stream, gif_object)

    if gif_object.global_color_table_size != 0:
        write_global_color_table(gif_stream, gif_object.global_color_table)

    for block in gif_object.structure:
        if isinstance(block, Image):
            if block.local_color_table_flag:
                write_image(gif_stream, block, block.local_color_table)
            else:
                write_image(gif_stream, block, gif_object.global_color_table)
        elif isinstance(block, CommentExtension):
            write_comment_extension(gif_stream, block)
        elif isinstance(block, PlainTextExtension):
            write_plain_text(gif_stream, block)
        elif isinstance(block, GraphicControlExtension):
            write_graphic_control_extension(gif_stream, block)
        elif isinstance(block, ApplicationExtension):
            write_application_extension(gif_stream, block)
        else:
            raise Exception("not a gif object in structure")

    gif_stream.write_bytes(BlockPrefix.Trailer.value)
    return gif_stream


def write_header(gif_stream: BitStreamWriter, gif_object: Gif) -> None:
    bytes = gif_object.version.encode()
    gif_stream.write_bytes(bytes)


def write_logical_screen_descriptor(gif_stream: BitStreamWriter, gif_object: Gif) -> None:
    gif_stream.write_unsigned_integer(gif_object.width, 2, 'bytes')
    gif_stream.write_unsigned_integer(gif_object.height, 2, 'bytes')

    # if global color table exist
    global_color_table_exist = gif_object.global_color_table_size != 0
    gif_stream.write_bool(global_color_table_exist)

    # both not relevant
    gif_stream.write_unsigned_integer(gif_object.color_resolution, 3, 'bits')
    gif_stream.write_bool(gif_object.sort_flag)

    if global_color_table_exist:
        global_color_table_size_value = int(math.log2(gif_object.global_color_table_size)) - 1
        gif_stream.write_unsigned_integer(global_color_table_size_value, 3, 'bits')
    else:
        gif_stream.write_unsigned_integer(0, 3, 'bits')

    gif_stream.write_unsigned_integer(gif_object.background_color_index, 1, 'bytes')

    pixel_ratio_value = int(gif_object.pixel_aspect_ratio * 64 - 15)
    gif_stream.write_unsigned_integer(pixel_ratio_value, 1, 'bytes')


def write_global_color_table(gif_stream: BitStreamWriter, global_color_table: list[bytes]) -> None:
    gif_stream.write_bytes(b''.join(global_color_table))


def write_application_extension(gif_stream: BitStreamWriter, application_ex: ApplicationExtension) -> None:
    gif_stream.write_bytes(BlockPrefix.Extension.value)
    gif_stream.write_bytes(BlockPrefix.ApplicationExtension.value)
    gif_stream.write_unsigned_integer(ApplicationExtensionBlockSize, 1, 'bytes')

    gif_stream.write_bytes(application_ex.application_name.encode())
    gif_stream.write_bytes(application_ex.identify.encode())

    # looping in chinks of 255 bytes
    for sub_block in chunker(255, application_ex.data):
        sub_block_size = len(sub_block)
        gif_stream.write_unsigned_integer(sub_block_size, 1, 'bytes')
        gif_stream.write_bytes(sub_block)

    gif_stream.write_bytes(BlockPrefix.Terminator.value)


def write_graphic_control_extension(gif_stream: BitStreamWriter, graphic_control_ex: GraphicControlExtension) -> None:
    gif_stream.write_bytes(BlockPrefix.Extension.value)
    gif_stream.write_bytes(BlockPrefix.GraphicControlExtension.value)

    gif_stream.write_unsigned_integer(GraphicControlExtensionBlockSize, 1, 'bytes')

    # write package
    gif_stream.write_unsigned_integer(graphic_control_ex.reserved, 3, 'bits')
    gif_stream.write_unsigned_integer(graphic_control_ex.disposal, 3, 'bits')
    gif_stream.write_bool(graphic_control_ex.user_input_flag)
    gif_stream.write_unsigned_integer(graphic_control_ex.transparent_color_flag, 1, 'bits')

    gif_stream.write_unsigned_integer(graphic_control_ex.delay_time, 2, 'bytes')
    gif_stream.write_unsigned_integer(graphic_control_ex.transparent_index, 1, 'bytes')

    gif_stream.write_bytes(BlockPrefix.Terminator.value)


def write_image(gif_stream: BitStreamWriter, image: Image, color_table: list[bytes]) -> None:
    # Image Descriptor
    gif_stream.write_bytes(BlockPrefix.ImageDescriptor.value)
    gif_stream.write_unsigned_integer(image.left, 2, 'bytes')
    gif_stream.write_unsigned_integer(image.top, 2, 'bytes')
    gif_stream.write_unsigned_integer(image.width, 2, 'bytes')
    gif_stream.write_unsigned_integer(image.height, 2, 'bytes')
    # write package
    gif_stream.write_bool(image.local_color_table_flag)
    gif_stream.write_unsigned_integer(image.interlace_flag, 1, 'bits')
    gif_stream.write_unsigned_integer(image.sort_flag, 1, 'bits')
    gif_stream.write_unsigned_integer(image.reserved, 2, 'bits')
    gif_stream.write_unsigned_integer(image.size_of_local_color_table, 3, 'bits')

    # Local Color Table
    if image.local_color_table_flag:
        gif_stream.write_bytes(b''.join(image.local_color_table))

    # Image Data
    gif_stream.write_unsigned_integer(image.lzw_minimum_code_size, 1, 'bytes')
    # TODO: need to change: get the data after the lzw algorithm presses.
    data = index_from_data(image.image_data, color_table)
    hex_string = ''.join(data)

    encoded = encode(hex_string, len(color_table))

    if not encoded:
        gif_stream.write_unsigned_integer(0, 1, 'bytes')
    else:
        # looping in chunks of 255 bytes
        for sub_block in chunker(255, encoded):
            sub_block_size = len(sub_block)
            gif_stream.write_unsigned_integer(sub_block_size, 1, 'bytes')
            gif_stream.write_bytes(sub_block)

        gif_stream.write_bytes(BlockPrefix.Terminator.value)


def write_comment_extension(gif_stream: BitStreamWriter, comment: CommentExtension) -> None:
    gif_stream.write_bytes(BlockPrefix.Extension.value)
    gif_stream.write_bytes(BlockPrefix.CommentExtension.value)

    # looping in chinks of 255 bytes
    for sub_block in chunker(255, comment.data):
        sub_block_size = len(sub_block)
        gif_stream.write_unsigned_integer(sub_block_size, 1, 'bytes')
        gif_stream.write_bytes(sub_block)

    gif_stream.write_bytes(BlockPrefix.Terminator.value)


def write_plain_text(gif_stream: BitStreamWriter, plain_text: PlainTextExtension) -> None:
    gif_stream.write_bytes(BlockPrefix.Extension.value)
    gif_stream.write_bytes(BlockPrefix.PlainTextExtension.value)

    gif_stream.write_unsigned_integer(PlainTextExtensionBlockSize, 1, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.left, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.top, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.width, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.height, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.char_width, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.char_height, 2, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.text_color, 1, 'bytes')
    gif_stream.write_unsigned_integer(plain_text.background_color, 1, 'bytes')

    # looping in chunks of 255 bytes
    for sub_block in chunker(255, plain_text.data):
        sub_block_size = len(sub_block)
        gif_stream.write_unsigned_integer(sub_block_size, 1, 'bytes')
        gif_stream.write_bytes(sub_block)

    gif_stream.write_bytes(BlockPrefix.Terminator.value)

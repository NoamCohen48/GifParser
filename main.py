import gif_objects
from decoder import decode_gif, decode_image_data, decode_local_color_table


def main():
    with open("example.gif", "rb") as gif_file:
        decode_gif(gif_file)


if __name__ == '__main__':
    main()
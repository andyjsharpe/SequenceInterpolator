black = '#171717'
navy = '#1f252e'
grey = '#2f353d'
lightGrey = '#595f69'
white = '#cfcfcf'
gold = '#ffcc00'
orange = '#ffaa00'
check = '#919191'
blue = '#178bff'
lightBlue = '#a4c1de'


def hex_to_rgb(hex_color):
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return rgb


def rgb_to_hex(rgb):
    # Convert RGB to hex
    hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
    return hex_color


def multiply_color(rgb, factor):
    return tuple(int(min(255, c * factor)) for c in rgb)


def add_colors_and_adjust_brightness(base_color, pre_light: int, brightness_factor: int, post_light: int):
    # Convert hex to RGB
    base_rgb = hex_to_rgb(base_color)
    additional_rgb = hex_to_rgb(pre_light)
    additional_rgb2 = hex_to_rgb(post_light)

    # Add the two colors
    new_rgb = tuple(c1 + c2 for c1, c2 in zip(base_rgb, additional_rgb))

    # Adjust brightness
    new_rgb = multiply_color(new_rgb, brightness_factor)

    # Add again
    new_rgb = tuple(c1 + c2 for c1, c2 in zip(new_rgb, additional_rgb2))

    # Convert RGB back to hex
    new_color = rgb_to_hex(new_rgb)

    return new_color
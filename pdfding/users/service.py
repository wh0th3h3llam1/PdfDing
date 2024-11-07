def convert_hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    """Converts a hex color representation to RGB representation"""

    hex_color = hex_color.replace('#', '')

    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # noqa


def convert_rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts RGB color representation to a hex representation"""

    hex_color = ('{:02X}' * 3).format(r, g, b)

    return f'#{str.lower(hex_color)}'


def lighten_color(red: int, green: int, blue: int, percentage: float) -> tuple[int, ...]:
    """Lighting a RGB color by the specified percentage"""

    correction_factor = percentage

    return tuple(round((255 - val) * correction_factor + val) for val in (red, green, blue))


def darken_color(red: int, green: int, blue: int, percentage: float) -> tuple[int, ...]:
    """Darkening a RGB color by the specified percentage"""

    correction_factor = 1 - percentage

    return tuple(round(val * correction_factor) for val in (red, green, blue))


def get_color_shades(custom_color: str) -> tuple[str, ...]:
    """Get the color shades needed for custom theme colors."""

    rgb_color = convert_hex_to_rgb(str(custom_color))

    secondary_color = darken_color(*rgb_color, percentage=0.2)
    tertiary_color_1 = darken_color(*rgb_color, percentage=0.4)
    tertiary_color_2 = lighten_color(*rgb_color, percentage=0.4)

    return tuple(convert_rgb_to_hex(*color) for color in (secondary_color, tertiary_color_1, tertiary_color_2))

from PIL import Image
import math
import sys

kb = 0.114
kr = 0.299
kg = 0.587
luminace_location = []
cb_location = []
cr_location = []
test_quant_matrix = [[-415.38, -30.19, -61.2, 27.24, 56.12, -20.1, -2.39, 0.46],
                     [4.47, -21.86, -60.76, 10.25, 13.15, -7.09, -8.54, 4.88],
                     [-46.83, 7.37, 77.13, -24.56, -28.91, 9.93, 5.42, -5.65],
                     [-48.53, 12.07, 34.1, -14.76, -10.24, 6.3, 1.83, 1.95],
                     [12.12, -6.55, -13.2, -3.95, -1.87, 1.75, -2.79, 3.14],
                     [-7.73, 2.91, 2.38, -5.94, -2.38, 0.94, 4.3, 1.85],
                     [-1.03, 0.18, 0.42, -2.42, -0.88, -3.02, 4.12, -0.66],
                     [-0.17, 0.14, -1.07, -4.19, -1.17, -0.1, 0.5, 1.68]]
test_dct_matrix = [[52, 55, 61, 66, 70, 61, 64, 73],
                   [63, 59, 55, 90, 109, 85, 69, 72],
                   [62, 59, 68, 113, 144, 104, 66, 73],
                   [63, 58, 71, 122, 154, 106, 70, 69],
                   [67, 61, 68, 104, 126, 88, 68, 70],
                   [79, 65, 60, 70, 77, 68, 58, 75],
                   [85, 71, 64, 59, 55, 61, 65, 83],
                   [87, 79, 69, 68, 65, 76, 78, 94]]
hex_lum_quantize = "0x100xb0xa0x100x180x280x330x3d0xc0xc0xe0x130x1a0x3a0x3c0x370xe0xd0x100x180x280x390x450x380xe0x110x160x1d0x330x570x500x3e0x120x160x250x380x440x6d0x670x4d0x180x230x370x400x510x680x710x5c0x310x400x4e0x4e0x570x670x790x780x650x480x5c0x5f0x620x700x640x670x63"
quantization_lum = [16, 11, 10, 16, 24, 40, 51, 61,
                    12, 12, 14, 19, 26, 58, 60, 55,
                    14, 13, 16, 24, 40, 57, 69, 56,
                    14, 17, 22, 29, 51, 87, 80, 62,
                    18, 22, 37, 56, 68, 109, 103, 77,
                    24, 35, 55, 64, 81, 104, 113, 92,
                    49, 64, 78, 78, 87, 103, 121, 120, 101,
                    72, 92, 95, 98, 112, 100, 103, 99]
hex_color_quantize = "0x110xf0x110x150x140x1a0x260x300xf0x130x120x110x140x1a0x230x2b0x110x120x140x160x1a0x1e0x2e0x350x150x110x160x1c0x1e0x270x350x400x140x140x1a0x1e0x270x300x400x400x1a0x1a0x1e0x270x300x3f0x400x400x260x230x2e0x350x400x400x400x400x300x2b0x350x400x400x400x400x40"
quantization_color = [17, 15, 17, 21, 20, 26, 38, 48,
                      15, 19, 18, 17, 20, 26, 35, 43,
                      17, 18, 20, 22, 26, 30, 46, 53,
                      21, 17, 22, 28, 30, 39, 53, 64,
                      20, 20, 26, 30, 39, 48, 64, 64,
                      26, 26, 30, 39, 48, 63, 64, 64,
                      38, 35, 46, 53, 64, 64, 64, 64,
                      48, 43, 53, 64, 64, 64, 64, 64]


def relatize_block(matrix):
    for v in range(8):
        for j in range(8):
            matrix[v][j] -= 128
    return matrix


def dct_transform(matrix, m=8, n=8):
    dct = []
    for v in range(m):
        dct.append([None for _ in range(n)])
    for v in range(m):
        for j in range(n):
            if v == 0:
                ci = 1 / (m ** 0.5)
            else:
                ci = (2 / m) ** 0.5
            if j == 0:
                cj = 1 / (n ** 0.5)
            else:
                cj = (2 / n) ** 0.5
            summed = 0
            for k in range(m):
                for p in range(n):
                    dct1 = matrix[k][p] * math.cos(((2 * k + 1) * v * math.pi) / (
                            2 * m)) * math.cos(((2 * p + 1) * j * math.pi) / (2 * n))
                    summed += dct1
            dct[v][j] = round(round(ci * cj * summed, 4), 2)
    return dct


def quantize(matrix, is_lum):
    row = 0
    collum = 0
    if is_lum:
        for num in quantization_lum:
            if collum >= 8:
                collum = 0
                row += 1
                if row >= 8:
                    break
            va = matrix[row][collum]
            matrix[row][collum] = int(round(va / num))
            collum += 1
    else:
        for num in quantization_color:
            if collum >= 8:
                collum = 0
                row += 1
                if row >= 8:
                    break
            va = matrix[row][collum]
            matrix[row][collum] = int(round(va / num))
            collum += 1
    return matrix


def ycbcr_to_rgb(lu, cb, cr):
    r = lu + 1.403 * (cr - 128)
    g = lu - 0.344136 * (cb - 128) + -0.714136 * (cr - 128)
    b = lu + 1.773 * (cb - 128)
    r = min(max(int(r), 0), 255)
    g = min(max(int(g), 0), 255)
    b = min(max(int(b), 0), 255)
    return r, g, b


def rgb_to_ycbcr(r, g, b):
    lu = r * kr + g * kg + b * kb
    cb = r * -0.16874 + g * -0.33126 + b * 0.5 + 128
    cr = r * 0.5 + g * -0.41869 + b * -0.08131 + 128
    return int(lu), int(cb), int(cr)


if __name__ == "__main__":
    image = Image.open("mtg.jpeg")
    data = image.load()

    for y in range(image.height):
        for x in range(image.width):
            Y, Cb, Cr = rgb_to_ycbcr(*data[x, y])
            data[x, y] = int(Y), int(Cb), int(Cr)

    block = []
    for d in range(8):
        block.append([None for _ in range(8)])
    for y in range(8):
        for x in range(8):
            Y, Cb, Cr = data[x, y]
            block[x][y] = Y
    block = relatize_block(block)
    dct_block = dct_transform(block, 8, 8)
    quant_block = quantize(dct_block, True)

    # MAKE THE IMAGE DIVISIBLE BY 8
    width_divisible = image.width % 8
    height_divisible = image.height % 8
    width_divisible = 8 - width_divisible
    height_divisible = 8 - height_divisible

    new_image = Image.new("RGB", (image.width + width_divisible, image.height + height_divisible))
    new_data = new_image.load()
    picture = []
    """ 
    matrix = [ [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255]]
    """
    # Make image Y Cb Cr
    for y in range(image.height):
        for x in range(image.width):
            Y, Cb, Cr = rgb_to_ycbcr(*data[x, y])
            new_data[x, y] = int(Y), int(Cb), int(Cr)
    # End make image Y Cb Cr

    # For each pixel in a 8x8 matrix use the DCT cosine transform then quantize it
    for oy in range(0, new_image.height, 8):
        sys.stdout.write(f"\rComplete: {oy / new_image.height * 100:.2f}%")
        sys.stdout.flush()
        for ox in range(0, new_image.width, 8):
            # Declare a whole matrix of empty cells
            luminace_block = []
            cb_block = []
            cr_block = []
            for d in range(8):
                luminace_block.append([None for _ in range(8)])
                cb_block.append([None for _ in range(8)])
                cr_block.append([None for _ in range(8)])
            for y in range(8):
                for x in range(8):
                    Y, Cb, Cr = new_data[ox + x, y + oy]
                    luminace_block[x][y] = Y
                    cb_block[x][y] = Cb
                    cr_block[x][y] = Cr

            # Do the stuff with luminace
            luminace_block = relatize_block(luminace_block)
            dct_luminace_block = dct_transform(luminace_block, 8, 8)
            quant_luminace_block = quantize(dct_luminace_block, True)
            luminace_location.append(quant_luminace_block)

            # Do the same stuff slightly different with chroma blue
            cb_block = relatize_block(cb_block)
            dct_cb_block = dct_transform(cb_block, 8, 8)
            quant_cb_block = quantize(dct_cb_block, False)
            cb_location.append(quant_cb_block)

            # Do the same stuff slightly different with chroma red
            cr_block = relatize_block(cr_block)
            dct_cr_block = dct_transform(cr_block, 8, 8)
            quant_cr_block = quantize(dct_cr_block, False)
            cr_location.append(quant_cr_block)

    zigzag_index = [[0, 0], [0, 1], [1, 0], [2, 0], [1, 1], [0, 2], [0, 3], [1, 2],
                    [2, 1], [3, 0], [4, 0], [3, 1], [2, 2], [1, 3], [0, 4], [0, 5],
                    [1, 4], [2, 3], [3, 2], [4, 1], [5, 0], [6, 0], [5, 1], [4, 2],
                    [3, 3], [2, 4], [1, 5], [0, 6], [0, 7], [1, 6], [2, 5], [3, 4],
                    [4, 3], [5, 2], [6, 1], [7, 0], [7, 1], [6, 2], [5, 3], [4, 4],
                    [3, 5], [2, 6], [1, 7], [2, 7], [3, 6], [4, 5], [5, 4], [6, 3],
                    [7, 2], [7, 3], [6, 4], [5, 5], [4, 6], [3, 7], [4, 7], [5, 6],
                    [6, 5], [7, 4], [7, 5], [6, 6], [5, 7], [6, 7], [7, 6], [7, 7]]
    all_dict = {}
    lum_string = ''
    for lum_block in luminace_location:
        for i in zigzag_index:
            value = lum_block[i[0]][i[1]]
            encoded_value = value & 0xFF
            str_val = hex(encoded_value).replace("0x", "").zfill(2)
            if str_val not in all_dict.keys():
                all_dict[str_val] = 1
            else:
                all_dict[str_val] += 1
            lum_string += str_val

    cb_string = ''
    for cb_block in cb_location:
        for i in zigzag_index:
            value = cb_block[i[0]][i[1]]
            encoded_value = value & 0xFF
            str_val = hex(encoded_value).replace("0x", "").zfill(2)
            if str_val not in all_dict.keys():
                all_dict[str_val] = 1
            else:
                all_dict[str_val] += 1
            cb_string += str_val

    cr_string = ''
    for cr_block in cr_location:
        for i in zigzag_index:
            value = cr_block[i[0]][i[1]]
            encoded_value = value & 0xFF
            str_val = hex(encoded_value).replace("0x", "").zfill(2)
            if str_val not in all_dict.keys():
                all_dict[str_val] = 1
            else:
                all_dict[str_val] += 1
            cr_string += str_val
    print()
    # print(all_dict)
    sorted_keys = sorted(all_dict, key=all_dict.get, reverse=True)

    sorted_dict = [(k, all_dict[k]) for k in sorted_keys]

    steps = []
    this_step = sorted_dict.copy()
    this_step = [{"value": x[0], "cost": x[1], "string": ""} for x in this_step]
    steps.append(this_step)

    sorted_key_strings = {}

    max_steps = 30
    step_cnt = 0
    while step_cnt < max_steps and len(steps[-1]) > 1:
        this_step = steps[step_cnt].copy()

        this_step = sorted(this_step, key=lambda temp: temp["cost"], reverse=True)
        last = this_step[-1]
        second_last = this_step[-2]
        last["string"] += '0'
        second_last['string'] += '1'

        for char in last["value"]:
            if char in sorted_key_strings:
                sorted_key_strings[char] = "0" + sorted_key_strings[char]
            else:
                sorted_key_strings[char] = "0"

        for char in second_last["value"]:
            if char in sorted_key_strings:
                sorted_key_strings[char] = "1" + sorted_key_strings[char]
            else:
                sorted_key_strings[char] = '1'

        this_step = this_step[:-2] + [{"value": second_last['value']+last['value'],
                                       'cost': second_last['cost'] + last['cost'], 'string': ""}]

        steps.append(this_step)
        step_cnt += 1

    # print(sorted_key_strings)

    all_string = lum_string + cb_string + cr_string
    huffman_string = ""
    final_string = ""
    for letter in all_string:
        if letter in sorted_key_strings.keys():
            huffman_string += sorted_key_strings[letter]

    for start in range(0, len(huffman_string), 4):
        final_string += hex(int(huffman_string[start:start+4], 2))[2:]

    with open("mtg.tpg", 'w') as fp:
        fp.writelines(final_string)
    exit(0)

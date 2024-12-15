from PIL import Image

image = Image.open("mtg.jpeg")

data = image.load()
# print(image.width)
# print(image.height)

pixel = data[0, 0]
# print(pixel)
'''
red = pixel[0]
green = pixel[1]
blue = pixel[2]
'''
red, green, blue = pixel

packed_int = 0

# print(red, green, blue)

packed_int += red << 16
packed_int += green << 8
packed_int += blue << 0

# print(packed_int)
'''
red = packed_int >> 16
packed_int -= red << 16
green = packed_int >> 8
packed_int -= green << 8
blue = blue >> 0
'''

new_blue = packed_int & 255
packed_int >>= 255
new_green = packed_int & 255
packed_int >>= 255
new_red = packed_int & 255

# print(new_red, new_blue, new_green)
# print(red, green, blue)


def vertical_flip(original_image):
    blank = Image.new("RGB", (original_image.width, original_image.height))
    blank_data = blank.load()
    original_data = original_image.load()

    for y in range(original_image.height):
        for x in range(original_image.width):
            opixel = original_data[x, y]
            blank_data[(original_image.width-1) - x, y] = opixel
    return blank


def horizontal_flip(original_image):
    blank = Image.new("RGB", (original_image.width, original_image.height))
    blank_data = blank.load()
    original_data = original_image.load()

    for y in range(original_image.height):
        for x in range(original_image.width):
            opixel = original_data[x, y]
            blank_data[x,  (original_image.height-1) - y] = opixel
    return blank


def rotate_90(original_image):
    blank = Image.new("RGB", (original_image.height, original_image.width))
    blank_data = blank.load()
    original_data = original_image.load()

    for y in range(original_image.height):
        for x in range(original_image.width):
            opixel = original_data[x, y]
            blank_data[-y + original_image.height-1, x] = opixel
    return blank


def translate(original_image, dx, dy):
    blank = Image.new("RGB", (original_image.width + dx, original_image.height + dy))
    blank_data = blank.load()
    original_data = original_image.load()

    for y in range(original_image.height):
        for x in range(original_image.width):
            opixel = original_data[x, y]
            blank_data[dx + x, dy + y] = opixel
    return blank


def transform(original_image, a, b, c, d, e, f):
    blank = Image.new("RGB", (original_image.width, original_image.height))
    blank_data = blank.load()
    original_data = original_image.load()

    for y in range(original_image.height):
        for x in range(original_image.width):
            opixel = original_data[x, y]
            new_x = x * a + y * b + c
            new_y =  x * d + y * e + f
            blank_data[new_x, new_y] = opixel
    return blank


image_rotated_90 = rotate_90(image)
image_rotated_90.save("rotated90.png")

image_translate = translate(image, 20, 72)
image_translate.save("translated.png")

image_transform = transform(image, -1, 0, image.width-1, 0, 1, 0)
image_transform.save("transformers.png")

from PIL import Image

kb = 0.114
kr = 0.299
kg = 0.587

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
    image = Image.open("wiehnachtsmarkt.jpg")
    data = image.load()

    image_y = Image.new("YCbCr", (image.width, image.height))
    data_y = image_y.load()

    image_cb = Image.new("YCbCr", (image.width, image.height))
    data_cb = image_cb.load()

    image_cr = Image.new("YCbCr", (image.width, image.height))
    data_cr = image_cr.load()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = data[x,y]
            lu, cb, cr = rgb_to_ycbcr(r,g,b)
            data_y[x,y] = (lu,0,0)
            data_cb[x,y] = (0,int(cb/2),0)
            data_cr[x,y] = (0,0,int(cr/2))

    image_y.save("y.jpg")
    image_cb.save("cb.jpg")
    image_cr.save("cr.jpg")

    
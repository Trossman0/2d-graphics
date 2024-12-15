from PIL import Image


def read_hidden_message(pic):
    image = Image.open(pic)
    data = image.load()

    h = ""
    w = ""
    # Get the width
    for tx in range(0, 2):
        tr, tg, tb = data[tx, 0]
        tr &= 7
        tg &= 7
        tb &= 7
        tr = format(tr, "03b")
        tg = format(tg, "03b")
        tb = format(tb, "03b")
        w += tr + tg + tb
    # Get the height
    for tx in range(2, 4):
        tr, tg, tb = data[tx, 0]
        tr &= 7
        tg &= 7
        tb &= 7
        tr = format(tr, "03b")
        tg = format(tg, "03b")
        tb = format(tb, "03b")
        h += tr + tg + tb
    width = int(w, 2)
    height = int(h, 2)
    new_image = Image.new("RGB", (width, height))
    new_data = new_image.load()
    tx, ty = 0, 0
    break_stick = False
    for y in range(image.height):
        if break_stick:
            break
        for x in range(4, image.width):
            # For each pixel take the 3 LSbs and write them to the new file with tx, and ty to make sure we are
            # correctly writing to the new image.
            r, g, b = data[x, y]
            r &= 7
            g &= 7
            b &= 7
            r <<= 5
            g <<= 5
            b <<= 5
            new_data[tx, ty] = r, g, b
            tx += 1
            if tx >= width:
                tx = 0
                ty += 1
            if ty >= height:
                break_stick = True
                break
    new_image.save("Hidden_Image.png")


def write_hidden_message(hid_image):
    # Writing this steganography using the LSB to hide my data
    # for translating from string to binary I used a function from here
    # https://www.geeksforgeeks.org/python-convert-string-to-binary/
    hidden_image = Image.open(hid_image)
    hidden_data = hidden_image.load()
    image = Image.open("Skybox.jpeg")
    data = image.load()
    if hidden_image.height * hidden_image.width > image.width * image.height:
        print("File / Message too large to be encoded in selected photo.")
        return -1
    hx = 0
    hy = 0
    break_stick = False

    w = format(hidden_image.width, "018b")
    h = format(hidden_image.height, "018b")
    # W x H
    lst = [0, 9]
    tv = 0
    for tx in lst:
        temp_red = int(w[tx:tx+3], 2)
        temp_green = int(w[tx+3:tx+6], 2)
        temp_blue = int(w[tx+6:tx+9], 2)
        tr, tg, tb = data[tv, 0]
        tr &= 248
        tg &= 248
        tb &= 248
        tr |= temp_red
        tg |= temp_green
        tb |= temp_blue
        data[tv, 0] = tr, tg, tb
        tv += 1
    for tx in lst:
        temp_red = int(h[tx:tx + 3], 2)
        temp_green = int(h[tx + 3:tx + 6], 2)
        temp_blue = int(h[tx + 6:tx + 9], 2)
        tr, tg, tb = data[tv, 0]
        tr &= 248
        tg &= 248
        tb &= 248
        tr |= temp_red
        tg |= temp_green
        tb |= temp_blue
        data[tv, 0] = tr, tg, tb
        tv += 1
    for y in range(image.height):
        if break_stick:
            break
        for x in range(4, image.width):
            r, g, b = data[x, y]
            hidden_r, hidden_g, hidden_b = hidden_data[hx, hy]
            r &= 248
            g &= 248
            b &= 248
            hidden_r >>= 5
            hidden_g >>= 5
            hidden_b >>= 5
            new_red = r | hidden_r
            new_green = g | hidden_g
            new_blue = b | hidden_b
            data[x, y] = (new_red, new_green, new_blue)
            hx += 1
            if hx >= hidden_image.width:
                hy += 1
                if hy >= hidden_image.height:
                    break_stick = True
                    break
                hx = 0
    image.save("Picture_Encoded.png")


write_hidden_message("Spoorweghaven.jpeg")
picture = "Picture_Encoded.png"
read_hidden_message(picture)

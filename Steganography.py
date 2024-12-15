from PIL import Image


def read_hidden_message(pic):
    image = Image.open(pic)
    data = image.load()
    x = 0
    y = 0
    count = 0
    hidden_binary = ''
    full_message = ''
    while hidden_binary != '00000000':
        pixel = data[x, y]
        red, green, blue = pixel
        packed_int = 0
        packed_int += red << 16
        packed_int += green << 8
        packed_int += blue << 0
        bin_packed_int = format(packed_int, 'b')
        if len(bin_packed_int) < 2:
            bin_packed_int += "00"
        lsb_bin_packed_int = bin_packed_int[-2] + bin_packed_int[-1]
        # print(lsb_bin_packed_int)
        if len(hidden_binary) <= 6:
            hidden_binary += lsb_bin_packed_int
        else:
            # print(hidden_binary)
            ascii_val = int(hidden_binary, 2)
            full_message += chr(ascii_val)
            hidden_binary = ''
            hidden_binary += lsb_bin_packed_int

        x += 1
        if x >= image.width:
            x = 0
            y += 1
    return full_message


def write_hidden_message(message):
    # Writing this steganography using the LSB to hide my data
    # for translating from string to binary I used a function from here https://www.geeksforgeeks.org/python-convert-string-to-binary/
    message += "\0"
    counter = 0
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    x = 0
    y = 0
    image = Image.open("mtg.jpeg")
    data = image.load()
    if len(binary_message) > image.width * image.height * 2:
        print("File / Message too large to be encoded in selected photo.")
        return -1
    for i in range(0, len(binary_message), 2):
        hidden_binary = binary_message[i] + binary_message[i+1]
        packed_int = 0
        pixel = data[x, y]
        red, green, blue = pixel
        new_binary_packed_int = ''
        packed_int += red << 16
        packed_int += green << 8
        packed_int += blue << 0
        bin_packed_int = format(packed_int, 'b')
        # print("The two bits I wish to hide " + hidden_binary)
        # print("Binary Packed Int " + bin_packed_int)
        lsb_bin_packed_int = bin_packed_int[-2] + bin_packed_int[-1]
        # print("the least significant bits of the packed integer " + lsb_bin_packed_int)
        lsb_hidden_binary = hidden_binary[-2] + hidden_binary[-1]
        if lsb_hidden_binary != lsb_bin_packed_int:
            b = 0
            while b < len(bin_packed_int)-2:
                new_binary_packed_int += bin_packed_int[b]
                b += 1
            new_binary_packed_int += hidden_binary
        else:
            new_binary_packed_int = bin_packed_int
        hidden_binary = binary_message[i] + binary_message[i+1]
        # print("The newly packed int in binary " + new_binary_packed_int)
        new_packed_int = int(new_binary_packed_int, 2)
        # print("The newly packed int", new_packed_int)
        # print("The old packed int", packed_int)
        new_red = new_packed_int >> 16
        new_packed_int -= new_red << 16
        new_green = new_packed_int >> 8
        new_packed_int -= new_green << 8
        new_blue = new_packed_int
        data[x, y] = (0, 0, new_blue)
        # print(new_red, red)
        # print(new_green, green)
        # print(new_blue, blue, "\n\n")
        x += 1
        if x >= image.width:
            x = 0
            y += 1
    image.save("Encoded.png")


write_hidden_message("Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not. It's not a story the Jedi would tell you. It's a Sith legend. Darth Plagueis was a Dark Lord of the Sith, so powerful and so wise he could use the Force to influence the midichlorians to create life... He had such a knowledge of the dark side that he could even keep the ones he cared about from dying. The dark side of the Force is a pathway to many abilities some consider to be unnatural. He became so powerful... the only thing he was afraid of was losing his power, which eventually, of course, he did. Unfortunately, he taught his apprentice everything he knew, then his apprentice killed him in his sleep. Ironic. He could save others from death, but not himself.")
picture = "Encoded.png"
rad = read_hidden_message(picture)
print(rad)

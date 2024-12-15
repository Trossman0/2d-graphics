from PIL import Image


def read_hidden_message(pic):
    image = Image.open(pic)
    data = image.load()
    x, y = 0, 0
    binary_message = ""
    full_message = ""
    while True:
        pixel = data[x, y]
        red, green, blue = pixel
        binary_message += format(red & 3, '02b')  # Take the last 2 bits
        binary_message += format(green & 3, '02b')
        binary_message += format(blue & 3, '02b')
        if len(binary_message) >= 8:
            byte = binary_message[:8]  # Get the last byte
            if byte == '00000000':  # Null terminator
                break
            full_message += chr(int(byte, 2))
            binary_message = binary_message[8:]
        x += 1
        if x >= image.width:
            x = 0
            y += 1

        if y >= image.height:
            break
    return full_message


def write_hidden_message(message):
    message += "\0"  # Add null terminator
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    x, y = 0, 0
    image = Image.open("mtg.jpeg")
    data = image.load()

    if len(binary_message) > image.width * image.height * 3:
        print("File / Message too large to be encoded in selected photo.")
        return -1

    for i in range(0, len(binary_message), 6):
        hidden_red = binary_message[i:i + 2]
        hidden_green = binary_message[i + 2:i + 4] if i + 4 <= len(binary_message) else '00'
        hidden_blue = binary_message[i + 4:i + 6] if i + 6 <= len(binary_message) else '00'
        pixel = data[x, y]
        red, green, blue = pixel

        new_red = (red & 252) | int(hidden_red, 2)
        new_green = (green & 252) | int(hidden_green, 2)
        new_blue = (blue & 252) | int(hidden_blue, 2)

        data[x, y] = (new_red, new_green, new_blue)

        x += 1
        if x >= image.width:
            x = 0
            y += 1

        if y >= image.height:
            break

    image.save("Improved_Encoded.png")


# write_hidden_message("Words go here")
picture = "Improved_Encoded.png"
rad = read_hidden_message(picture)
print(rad)
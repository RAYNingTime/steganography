from PIL import Image
import os
import random


def generate_pattern(n, type_g="default"):
    pattern = []
    if type_g == "snake":
        for i in range(n):
            for j in range(i + 1):
                pattern.append((i - j, j))

    elif type_g == "default":
        for i in range(n):
            for j in range(n):
                pattern.append((i, j))
    return pattern


def text_to_bin(text):
    return ''.join(format(ord(char), '08b') for char in text)


def bin_to_text(binary):
    text = ''
    for i in range(0, len(binary), 8):  # Read 8 bits at a time
        byte = binary[i:i+8]
        if len(byte) < 8:  # Skip incomplete bytes
            continue
        text += chr(int(byte, 2))
    return text


def steganography(path, save=False, show=False, end_marker='1111111111111110'):
    if len(end_marker) != 16:
        print("Incorrect size of end marker! Try again")
        return

    # Load the image
    img = Image.open(path)

    # Get image size
    width, height = img.size

    if width != height:
        print(f"Image dimensions: {width}x{height}")
        print("ERROR: Fixing Dimensions!")
        size = min(width, height)
        img = img.resize((size, size))  # Update the image variable
        # Save the fixed image
        fn, fext = os.path.splitext(path)
        img.save('{}_fixed{}'.format(fn, fext))
    else:
        size = width

    print("Dimensions are correct!")

    # Input for password
    password = input("What to hide: ")
    binary_message = text_to_bin(password) + end_marker
    print(binary_message)
    message_len = len(binary_message)
    index = 0

    total_capacity = size * size * 3 # X, Y, RGB, TWO BITS

    print(total_capacity - len(binary_message))
    if len(binary_message) > total_capacity:
        print("ERROR: The message is too long to hide in this image.")
        return
    elif len(binary_message) < total_capacity:
        to_fill = (total_capacity - len(binary_message))
        for _ in range(to_fill):
            # Choose 0 or 1 semi-randomly, with bias defined by weight_factor
            # weight_factor: Probability of appending '1'
            bit = '1' if random.random() < 0.5 else '0'

            # Append the chosen bit to the binary string
            binary_message += bit

    # Loop through the image pixels
    for x, y in generate_pattern(size):
        pixel = img.getpixel((x, y))
        new_pixel = list(pixel)  # Work with a mutable list
        for channel in range(3):  # Loop through R, G, B channels
            if binary_message:  # Check if there's still a message to encode
                # Get the next bit of the message
                bit = binary_message[0]
                binary_message = binary_message[1:]  # Remove the bit from the message
                # Replace the LSB
                new_pixel[channel] = (pixel[channel] & ~1) | int(bit)  # Set the LSB to the bit
        img.putpixel((x, y), tuple(new_pixel))  # Update the pixel in the image

    # Show the modified image
    if show:
        img.show()

    if save:
        fn, fext = os.path.splitext(path)
        try:
            img.save('{}_hidden{}'.format(fn, fext))
            print("Image saved successfully.")
        except Exception as e:
            print(f"Error saving image: {e}")

    print(f"Successfully hidden {message_len} bits of {len(binary_message)} in the image.")


def img_sub(path1, path2, save=False):
    img1 = Image.open(path1).convert('RGB')
    img2 = Image.open(path2).convert('RGB')

    # Ensure both images are of the same size
    if img1.size != img2.size:
        print("Error: Images must be of the same dimensions.")
        return

    result = Image.new('RGB', img1.size)

    for x in range(img1.width):
        for y in range(img1.height):
            r1, g1, b1 = img1.getpixel((x, y))
            r2, g2, b2 = img2.getpixel((x, y))

            # Calculate absolute difference
            r = abs(r1 - r2)
            g = abs(g1 - g2)
            b = abs(b1 - b2)

            # Optionally scale the differences to enhance visibility
            r = min(255, r * 50)  # Scale by a factor of 10 (adjust as needed)
            g = min(255, g * 50)
            b = min(255, b * 50)

            # Set the new pixel value
            result.putpixel((x, y), (r, g, b))

    # Show and save the result
    result.show()

    # TODO: Fix the saving of the file.
    if save:
        fn1, fext1 = os.path.splitext(path1)
        fn2, fext2 = os.path.splitext(path2)
        result.save('{}_{}_subtract{}'.format(fn1, fn2, fext1))


def steganography_decrypt(path, end_marker='1111111111111110'):
    # Load the image
    img = Image.open(path)

    # Get image size
    width, height = img.size
    size = min(width, height)

    binary_message = ''
    # Retrieve pixel data
    for x, y in generate_pattern(size):
        pixel = img.getpixel((x, y))
        for channel in range(3):  # Loop through R, G, B channels
            lsb = pixel[channel] & 1  # Get the last bit
            binary_message += str(lsb)  # Append the bit
            if binary_message.endswith(end_marker):  # Check for the end marker
                return bin_to_text(binary_message[:-len(end_marker)])  # Remove end marker before converting
    # In case no end marker is found, return the whole message
    return bin_to_text(binary_message)


steganography("pngs/code3.png", save=True)
img_sub("pngs/code3_hidden.png", "pngs/code3_fixed.png")
hidden_message = steganography_decrypt('pngs/code3_hidden.png')
print(hidden_message)

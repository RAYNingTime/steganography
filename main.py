from PIL import Image
import os


def generate_pattern(n, type = "default"):
    pattern = []
    if type == "snake":
        for i in range(n):
            for j in range(i + 1):
                pattern.append((i - j, j))

    elif type == "default":
        for i in range(n):
            for j in range(n):
                pattern.append((i, j))

    return pattern


def text_to_bin(text):
    return ''.join(format(ord(char), '08b') for char in text)


def steganography(path, save=False, show=False):
    # Load the image
    img = Image.open(path)

    # Get image size
    width, height = img.size

    if width != height:
        print(f"Image dimensions: {width}x{height}")
        print("ERROR: Fixing Dimensions!")
        size = min(width, height)
        img = img.resize((size, size))  # Update the image variable
    else:
        size = width

    print("Dimensions are correct!")

    # Save the fixed image
    fn, fext = os.path.splitext(path)
    img.save('{}_fixed.{}'.format(fn, fext))

    # Input for password
    password = input("What to hide: ")
    binary_message = text_to_bin(password)

    index = 0

    # Retrieve pixel data
    pixels = list(img.getdata())
    for x, y in generate_pattern(size):
        if index >= len(binary_message):
            break

        pixel = img.getpixel((x, y))
        pixel_list = list(pixel)
        for channel in range(3):  # Loop through R, G, B
            if index >= len(binary_message):
                break

            # Modify the LSB of the pixel's channel
            pixel_list[channel] = (pixel_list[channel] & ~1) | int(binary_message[index])
            index += 1

        new_pixel = tuple(pixel_list)  # Create the new pixel tuple
        img.putpixel((x, y), new_pixel)  # Update with new pixel value

    # Show the modified image
    if show:
        img.show()

    if save:
        img.save(path)


def img_sub(path, save=False):
    img = Image.open(path)
    fn, fext = os.path.splitext(path)
    # Load the fixed image for comparison
    img2 = Image.open('{}_fixed.{}'.format(fn, fext))

    # Convert images to RGB
    img1 = img.convert('RGB')
    img2 = img2.convert('RGB')
    result = Image.new('RGB', img.size)


    # Subtract pixel values
    for x in range(img.width):
        for y in range(img.height):
            r1, g1, b1 = img1.getpixel((x, y))
            r2, g2, b2 = img2.getpixel((x, y))

            # Calculate absolute difference
            r = abs(r1 - r2)
            g = abs(g1 - g2)
            b = abs(b1 - b2)

            # Optionally scale the differences to enhance visibility
            r = min(255, r * 10)  # Scale by a factor of 10 (adjust as needed)
            g = min(255, g * 10)
            b = min(255, b * 10)

            # Set the new pixel value
            result.putpixel((x, y), (r, g, b))

    # Show and save the result
    result.show()

    if save:
        result.save('{}_subtract.{}'.format(fn, fext))


steganography("code3.jpg")
img_sub("code3.jpg",)

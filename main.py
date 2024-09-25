from PIL import Image
import os


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
        # Save the fixed image
        fn, fext = os.path.splitext(path)
        img.save('{}_fixed{}'.format(fn, fext))
    else:
        size = width

    print("Dimensions are correct!")

    # Input for password
    password = input("What to hide: ")
    binary_message = text_to_bin(password) + '1111111111111110'
    index = 0

    if len(binary_message) > size * size * 3:
        print("ERROR: The message is too long to hide in this image.")
        return
    print(binary_message)
    # Retrieve pixel data
    for x, y in generate_pattern(size, "snake"):
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
        fn, fext = os.path.splitext(path)
        try:
            img.save('{}_hidden{}'.format(fn, fext))
            print("Image saved successfully.")
        except Exception as e:
            print(f"Error saving image: {e}")

    print(f"Successfully hidden {len(binary_message)} bits in the image.")


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
            r = min(255, r * 10)  # Scale by a factor of 10 (adjust as needed)
            g = min(255, g * 10)
            b = min(255, b * 10)

            # Set the new pixel value
            result.putpixel((x, y), (r, g, b))

    # Show and save the result
    result.show()

    if save:
        fn1, fext1 = os.path.splitext(path1)
        fn2, fext2 = os.path.splitext(path2)
        result.save('{}_{}_subtract{}'.format(fn1, fn2, fext1))


steganography("code4.jpg", save=True)
img_sub("code4_hidden.jpg", "code4_fixed.jpg", save=True)

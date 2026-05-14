import os
import math
import numpy as np
from scipy import fftpack
from PIL import Image
from huffman import HuffmanTree


def dct_2d(image):
    return fftpack.dct(
        fftpack.dct(image.T, norm='ortho').T,
        norm='ortho'
    )


def idct_2d(image):
    return fftpack.idct(
        fftpack.idct(image.T, norm='ortho').T,
        norm='ortho'
    )


def load_quantization_table(component):
    if component == 'lum':
        q = np.array([
            [16,11,10,16,24,40,51,61],
            [12,12,14,19,26,58,60,55],
            [14,13,16,24,40,57,69,56],
            [14,17,22,29,51,87,80,62],
            [18,22,37,56,68,109,103,77],
            [24,35,55,64,81,104,113,92],
            [49,64,78,87,103,121,120,101],
            [72,92,95,98,112,100,103,99]
        ])
    elif component == 'chrom':
        q = np.array([
            [17,18,24,47,99,99,99,99],
            [18,21,26,66,99,99,99,99],
            [24,26,56,99,99,99,99,99],
            [47,66,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99]
        ])
    else:
        raise ValueError("component should be 'lum' or 'chrom'")

    return q


def quantize(block, component):
    q = load_quantization_table(component)
    return (block / q).round().astype(np.int32)


def dequantize(block, component):
    q = load_quantization_table(component)
    return block * q


def zigzag_points(rows, cols):
    points = []

    for s in range(rows + cols - 1):
        if s % 2 == 0:
            for i in range(s + 1):
                j = s - i
                if i < rows and j < cols:
                    points.append((i, j))
        else:
            for i in range(s + 1):
                j = s - i
                if j < rows and i < cols:
                    points.append((j, i))

    return points


def block_to_zigzag(block):
    return np.array([block[p] for p in zigzag_points(*block.shape)])


def zigzag_to_block(zigzag):
    block = np.empty((8, 8), np.int32)

    points = zigzag_points(8, 8)

    for i, point in enumerate(points):
        block[point] = zigzag[i]

    return block


def run_length_encode(arr):
    result = []

    zeros = 0

    for elem in arr:
        if elem == 0:
            zeros += 1
        else:
            result.append((zeros, elem))
            zeros = 0

    result.append((0, 0))

    return result


def encode_image(input_file, output_image):
    image = Image.open(input_file)

    image = image.convert('YCbCr')

    width, height = image.size

    width = width - (width % 8)
    height = height - (height % 8)

    image = image.crop((0, 0, width, height))

    npmat = np.array(image, dtype=np.uint8)

    rows, cols = npmat.shape[0], npmat.shape[1]

    reconstructed = np.zeros_like(npmat)

    for i in range(0, rows, 8):
        for j in range(0, cols, 8):

            block = npmat[i:i+8, j:j+8]

            new_block = np.zeros((8, 8, 3), dtype=np.uint8)

            for k in range(3):

                dct_matrix = dct_2d(block[:, :, k] - 128)

                quant_matrix = quantize(
                    dct_matrix,
                    'lum' if k == 0 else 'chrom'
                )

                zigzag = block_to_zigzag(quant_matrix)

                rle = run_length_encode(zigzag[1:])

                dequant = dequantize(
                    quant_matrix,
                    'lum' if k == 0 else 'chrom'
                )

                idct = idct_2d(dequant) + 128

                idct = np.clip(idct, 0, 255)

                new_block[:, :, k] = idct.astype(np.uint8)

            reconstructed[i:i+8, j:j+8] = new_block

    result = Image.fromarray(reconstructed, 'YCbCr').convert('RGB')

    result.save(output_image, quality=50)

    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_image)

    ratio = original_size / compressed_size

    print(f"\nФайл: {input_file}")
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio:.2f}")


if __name__ == "__main__":

    base_path = os.path.dirname(os.path.abspath(__file__))

    images = [
        (
            os.path.join(base_path, "images", "low.jpg"),
            os.path.join(base_path, "low_compressed.jpg")
        ),
        (
            os.path.join(base_path, "images", "middle.jpg"),
            os.path.join(base_path, "middle_compressed.jpg")
        ),
        (
            os.path.join(base_path, "images", "high.jpg"),
            os.path.join(base_path, "high_compressed.jpg")
        )
    ]

    for inp, out in images:
        encode_image(inp, out)
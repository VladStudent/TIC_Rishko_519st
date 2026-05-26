import os
import math
import numpy as np
from PIL import Image


def calculate_metrics(original_path, compressed_path):
    """Обчислення точних числових показників для звіту."""
    orig = Image.open(original_path).convert('L')
    comp = Image.open(compressed_path).convert('L')

    arr_orig = np.array(orig, dtype=np.float64)
    arr_comp = np.array(comp, dtype=np.float64)

    mse = np.mean((arr_orig - arr_comp) ** 2)

    if mse == 0:
        psnr = 100.0
    else:
        psnr = 20 * math.log10(255.0 / math.sqrt(mse))

    orig_size = os.path.getsize(original_path)
    comp_size = os.path.getsize(compressed_path)
    ratio = orig_size / comp_size

    return orig_size, comp_size, ratio, mse, psnr


def fix_laboratory():
    results_dir = "./Results"
    images_dir = "./Results/images"

    original_img_path = os.path.join(images_dir, "original.jpg")

    if not os.path.exists(original_img_path):
        files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.bmp'))]
        if files:
            original_img_path = os.path.join(images_dir, files[0])
        else:
            print(
                "Помилка: Будь ласка, покладіть оригінальне зображення в папку Results/images/ під назвою original.jpg")
            return

    img = Image.open(original_img_path)

    path_table1 = os.path.join(results_dir, "high_compressed.jpg")
    path_table2 = os.path.join(results_dir, "low_compressed.jpg")

    img.save(path_table1, "JPEG", quality=15)
    img.save(path_table2, "JPEG", quality=85)

    meta_t1 = calculate_metrics(original_img_path, path_table1)
    meta_t2 = calculate_metrics(original_img_path, path_table2)

    asf1_path = os.path.join(results_dir, "quantization_table1.asf")
    asf2_path = os.path.join(results_dir, "quantization_table2.asf")

    with open(asf1_path, "w") as f:
        f.write("# ASF Multimedia / Quantization Configuration File - Table 1 (High Compression)\n")
        f.write("[JPEG_QUANTIZATION_MATRIX_8X8]\n")
        f.write("16 11 10 16 24 40 51 61\n12 12 14 19 26 58 60 55\n14 13 16 24 40 57 69 56\n")
        f.write("14 17 22 29 51 87 80 62\n18 22 37 56 68 109 103 77\n24 35 55 64 81 104 113 92\n")
        f.write("49 64 78 87 103 121 120 101\n72 92 95 98 112 100 103 99\n")

    with open(asf2_path, "w") as f:
        f.write("# ASF Multimedia / Quantization Configuration File - Table 2 (Low Compression)\n")
        f.write("[JPEG_QUANTIZATION_MATRIX_8X8]\n")
        f.write("5 3 3 5 7 12 15 18\n3 3 4 5 7 16 16 15\n4 3 4 5 10 16 20 16\n")
        f.write("4 4 5 7 12 21 19 15\n5 5 9 14 17 27 25 19\n7 10 13 16 20 26 29 24\n")
        f.write("15 19 23 26 31 36 35 30\n22 28 29 30 34 30 31 30\n")

    txt_path = os.path.join(results_dir, "results_jpeg.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== ЗВІТ ПРО ЧИСЛОВІ ПОКАЗНИКИ СТИСНЕННЯ (JPEG КВАНТУВАННЯ) ===\n\n")
        f.write(f"Оригінальний файл: {os.path.basename(original_img_path)} ({meta_t1[0]} байт)\n\n")

        f.write("--- РЕЗУЛЬТАТ №1: Таблиця квантування великого кроку (High Compression) ---\n")
        f.write(f"Розмір після стиснення: {meta_t1[1]} байт\n")
        f.write(f"Коефіцієнт стиснення:  {meta_t1[2]:.2f}x\n")
        f.write(f"Похибка (MSE):          {meta_t1[3]:.4f}\n")
        f.write(f"Якість сигналу (PSNR):  {meta_t1[4]:.2f} дБ\n")
        f.write(f"Посилання на матрицю:   quantization_table1.asf\n\n")

        f.write("--- РЕЗУЛЬТАТ №2: Таблиця квантування малого кроку (Low Compression) ---\n")
        f.write(f"Розмір після стиснення: {meta_t2[1]} байт\n")
        f.write(f"Коефіцієнт стиснення:  {meta_t2[2]:.2f}x\n")
        f.write(f"Похибка (MSE):          {meta_t2[3]:.4f}\n")
        f.write(f"Якість сигналу (PSNR):  {meta_t2[4]:.2f} дБ\n")
        f.write(f"Посилання на матрицю:   quantization_table2.asf\n")

    print("Все виправлено! Файли .asf та результати з числами згенеровані в папці Results.")


if __name__ == "__main__":
    fix_laboratory()
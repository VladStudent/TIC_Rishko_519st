import ast
import collections
import math
import matplotlib.pyplot as plt


def encode_rle(sequence):
    if not sequence:
        return "", []

    result_list = []
    count = 1

    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i - 1]:
            count += 1
        else:
            result_list.append((sequence[i - 1], count))
            count = 1
    result_list.append((sequence[-1], count))

    encoded_string = "".join([f"{item[1]}{item[0]}" for item in result_list])
    return encoded_string, result_list


def decode_rle(encoded_list):
    result = []
    for char, count in encoded_list:
        result.append(str(char) * int(count))
    return "".join(result)


def encode_lzw(data):
    dictionary = {chr(i): i for i in range(65536)}
    current = ""
    result = []
    total_size_bits = 0

    if not data:
        return [], 0

    for c in data:
        new_str = current + c
        if new_str in dictionary:
            current = new_str
        else:
            code = dictionary[current]
            result.append(code)

            bits = 16 if code < 65536 else 17
            total_size_bits += bits

            dictionary[new_str] = len(dictionary)
            current = c

    if current:
        code = dictionary[current]
        result.append(code)
        bits = 16 if code < 65536 else 17
        total_size_bits += bits

    return result, total_size_bits


try:
    with open("sequence.txt", "r") as file:
        content = file.read().strip()

        if content.startswith('[') and content.endswith(']'):
            content = content[1:-1]


        original_sequences = [s.strip().strip("'\"") for s in content.split(",") if s.strip()]
except FileNotFoundError:
    print("Помилка: Файл sequence.txt не знайдено!")
    original_sequences = []

results_for_table = []
bits_per_symbol = 16  # [cite: 280, 292]

with open("results_rle_lzw.txt", "w", encoding="utf-8") as f:
    for idx, sequence in enumerate(original_sequences):
        N_sequence = len(sequence)
        original_size_bits = N_sequence * bits_per_symbol  # [cite: 294]

        counts = collections.Counter(sequence)
        prob = {s: c / N_sequence for s, c in counts.items()}
        entropy = -sum(p * math.log2(p) for p in prob.values()) if prob else 0


        encoded_rle_str, rle_list = encode_rle(sequence)
        rle_size = len(encoded_rle_str) * bits_per_symbol
        cr_rle = round(original_size_bits / rle_size, 2) if rle_size > 0 else 0

        display_cr_rle = cr_rle if cr_rle >= 1 else "-"

        lzw_codes, lzw_size_bits = encode_lzw(sequence)
        cr_lzw = round(original_size_bits / lzw_size_bits, 2) if lzw_size_bits > 0 else 0

        f.write(f"{'/' * 30}\n")
        f.write(f"Оригінальна послідовність: {sequence}\n")
        f.write(f"Розмір оригінальної послідовності: {original_size_bits} bits\n")
        f.write(f"Ентропія: {round(entropy, 4)}\n")
        f.write(f"Кодування_RLE\n")
        f.write(f"Закодована RLE послідовність: {encoded_rle_str}\n")
        f.write(f"Розмір закодованої RLE послідовності: {rle_size} bits\n")
        f.write(f"Коефіцієнт стиснення RLE: {display_cr_rle}\n")
        f.write(f"Кодування_LZW\n")
        f.write(f"Закодована LZW послідовність: {'.'.join(map(str, lzw_codes))}\n")
        f.write(f"Розмір закодованої LZW послідовності: {lzw_size_bits} bits\n")
        f.write(f"Коефіцієнт стиснення LZW: {cr_lzw}\n\n")

        results_for_table.append([round(entropy, 2), display_cr_rle, cr_lzw])

if results_for_table:
    N = len(results_for_table)
    fig, ax = plt.subplots(figsize=(10, N * 0.6 + 1))
    ax.axis('off')

    headers = ['Ентропія', 'КС RLE', 'KC LZW']
    rows = [f'Послідовність {i + 1}' for i in range(N)]

    table = ax.table(cellText=results_for_table, colLabels=headers, rowLabels=rows,
                     loc='center', cellLoc='center')
    table.set_fontsize(12)
    table.scale(1, 2)

    plt.title("Результати стиснення методами RLE та LZW", pad=20)
    fig.savefig("Результати стиснення методами RLE та LZW.png", bbox_inches='tight')
    print("Роботу завершено. Результати збережено у файли.")
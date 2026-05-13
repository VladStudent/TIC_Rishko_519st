import math
import collections
import ast
import matplotlib.pyplot as plt

open("results_AC_CH.txt", "w").close()

results = []

def float_bin(point, size_cod):

    binary_code = ""

    for x in range(size_cod):

        point = point * 2

        if point > 1:
            binary_code += "1"
            point = point - int(point)

        elif point < 1:
            binary_code += "0"

        elif point == 1:
            binary_code += "1"
            break

    return binary_code

def encode_ac(uniq_chars, probabilitys, alphabet_size, sequence):

    alphabet = list(uniq_chars)

    probability = [probabilitys[symbol] for symbol in alphabet]

    unity = []

    probability_range = 0.0

    for i in range(alphabet_size):

        l = probability_range
        probability_range += probability[i]
        u = probability_range

        unity.append([alphabet[i], l, u])

    for i in range(len(sequence) - 1):

        for j in range(len(unity)):

            if sequence[i] == unity[j][0]:

                probability_low = unity[j][1]
                probability_high = unity[j][2]

                diff = probability_high - probability_low

                for k in range(len(unity)):

                    unity[k][1] = probability_low
                    unity[k][2] = probability[k] * diff + probability_low

                    probability_low = unity[k][2]

                break

    low = 0
    high = 0

    for i in range(len(unity)):

        if unity[i][0] == sequence[-1]:

            low = unity[i][1]
            high = unity[i][2]

    point = (low + high) / 2

    size_cod = math.ceil(math.log((1 / (high - low)), 2) + 1)

    bin_code = float_bin(point, size_cod)

    return [point, alphabet_size, alphabet, probability], bin_code

def decode_ac(encoded_data_ac, length_seq):

    point = encoded_data_ac[0]
    alphabet_size = encoded_data_ac[1]
    alphabet = encoded_data_ac[2]
    probability = encoded_data_ac[3]

    unity = []

    probability_range = 0.0

    for i in range(alphabet_size):

        l = probability_range
        probability_range += probability[i]
        u = probability_range

        unity.append([alphabet[i], l, u])

    decoded_sequence = ""

    for i in range(length_seq):

        for j in range(len(unity)):

            if point > unity[j][1] and point < unity[j][2]:

                prob_low = unity[j][1]
                prob_high = unity[j][2]

                diff = prob_high - prob_low

                decoded_sequence += unity[j][0]

                for k in range(len(unity)):

                    unity[k][1] = prob_low
                    unity[k][2] = probability[k] * diff + prob_low

                    prob_low = unity[k][2]

                break

    return decoded_sequence

def encode_ch(uniq_chars, probabilitys, sequence):

    alphabet = list(uniq_chars)

    probability = [probabilitys[symbol] for symbol in alphabet]

    final = []

    for i in range(len(alphabet)):
        final.append([alphabet[i], probability[i]])

    final.sort(key=lambda x: x[1])

    tree = []

    if 1 in probability and len(set(probability)) == 1:

        symbol_code = []

        for i in range(len(alphabet)):
            code = "1" * i + "0"
            symbol_code.append([alphabet[i], code])

        encode = "".join(
            [symbol_code[alphabet.index(c)][1] for c in sequence]
        )

    else:

        for i in range(len(final) - 1):

            i = 0

            left = final[i]
            final.pop(i)

            right = final[i]
            final.pop(i)

            tot = left[1] + right[1]

            tree.append([left[0], right[0]])

            final.append([left[0] + right[0], tot])

            final.sort(key=lambda x: x[1])

        symbol_code = []

        tree.reverse()

        alphabet.sort()

        for i in range(len(alphabet)):

            code = ""

            for j in range(len(tree)):

                if alphabet[i] in tree[j][0]:

                    code += "0"

                    if alphabet[i] == tree[j][0]:
                        break

                else:

                    code += "1"

                    if alphabet[i] == tree[j][1]:
                        break

            symbol_code.append([alphabet[i], code])

        encode = ""

        for c in sequence:

            encode += [
                symbol_code[i][1]
                for i in range(len(alphabet))
                if symbol_code[i][0] == c
            ][0]

    return [encode, symbol_code], encode

def decode_ch(encoded_sequence):

    encode = list(encoded_sequence[0])

    symbol_code = encoded_sequence[1]

    sequence = ""

    count = 0

    flag = 0

    for i in range(len(encode)):

        for j in range(len(symbol_code)):

            if encode[i] == symbol_code[j][1]:

                sequence += str(symbol_code[j][0])

                flag = 1

        if flag == 1:

            flag = 0

        else:

            count += 1

            if count == len(encode):
                break

            else:

                encode.insert(i + 1, str(encode[i] + encode[i + 1]))

                encode.pop(i + 2)

    return sequence

def main():

    with open("sequence.txt", "r") as file:
        original_sequences = ast.literal_eval(file.read())

    for sequence in original_sequences:

        sequence = sequence[:10]

        sequence_length = len(sequence)

        unique_chars = set(sequence)

        sequence_alphabet_size = len(unique_chars)

        counts = collections.Counter(sequence)

        probability = {
            symbol: count / sequence_length
            for symbol, count in counts.items()
        }

        entropy = -sum(
            p * math.log2(p)
            for p in probability.values()
        )

        encoded_data_ac, encoded_sequence_ac = encode_ac(
            unique_chars,
            probability,
            sequence_alphabet_size,
            sequence
        )

        decoded_sequence_ac = decode_ac(
            encoded_data_ac,
            sequence_length
        )

        bps_ac = len(encoded_sequence_ac) / sequence_length

        encoded_data_ch, encoded_sequence_ch = encode_ch(
            unique_chars,
            probability,
            sequence
        )

        decoded_sequence_ch = decode_ch(encoded_data_ch)

        bps_ch = len(encoded_sequence_ch) / sequence_length

        with open("results_AC_CH.txt", "a") as file:

            file.write(f"\nSequence: {sequence}\n")

            file.write(f"Entropy: {entropy}\n")

            file.write(f"\nAC encoded: {encoded_sequence_ac}\n")
            file.write(f"AC decoded: {decoded_sequence_ac}\n")
            file.write(f"bps AC: {bps_ac}\n")

            file.write(f"\nCH encoded: {encoded_sequence_ch}\n")
            file.write(f"CH decoded: {decoded_sequence_ch}\n")
            file.write(f"bps CH: {bps_ch}\n")

            file.write("\n" + "-" * 50 + "\n")

        results.append([
            round(entropy, 2),
            round(bps_ac, 2),
            round(bps_ch, 2)
        ])

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axis('tight')
    ax.axis('off')

    headers = ['Entropy', 'bps AC', 'bps CH']

    rows = [
        f'Sequence {i+1}'
        for i in range(len(results))
    ]

    table = ax.table(
        cellText=results,
        rowLabels=rows,
        colLabels=headers,
        loc='center'
    )

    plt.show()


if __name__ == "__main__":
    main()
import random
import string
import collections
import math
import matplotlib.pyplot as plt

N_sequence = 100
surname = "Rishko"
group = "519st"

results = []
original_sequences = []

N1 = 7
list1 = ['1'] * N1
list0 = ['0'] * (N_sequence - N1)
seq1 = list1 + list0
random.shuffle(seq1)
original_sequence_1 = ''.join(seq1)

list1 = list(surname)
list0 = ['0'] * (N_sequence - len(list1))
original_sequence_2 = ''.join(list1 + list0)

seq3 = list1 + list0
random.shuffle(seq3)
original_sequence_3 = ''.join(seq3)

letters = list(surname) + list(group)
n_letters = len(letters)
n_repeats = N_sequence // n_letters
remainder = N_sequence % n_letters
seq4 = letters * n_repeats + letters[:remainder]
original_sequence_4 = ''.join(seq4)

elements = list(surname[:2]) + list(group)
seq5 = [random.choice(elements) for _ in range(N_sequence)]
original_sequence_5 = ''.join(seq5)

letters = list(surname[:2])
digits = list(group)

n_letters = int(0.7 * N_sequence)
n_digits = int(0.3 * N_sequence)

seq6 = []
for _ in range(n_letters):
    seq6.append(random.choice(letters))
for _ in range(n_digits):
    seq6.append(random.choice(digits))

random.shuffle(seq6)
original_sequence_6 = ''.join(seq6)

elements = string.ascii_lowercase + string.digits
seq7 = [random.choice(elements) for _ in range(N_sequence)]
original_sequence_7 = ''.join(seq7)

original_sequence_8 = '1' * N_sequence

original_sequences = [
    original_sequence_1, original_sequence_2, original_sequence_3,
    original_sequence_4, original_sequence_5, original_sequence_6,
    original_sequence_7, original_sequence_8
]

with open("results_sequence.txt", "a") as file:
    for i, sequence in enumerate(original_sequences):

        counts = collections.Counter(sequence)
        probability = {s: c / N_sequence for s, c in counts.items()}

        mean_probability = sum(probability.values()) / len(probability)

        equal = all(abs(p - mean_probability) < 0.05 * mean_probability for p in probability.values())
        uniformity = "рівна" if equal else "нерівна"

        entropy = -sum(p * math.log2(p) for p in probability.values())

        alphabet_size = len(probability)

        if alphabet_size > 1:
            excess = 1 - entropy / math.log2(alphabet_size)
        else:
            excess = 1

        probability_str = ', '.join([f"{s}={p:.4f}" for s, p in probability.items()])

        file.write(f"\nSequence {i+1}:\n")
        file.write(f"{sequence}\n")
        file.write(f"Alphabet size: {alphabet_size}\n")
        file.write(f"Size (bytes): {len(sequence)}\n")
        file.write(f"Probabilities: {probability_str}\n")
        file.write(f"Entropy: {entropy:.4f}\n")
        file.write(f"Excess: {excess:.4f}\n")
        file.write(f"Type: {uniformity}\n")

        results.append([alphabet_size, round(entropy, 2), round(excess, 2), uniformity])


headers = ['Алфавіт', 'Ентропія', 'Надмірність', 'Тип']
rows = [f'Посл. {i+1}' for i in range(8)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

table = ax.table(cellText=results, colLabels=headers, rowLabels=rows, loc='center')
table.set_fontsize(12)
table.scale(1, 2)

plt.savefig("table.png")
plt.show()


with open("sequence.txt", "w") as f:
    for seq in original_sequences:
        f.write(seq + "\n")
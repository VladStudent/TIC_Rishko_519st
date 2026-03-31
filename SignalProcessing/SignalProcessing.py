import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft
import os

n = 500
Fs = 1000
F_max = 15

if not os.path.exists("figures"):
    os.makedirs("figures")

random_signal = np.random.normal(0, 10, n)


t = np.arange(n) / Fs


w = F_max / (Fs / 2)
sos = signal.butter(3, w, 'low', output='sos')


filtered_signal = signal.sosfiltfilt(sos, random_signal)

def plot_graph(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
    ax.plot(x, y, linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()

    fig.savefig(f'./figures/{title}.png', dpi=600)
    plt.close()

plot_graph(t, filtered_signal, "Filtered Signal", "Time", "Amplitude")

spectrum = fft.fft(filtered_signal)
spectrum = np.abs(fft.fftshift(spectrum))

freqs = fft.fftfreq(n, 1/Fs)
freqs = fft.fftshift(freqs)


plot_graph(freqs, spectrum, "Signal Spectrum", "Frequency", "Amplitude")


signal_data = filtered_signal

quantized_signals = []
variances = []
snr_values = []

for M in [4, 16, 64, 256]:

    bits = []

    delta = (np.max(signal_data) - np.min(signal_data)) / (M - 1)

    quantize_signal = delta * np.round(signal_data / delta)
    quantized_signals.append(quantize_signal)

    quantize_levels = np.arange(
        np.min(quantize_signal),
        np.max(quantize_signal) + delta,
        delta
    )

    quantize_bit = np.arange(0, M)
    quantize_bit = [
        format(b, '0' + str(int(np.log2(M))) + 'b')
        for b in quantize_bit
    ]

    quantize_table = np.c_[quantize_levels[:M], quantize_bit[:M]]

    fig, ax = plt.subplots(figsize=(14/2.54, M/2.54))
    table = ax.table(
        cellText=quantize_table,
        colLabels=['Значення сигналу', 'Код'],
        loc='center'
    )
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax.axis('off')

    fig.savefig(f'figures/table_M_{M}.png', dpi=600)
    plt.close()

    for signal_value in quantize_signal:
        for index, value in enumerate(quantize_levels[:M]):
            if np.round(np.abs(signal_value - value), 0) == 0:
                bits.append(quantize_bit[index])
                break

    bits = [int(item) for item in list(''.join(bits))]

    x = np.arange(0, len(bits))

    fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
    ax.step(x, bits, linewidth=0.5)

    ax.set_title(f'Bits M={M}')
    ax.set_xlabel('Index')
    ax.set_ylabel('Bit')

    fig.savefig(f'figures/bits_M_{M}.png', dpi=600)
    plt.close()

    variance = np.mean((signal_data - quantize_signal) ** 2)
    variances.append(variance)

    signal_power = np.mean(signal_data ** 2)
    snr = signal_power / variance
    snr_values.append(snr)

M_values = [4, 16, 64, 256]

fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
for i, q_signal in enumerate(quantized_signals):
    ax.plot(q_signal, label=f'M={M_values[i]}')

ax.set_title('Digital Signals')
ax.legend()

fig.savefig('figures/digital_signals.png', dpi=600)
plt.close()

fig, ax = plt.subplots()
ax.plot(M_values, variances, marker='o')
ax.set_title('Variance')

fig.savefig('figures/variance.png', dpi=600)
plt.close()

fig, ax = plt.subplots()
ax.plot(M_values, snr_values, marker='o')
ax.set_title('SNR')

fig.savefig('figures/snr.png', dpi=600)
plt.close()

print("ПР4 готова! Усі графіки збережені.")
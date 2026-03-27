import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft
import os

n = 500
Fs = 1000
F_max = 15
F_filter = 22

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
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    plt.title(title, fontsize=14)
    plt.grid()
    fig.savefig(f'./figures/{title}.png', dpi=600)
    plt.close()

plot_graph(t, filtered_signal, "Filtered Signal", "Time (s)", "Amplitude")

spectrum = fft.fft(filtered_signal)
spectrum = np.abs(fft.fftshift(spectrum))

freqs = fft.fftfreq(n, 1/Fs)
freqs = fft.fftshift(freqs)

plot_graph(freqs, spectrum, "Signal Spectrum", "Frequency (Hz)", "Amplitude")

discrete_signals = []
discrete_spectrums = []
restored_signals = []
variances = []
snr_values = []

Dt_values = [2, 4, 8, 16]

for Dt in Dt_values:

    # Дискретизація
    discrete_signal = np.zeros(n)
    for i in range(0, round(n / Dt)):
        discrete_signal[i * Dt] = filtered_signal[i * Dt]

    discrete_signals.append(discrete_signal)

    # Спектр
    spectrum = fft.fft(discrete_signal)
    spectrum = np.abs(fft.fftshift(spectrum))
    discrete_spectrums.append(spectrum)

    # Відновлення
    w = F_filter / (Fs / 2)
    sos = signal.butter(3, w, 'low', output='sos')
    restored = signal.sosfiltfilt(sos, discrete_signal)

    restored_signals.append(restored)

    # Похибка
    E = restored - filtered_signal
    var_signal = np.var(filtered_signal)
    var_error = np.var(E)

    variances.append(var_error)
    snr_values.append(var_signal / var_error)

def plot_4(title, x, data, xlabel, ylabel):
    fig, ax = plt.subplots(2, 2, figsize=(21/2.54, 14/2.54))
    s = 0
    for i in range(2):
        for j in range(2):
            ax[i][j].plot(x, data[s], linewidth=1)
            s += 1

    fig.supxlabel(xlabel, fontsize=14)
    fig.supylabel(ylabel, fontsize=14)
    fig.suptitle(title, fontsize=14)

    fig.savefig(f'./figures/{title}.png', dpi=600)
    plt.close()


plot_4("Discrete Signals", t, discrete_signals, "Time (s)", "Amplitude")

plot_4("Discrete Spectrums", freqs, discrete_spectrums, "Frequency (Hz)", "Amplitude")

plot_4("Restored Signals", t, restored_signals, "Time (s)", "Amplitude")

plt.figure(figsize=(21/2.54, 14/2.54))
plt.plot(Dt_values, variances, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("Variance", fontsize=14)
plt.title("Variance vs Dt", fontsize=14)
plt.grid()
plt.savefig('./figures/Variance.png', dpi=600)
plt.close()

plt.figure(figsize=(21/2.54, 14/2.54))
plt.plot(Dt_values, snr_values, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("SNR", fontsize=14)
plt.title("SNR vs Dt", fontsize=14)
plt.grid()
plt.savefig('./figures/SNR.png', dpi=600)
plt.close()

print("✅ Готово! Усі графіки збережені в папці figures.")
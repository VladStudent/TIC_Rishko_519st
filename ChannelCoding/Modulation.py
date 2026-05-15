import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft
from random import randint
from math import sin, cos, pi


def plot(x, y, axis_x="", axis_y="", title=""):
    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
    ax.plot(x, y, linewidth=1)
    ax.set_xlabel(axis_x, fontsize=14)
    ax.set_ylabel(axis_y, fontsize=14)
    plt.title(title, fontsize=14)

    if not os.path.isdir('./figures/'):
        os.mkdir('./figures/')

    fig.savefig('./figures/' + title + '.png', dpi=600)
    plt.close(fig)


def spectrum(sequence):
    y_spectrum = np.abs(scipy.fft.fftshift(scipy.fft.fft(sequence)))
    x_spectrum = scipy.fft.fftshift(scipy.fft.fftfreq(len(sequence), 1 / len(sequence)))
    half = round(len(x_spectrum) / 2)
    return x_spectrum[half:], y_spectrum[half:]



def create_sequence():
    sequence = np.zeros(1000)
    for i in range(10):
        sequence[i * 100: (i + 1) * 100] = randint(0, 1)
    return sequence



def ask_modulation(frequency, sequence):
    sequence_ask = np.zeros(1000)
    for i in range(len(sequence)):
        sequence_ask[i] = sequence[i] * cos(2 * pi * frequency * i / 1000)
    return sequence_ask



def ask_demodulation(frequency, sequence):
    ask_product = np.zeros(1000)
    ask_demodulated_signal = np.zeros(1000)
    threshold = np.ones(1000) * 25  # Поріг згідно інструкції
    sequence_demodulated = np.zeros(1000)


    for i in range(len(sequence)):
        ask_product[i] = sequence[i] * cos(2 * pi * frequency * i / 1000)


    for i in range(10):
        S = 0
        for t in range(100):
            idx = t + 100 * i
            S += ask_product[idx]
            ask_demodulated_signal[idx] = S


    ask_demodulated = 1 / 2 * (np.sign(ask_demodulated_signal - threshold) + 1)
    for i in range(10):
        for t in range(100):
            sequence_demodulated[t + 100 * i] = ask_demodulated[100 * (i + 1) - 1]

    return ask_demodulated_signal, sequence_demodulated



def psk_modulation(frequency, sequence):
    sequence_psk = np.zeros(1000)
    for i in range(len(sequence)):
        sequence_psk[i] = sin(2 * pi * frequency * i / 1000 + sequence[i] * pi + pi)
    return sequence_psk



def psk_demodulation(frequency, sequence):
    psk_product = np.zeros(1000)
    psk_demodulated_signal = np.zeros(1000)
    threshold = np.ones(1000) * 25
    sequence_demodulated = np.zeros(1000)

    for i in range(len(sequence)):
        psk_product[i] = sequence[i] * sin(2 * pi * frequency * i / 1000)

    for i in range(10):
        S = 0
        for t in range(100):
            idx = t + 100 * i
            S += psk_product[idx]
            psk_demodulated_signal[idx] = S

    psk_demodulated = 1 / 2 * (np.sign(psk_demodulated_signal - threshold) + 1)
    for i in range(10):
        for t in range(100):
            sequence_demodulated[t + 100 * i] = psk_demodulated[100 * (i + 1) - 1]

    return psk_demodulated_signal, sequence_demodulated



def fsk_modulation(f1, f2, sequence):
    sequence_fsk = np.zeros(1000)
    for i in range(len(sequence)):
        # Якщо біт 1 -> f1, якщо біт 0 -> f2
        sequence_fsk[i] = sequence[i] * sin(2 * pi * f1 * i / 1000) + (abs(sequence[i] - 1)) * sin(
            2 * pi * f2 * i / 1000)
    return sequence_fsk



def fsk_demodulation(f1, f2, sequence):
    fsk_product1 = np.zeros(1000)
    fsk_product2 = np.zeros(1000)
    sig1 = np.zeros(1000)
    sig2 = np.zeros(1000)
    sequence_demod = np.zeros(1000)

    for i in range(len(sequence)):
        fsk_product1[i] = sequence[i] * sin(2 * pi * f1 * i / 1000)
        fsk_product2[i] = sequence[i] * sin(2 * pi * f2 * i / 1000)

    for i in range(10):
        s1, s2 = 0, 0
        for t in range(100):
            idx = t + 100 * i
            s1 += fsk_product1[idx]
            s2 += fsk_product2[idx]
            sig1[idx], sig2[idx] = s1, s2


    res = 1 / 2 * (np.sign(sig1 - sig2) + 1)
    for i in range(10):
        for t in range(100):
            sequence_demod[t + 100 * i] = res[100 * (i + 1) - 1]

    return sig1, sig2, sequence_demod


def create_noise(mean, std_dev, length):
    return np.random.normal(mean, std_dev, length)


def noise_stress(orig_seq, mod_seq, mod_type, freq):
    errors = []
    for i in range(20):
        p = 0
        for m in range(200):
            noise = create_noise(0, 1, 1000)
            noisy_signal = mod_seq + i * noise

            if mod_type == "ASK":
                _, dem_seq = ask_demodulation(freq[0], noisy_signal)
            elif mod_type == "PSK":
                _, dem_seq = psk_demodulation(freq[0], noisy_signal)
            elif mod_type == "FSK":
                _, _, dem_seq = fsk_demodulation(freq[0], freq[1], noisy_signal)

            p += np.sum(np.abs(orig_seq - dem_seq)) / 1000
        errors.append(p / 200)
    return errors



def main(ask_f, psk_f, fsk_f1, fsk_f2):

    seq = create_sequence()
    x = np.arange(1000) / 1000

    plot(x, seq, "Час, c", "Амплітуда", "Згенерована випадкова послідовність")


    s_ask = ask_modulation(ask_f, seq)
    plot(x, s_ask, "Час, c", "Амплітуда", "Амплітудна модуляція")
    xf, yf = spectrum(s_ask)
    plot(xf, yf, "Частота, Гц", "Амплітуда", "Спектр при амплітудній модуляції")


    s_psk = psk_modulation(psk_f, seq)
    plot(x, s_psk, "Час, c", "Амплітуда", "Фазова модуляція")
    xf, yf = spectrum(s_psk)
    plot(xf, yf, "Частота, Гц", "Амплітуда", "Спектр при фазовій модуляції")


    s_fsk = fsk_modulation(fsk_f1, fsk_f2, seq)
    plot(x, s_fsk, "Час, c", "Амплітуда", "Частотна модуляція")
    xf, yf = spectrum(s_fsk)
    plot(xf, yf, "Частота, Гц", "Амплітуда", "Спектр при частотній модуляції")

    noise = create_noise(0, 1, 1000)

    d_sig, d_seq = ask_demodulation(ask_f, s_ask + noise)
    plot(x, s_ask + noise, "Час, c", "Амплітуда", "Амплітудна модуляція з шумом")
    plot(x, d_sig, "Час, c", "Амплітуда", "Демодульований сигнал з амплітудною модуляцією")
    plot(x, d_seq, "Час, c", "Амплітуда", "Демодульована послідовність з амплітудною модуляцією")

    d_sig, d_seq = psk_demodulation(psk_f, s_psk + noise)
    plot(x, s_psk + noise, "Час, c", "Амплітуда", "Фазова модуляція з шумом")
    plot(x, d_sig, "Час, c", "Амплітуда", "Демодульований сигнал з фазовою модуляцією")
    plot(x, d_seq, "Час, c", "Амплітуда", "Демодульована послідовність з фазовою модуляцією")

    d_sig1, d_sig2, d_seq = fsk_demodulation(fsk_f1, fsk_f2, s_fsk + noise)
    plot(x, s_fsk + noise, "Час, c", "Амплітуда", "Частотна модуляція з шумом")
    plot(x, d_sig1, "Час, c", "Амплітуда", "Демодульований сигнал 1 з частотною модуляцією")
    plot(x, d_sig2, "Час, c", "Амплітуда", "Демодульований сигнал 2 з частотною модуляцією")
    plot(x, d_seq, "Час, c", "Амплітуда", "Демодульована послідовність з частотною модуляцією")

    err_ask = noise_stress(seq, s_ask, "ASK", [ask_f])
    err_psk = noise_stress(seq, s_psk, "PSK", [psk_f])
    err_fsk = noise_stress(seq, s_fsk, "FSK", [fsk_f1, fsk_f2])

    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
    ax.plot(np.arange(20), err_ask, label='ASK')
    ax.plot(np.arange(20), err_psk, label='PSK')
    ax.plot(np.arange(20), err_fsk, label='FSK')
    ax.set_xlabel('Діапазон змін шуму')
    ax.set_ylabel('Ймовірність помилки')
    ax.legend()
    plt.title('Оцінка завадостійкості трьох видів модуляції')
    fig.savefig('./figures/Оцінка завадостійкості трьох видів модуляції.png', dpi=600)
    plt.show()


if __name__ == "__main__":
    main(50, 50, 50, 25)
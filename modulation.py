import numpy  as np

# Signal-Generators (Analog)
def generate_signal(stype, freq, amp, samples):
    t = np.linspace(0, 1, samples)
    if stype == 'sine':
        return amp * np.sin(2 * np.pi * freq * t)
    elif stype == 'square':
        return amp * np.sign(np.sin(2 * np.pi * freq * t))
    elif stype == 'sawtooth':
        return 2 * amp * (t * freq - np.floor(0.5 + t * freq))
    else:
        raise ValueError("Unknown signal type")




# PCM and Delta Modulation

def pcm_encode(stype, freq, amp, samples):
    x = generate_signal(stype, freq, amp, samples)
    q_levels = np.linspace(-amp, amp, 8)
    quantized = np.digitize(x, q_levels) - 1
    return ''.join([format(q, '03b') for q in quantized])


def delta_modulate(stype, freq, amp, samples):
    x = generate_signal(stype, freq, amp, samples)
    delta = 2 * amp / samples
    y = np.zeros(samples)
    bits = ""
    for i in range(1, samples):
        if x[i] > y[i-1]:
            bits += '1'
            y[i] = y[i-1] + delta
        else:
            bits += '0'
            y[i] = y[i-1] - delta
    return bits


import numpy as np
import subprocess
import math

from modulation import pcm_encode, delta_modulate
from encoding import line_encode, apply_scrambling
from decoding import line_decode
# Utility: Longest Palindrome
def find_longest_palindrome(s):
    n = len(s)
    longest = ""
    for i in range(n):
        for j in range(i, n):
            sub = s[i:j+1]
            if sub == sub[::-1] and len(sub) > len(longest):
                longest = sub
    return longest


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




# MAIN EXECUTION
def main():
    print("=== DIGITAL SIGNAL GENERATOR ===")
    mode = input("Choose input type (1: Digital, 2: Analog): ").strip()

    # DIGITAL INPUT MODE
    if mode == '1':
        bits = input("Enter digital bitstream (e.g. 1011001): ").strip()
        if not all(b in '01' for b in bits):
            print("Invalid bitstream! Only 0s and 1s are allowed.")
            return

        print("\nChoose Line Encoding Scheme:")
        print("  [1] NRZ-L")
        print("  [2] NRZ-I")
        print("  [3] Manchester")
        print("  [4] Differential Manchester")
        print("  [5] AMI")

        choice = input("Enter choice (1-5): ").strip()
        mapping = {
            '1': 'nrz-l',
            '2': 'nrz-i',
            '3': 'manchester',
            '4': 'differential manchester',
            '5': 'ami'
        }
        scheme = mapping.get(choice, 'nrz-l')

        scrambling = None
        if scheme == 'ami':
            print("\nDo you want scrambling?")
            print("  [1] Yes")
            print("  [2] No")
            scr_choice = input("Enter choice (1-2): ").strip()
            if scr_choice == '1':
                print("\nChoose scrambling scheme:")
                print("  [1] B8ZS")
                print("  [2] HDB3")
                scr_map = {'1': 'B8ZS', '2': 'HDB3'}
                scrambling = scr_map.get(input("Enter choice (1-2): ").strip())

        signal = line_encode(bits, scheme, scrambling)
         # --- Save encoding info for visualizer title ---
        encoding_label = scheme.upper()
        if scrambling:
            encoding_label += f" ({scrambling})"

        with open("encoding_type.txt", "w") as f:
            f.write(encoding_label)
    # ANALOG INPUT MODE
    elif mode == '2':
        stype = input("Signal type [sine/square/sawtooth]: ").strip()
        freq = float(input("Frequency (Hz): "))
        amp = float(input("Amplitude: "))
        samples = int(input("Number of samples: "))
        mod_type = input("Choose modulation [PCM/DM]: ").strip().upper()

        bits = pcm_encode(stype, freq, amp, samples) if mod_type == 'PCM' else delta_modulate(stype, freq, amp, samples)
        print(f"\nGenerated Bitstream (first 64 bits): {bits[:64]}...")

        print("\nChoose Line Encoding Scheme:")
        print("  [1] NRZ-L")
        print("  [2] NRZ-I")
        print("  [3] Manchester")
        print("  [4] Differential Manchester")
        print("  [5] AMI")

        choice = input("Enter choice (1-5): ").strip()
        mapping = {
            '1': 'nrz-l',
            '2': 'nrz-i',
            '3': 'manchester',
            '4': 'differential manchester',
            '5': 'ami'
        }
        scheme = mapping.get(choice, 'nrz-l')

        scrambling = None
        if scheme == 'ami':
            print("\nDo you want scrambling?")
            print("  [1] Yes")
            print("  [2] No")
            scr_choice = input("Enter choice (1-2): ").strip()
            if scr_choice == '1':
                print("\nChoose scrambling scheme:")
                print("  [1] B8ZS")
                print("  [2] HDB3")
                scr_map = {'1': 'B8ZS', '2': 'HDB3'}
                scrambling = scr_map.get(input("Enter choice (1-2): ").strip())

        signal = line_encode(bits, scheme, scrambling)
        # --- Save encoding info for visualizer title ---
        encoding_label = scheme.upper()
        if scrambling:
            encoding_label += f" ({scrambling})"

        with open("encoding_type.txt", "w") as f:
            f.write(encoding_label)

    else:
        print("Invalid input type.")
        return

    # OUTPUT
    palindrome = find_longest_palindrome(bits)
    print(f"\nLongest Palindrome in Bitstream: {palindrome}")

    bit_duration = 1.0 / len(signal) * len(bits)
    step_points = []
    for i, (t, val) in enumerate(signal):
        t0 = i * bit_duration
        t1 = (i + 1) * bit_duration
        step_points.append((t0, val))
        step_points.append((t1, val))

    # --- Write rectangular data to file ---
    with open("signal.txt", "w") as f:
        for t, val in step_points:
            f.write(f"{t} {val}\n")

     # === Add this block BELOW ===
    choice = input("\nDo you want to decode the signal? (y/n): ").strip().lower()
    if choice == "y":
        # Load signal from file
        signal_values = []
        with open("signal.txt", "r") as f:
            for line in f:
                _, val = line.strip().split()
                signal_values.append(float(val))

        # Determine samples per bit
        samples_per_bit = len(signal_values) // len(bits)

        # Decode
        decoded_bits = line_decode(signal_values, scheme, samples_per_bit, scrambling)

        print("\n==============================")
        print(f"Decoded using: {scheme}")
        print("Decoded Bits:")
        print(decoded_bits)
        print("==============================\n")

    subprocess.run(["./visualizer"])  # launch C++ MathGL window



if __name__ == "__main__":
    while True:
        main()
        choice = input("\nDo you want to generate another signal? (y/n): ").strip().lower()
        if choice != 'y':
            print("Exiting Digital Signal Generator. bye")
            break

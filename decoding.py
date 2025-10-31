import math
# Line Decoder (Universal)
def line_decode(signal, scheme, samples_per_bit,scrambling="B8ZS"):
    
    scheme = scheme.lower()
    bits = len(signal) // samples_per_bit
    decoded_bits = []

    if scheme == "nrz-l":
        for i in range(bits):
            start = i * samples_per_bit
            end = start + samples_per_bit
            avg = sum(signal[start:end]) / samples_per_bit
            decoded_bits.append(1 if avg < 0 else 0)

    elif scheme == "nrz-i":
        bit_levels = []
        for i in range(bits):
            start = i * samples_per_bit
            end = start + samples_per_bit
            avg = sum(signal[start:end]) / samples_per_bit
            bit_levels.append(avg)

        for i in range(bits):
            if i == 0:
                decoded_bits.append(1 if bit_levels[i] < 0 else 0)
            else:
                transition = math.copysign(1, bit_levels[i]) != math.copysign(1, bit_levels[i - 1])
                decoded_bits.append(1 if transition else 0)

    elif scheme == "manchester":
        half = max(1, samples_per_bit // 2)
        for i in range(bits):
            start = i * samples_per_bit
            mid = start + half
            end = start + samples_per_bit
            avg_first = sum(signal[start:mid]) / half
            avg_second = sum(signal[mid:end]) / half
            # Manchester: 0 = High→Low, 1 = Low→High
            if avg_first > 0 and avg_second < 0:
                decoded_bits.append(0)
            else:
                decoded_bits.append(1)

    elif scheme == "differential manchester":
        half = max(1, samples_per_bit // 2)
        prev_end_level = 2.0
        for i in range(bits):
            start = i * samples_per_bit
            mid = start + half
            end = start + samples_per_bit
            avg_first = sum(signal[start:mid]) / half
            start_transition = math.copysign(1, avg_first) != math.copysign(1, prev_end_level)
            decoded_bits.append(0 if start_transition else 1)
            avg_second = sum(signal[mid:end]) / half
            prev_end_level = math.copysign(1, avg_second)
            if prev_end_level == 0.0:
                prev_end_level = 1.0

    
    elif scheme == "ami":
        levels = []
        for i in range(bits):
            start = i * samples_per_bit
            end = start + samples_per_bit
            avg = sum(signal[start:end]) / samples_per_bit
            if avg > 0.2:
                levels.append(1)
            elif avg < -0.2:
                levels.append(-1)
            else:
                levels.append(0)

        if scrambling:
            # Decode B8ZS or HDB3
            bits_out = []
            i = 0
            prev_polarity = -1
            scr = scrambling.upper()

            while i < len(levels):
                level = levels[i]

                # --- B8ZS decoding ---
                if scr == "B8ZS" and i + 7 < len(levels):
                    pattern = levels[i:i+8]
                    pattern_pos = [0, 0, 0, +1, -1, 0, -1, +1]
                    pattern_neg = [0, 0, 0, -1, +1, 0, +1, -1]
                    if pattern == pattern_pos or pattern == pattern_neg:
                        bits_out.extend([0] * 8)
                        i += 8
                        for val in reversed(pattern):
                            if val != 0:
                                prev_polarity = val
                                break
                        continue

                if scr == "HDB3" and i + 3 < len(levels):
                    pat = levels[i:i+4]

                    
                    if pat[:3] == [0, 0, 0] and pat[3] != 0 and pat[3] == prev_polarity:
                        bits_out.extend([0, 0, 0, 0])
                        prev_polarity = pat[3]       
                        pulses_since_last_sub = 0
                        i += 4
                        continue

                   
                   
                    if pat[0] != 0 and pat[1:3] == [0, 0] and pat[3] != 0:
                        expected_B = -prev_polarity
                        if pat[0] == expected_B and pat[3] == expected_B:
                            bits_out.extend([0, 0, 0, 0])
                            prev_polarity = pat[3]
                            pulses_since_last_sub = 0
                            i += 4
                            continue


                # --- Normal AMI decoding ---
                if level == 0:
                    bits_out.append(0)
                else:
                    bits_out.append(1)
                    prev_polarity = level
                i += 1

            decoded_bits = bits_out

        else:
            decoded_bits = [1 if abs(l) > 0.1 else 0 for l in levels]


    

    else:
        raise ValueError("Unsupported scheme. Choose from: NRZ-L, NRZ-I, Manchester, Differential Manchester, AMI")

    return decoded_bits

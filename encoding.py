
# Line Encoding + Scrambling
def line_encode(bits, scheme, scrambling=None):
    scheme = scheme.lower()
    signal = []
    t = 0
    last_level = 1
    ami_polarity = 1

    for b in bits:
        b = int(b)
        if scheme == 'nrz-l':
            level = -1 if b == 1 else 1
        elif scheme == 'nrz-i':
            if b == 1:
                last_level *= -1
            level = last_level
        elif scheme == 'manchester':
            # mid-bit transition

            half = 0.5
            if b == 0:
                # High → Low
                signal.append((t, 1))
                signal.append((t + half, -1))
            else:
                # Low → High
                signal.append((t, -1))
                signal.append((t + half, 1))
            t += 1
            continue  # skip the default append below

        elif scheme == 'differential manchester':
            # mid-bit transition
            # Bit 0 → transition at start
            # Bit 1 → no transition at start
            half = 0.5
            if b == 0:
                last_level *= -1  
            # First half
            signal.append((t, last_level))
            # Mid-bit transition 
            last_level *= -1
            signal.append((t + half, last_level))
            t += 1
            continue
        elif scheme == 'ami':
            if b == 1:
                level = ami_polarity
                ami_polarity *= -1
            else:
                level = 0
        else:
            raise ValueError("Invalid encoding scheme")
        signal.append((t, level))
        t += 1

    if scheme == 'ami' and scrambling:
        signal = apply_scrambling(bits, scrambling)

    return signal


def apply_scrambling(bits, scheme='B8ZS', prev_polarity=-1):

    scheme = scheme.upper() if scheme else None
    levels = []
    zero_count = 0
    pulses_since_last_sub = 0  

    for b in bits:
        if b == '1':
            # Normal AMI encoding
            prev_polarity *= -1
            levels.append(prev_polarity)
            zero_count = 0
            pulses_since_last_sub += 1
        else:
            zero_count += 1
            levels.append(0)

            # -------------------- B8ZS --------------------
            if scheme == 'B8ZS' and zero_count == 8:
                levels = levels[:-8]

                
                if prev_polarity == 1:
                    pattern = [0, 0, 0, +1, -1, 0, -1, +1]
                else:
                    pattern = [0, 0, 0, -1, +1, 0, +1, -1]

                levels.extend(pattern)

                for val in reversed(pattern):
                    if val != 0:
                        prev_polarity = val
                        break

                zero_count = 0
                pulses_since_last_sub = 0

            elif scheme == 'HDB3' and zero_count == 4:
                levels = levels[:-4]

                if pulses_since_last_sub % 2 == 0:
                    B = -prev_polarity
                    V = B
                    pattern = [B, 0, 0, V]
                else:
                    V = prev_polarity
                    pattern = [0, 0, 0, V]

                levels.extend(pattern)
                prev_polarity = pattern[-1]
                zero_count = 0
                pulses_since_last_sub = 0

    signal = []
    t = 0.0
    for level in levels:
        signal.append((t, level))
        t += 1.0

    return signal


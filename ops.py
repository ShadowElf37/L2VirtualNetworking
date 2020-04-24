def bin_to_bytes(str):
    ints = []
    for i in range(len(str)//8):
        try:
            ints.append(int(str[i*8:(i+1)*8], 2))
        except ValueError:
            raise ValueError('Malformed binary data.')
    return bytes(ints)

def ltb(list, chunk=8):
    return sum([int << chunk*(len(list)-idx) for idx, int in enumerate(list)]) >> chunk

def force_bits(i, n=8):
    if type(i) is int:
        i = bin(i)[2:]
    return ('0'*(n - len(i)) + i)[:n]

#print(force_octets(0x1000800, 2))
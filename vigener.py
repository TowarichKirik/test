def vigenere(text, key, mode='encode'):
    ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    key_repeated = (key * (len(text) // len(key) + 1))[:len(text)].lower()
    result = []

    for i, char in enumerate(text.lower()):
        if char in ru_alphabet:
            text_index = ru_alphabet.index(char)
            key_index = ru_alphabet.index(key_repeated[i])
            if mode == 'encode':
                new_index = (text_index + key_index) % len(ru_alphabet)
            elif mode == 'decode':
                new_index = (text_index - key_index) % len(ru_alphabet)
            result.append(ru_alphabet[new_index])
        else:
            result.append(char)

    return ''.join(result)

import string
import random

KEY_LEN = 12

def main():

    print key_gen()

def base_str():
    return string.letters+string.digits

def key_gen():
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)

main()
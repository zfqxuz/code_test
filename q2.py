import sys


def modify_string(s, k):
    char_list = list(s)
    char_positions = {}

    for i, char in enumerate(char_list):
        if char in char_positions and i - char_positions[char] <= k:
            char_list[i] = '-'
        # 更新最后出现的位置
        char_positions[char] = i
    return ''.join(char_list)


if __name__ == '__main__':
    s,k= sys.argv[1], int(sys.argv[2])
    print(modify_string(s,k))
class Scale:
    # scale:[0:C2,1:C#2,...,12:C3,...,24:C4,...,36:C5,...,48:C6,...,60:C7,...,72:C8]
    # root:C♮/C♯/C♭
    # key:自然大调、和声大调、旋律大调、自然小调、和声小调、旋律小调、大调五声音阶、小调五声音阶
    def __init__(self, root, key):
        self.root = root
        self.key = key
        self.scale = [0] * 73  # 0表示黑键，1表示白键
        self.major = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        self.harmonic_major = [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1]
        self.melodic_major = [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0]
        self.minor = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        self.harmonic_minor = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]
        self.melodic_minor = [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        self.pentatonic_major = [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0]
        self.pentatonic_minor = [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0]

        index = 0
        if self.root[0] == 'C':
            index = 24  # 定位在C4
        elif self.root[0] == 'D':
            index = 26
        elif self.root[0] == 'E':
            index = 28
        elif self.root[0] == 'F':
            index = 29
        elif self.root[0] == 'G':
            index = 31
        elif self.root[0] == 'A':
            index = 21
        else:
            index = 23
        if self.root[1] == '♯':
            index += 1
        elif self.root[1] == '♭':
            index -= 1
        self.root_index = index
        self.scale[index] = 1

        self.calculate(self.get_foundation_scale())

        # 初始化对应的音符名字
        self.scale_name = [''] * 73
        for i in range(2, 8):
            temp = [f'C{i}', f'C♯{i}', f'D{i}', f'D♯{i}', f'E{i}', f'F{i}', f'F♯{i}', f'G{i}', f'G♯{i}', f'A{i}',
                    f'A♯{i}', f'B{i}']
            self.scale_name[12 * (i - 2):12 * (i - 1)] = temp

    def calculate(self, key_mask):
        # 从根音开始，分别向右、向左赋值
        for i in range(self.root_index, 73, 12):
            self.scale[i:i + 12] = key_mask[0:len(self.scale[i:i + 12])]
        for i in range(self.root_index, -1, -12):
            if i - 12 < 0:
                self.scale[0:i] = key_mask[12 - len(self.scale[0:i]):12]
            else:
                self.scale[i - 12:i] = key_mask[0:12]

    def get_foundation_scale(self):
        if self.key == 'Major' or self.key == '自然大调':
            return self.major
        elif self.key == 'Harmonic Major' or self.key == '和声大调':
            return self.harmonic_major
        elif self.key == 'Melodic Major' or self.key == '旋律大调':
            return self.melodic_major
        elif self.key == 'Minor' or self.key == '自然小调':
            return self.minor
        elif self.key == 'Harmonic Minor' or self.key == '和声小调':
            return self.harmonic_minor
        elif self.key == 'Melodic Minor' or self.key == '旋律小调':
            return self.melodic_minor
        elif self.key == 'Pentatonic Major' or self.key == '大调五声音阶':
            return self.pentatonic_major
        elif self.key == 'Pentatonic Minor' or self.key == '小调五声音阶':
            return self.pentatonic_minor

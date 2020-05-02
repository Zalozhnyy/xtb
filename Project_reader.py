import locale
import os


class Particle:
    def __init__(self, dictionary):
        self.particle_dictionary = dictionary

    def append_dict(self, key, value):
        self.particle_dictionary.update({f'{key}': value})

    def dict_return(self):
        return self.particle_dictionary


class DataParcer:
    def __init__(self, path):
        self.path = path
        self.decoding_def = locale.getpreferredencoding()
        self.decoding = 'utf-8'
        self.dict_list = []

        self.decode_dictionary = {
            1: '_KOM_',
            2: '_ANN_',
            3: '_FOT_',
            4: '_BRM_',
            5: '_BRM_',
            6: '_ANN_',
            7: '_ELA_',
            8: '_EXC_',
            9: '_ROT_',
            10: '_ION_',
            11: '_ATT_',
            12: '_REC_',
        }

    def particle(self):
        a = {}
        return Particle(dictionary=a)

    def par_decoder(self):
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()

        # L[0] '<Количество типов частиц>'
        L = []
        L.append(int(lines[2].strip()))

        string_num = 6
        for num in range(L[0]):

            part = self.particle()

            string_num += 1  # <Номер, заряд(эл.), масса(г), самосогл.(0-нет,1-да) + 1 str

            if int(lines[string_num].split()[4]) == 1:
                part.append_dict(key='FBB_E_', value=[1])
            if int(lines[string_num].split()[4]) == 2:
                part.append_dict(key='FBB_P_', value=[2])

            # L.append(int(lines[string_num].split()[0]))
            string_num += 3  # <Количество процессов>
            string_num += 1  # <Количество процессов> + 2 str

            end = string_num + int(lines[string_num]) * 2
            string_num += 1  # <Номер процесса, процесс(0-нет,1-есть)
            start = string_num + 1

            for i in range(start, end + 1, 2):
                key = self.decode_dictionary.get(int(lines[i].split()[0]))
                value = list(map(int, lines[i].split()[1:]))
                part.append_dict(key=key, value=value)

            string_num = end

            self.dict_list.append(part.dict_return())
            string_num += 4  # переход к следующему кластеру (последняя строка с цифрами в процессах)

        return self.dict_list

    def lay_decoder(self):
        #### .LAY DECODER
        decoding_def = locale.getpreferredencoding()
        decoding = 'utf-8'
        path = self.path

        try:
            with open(rf'{path}', 'r', encoding=f'{decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{path}', 'r', encoding=f'{decoding_def}') as file:
                lines = file.readlines()

        try:

            line = 2  # <Количество слоев> + 1 строка
            lay_numeric = int(lines[line])
            out_lay = []
            # print(f'<Количество слоев> + 1 строка     {lines[line]}')

            line += 2  # <Номер, название слоя>
            # print(f'<Номер, название слоя>     {lines[line]}')

            for layer in range(lay_numeric):
                local = []
                line += 1  # <Номер, название слоя> + 1 строка
                # print(f'<Номер, название слоя> + 1 строка     {lines[line]}')
                local.append(lines[line].split()[0])  # 0 - номер слоя
                local.append(lines[line].split()[-1])  # 1 - название слоя

                line += 2  # <газ(0)/не газ(1), и тд + 1 строка

                extended = False
                if int(lines[line].split()[-1]) == 1:
                    extended = True

                line += 2  # <давление в слое(атм.), плотн.(г/см3), + 1 строка
                local.append(lines[line].split()[1])  # 2 - плотность

                if extended is False:
                    line += 2  # следущая частица    <Номер, название слоя>
                elif extended is True:
                    line += 2  # <молекулярный вес[г/моль] + 1 строка

                    line += 2  # следущая частица    <Номер, название слоя>
                out_lay.append(local)

            # sgs convert to si

            # for i in range(len(out_lay)):
            #     density = eval(out_lay[i][2])
            #     density *= 1000
            #     out_lay[i][2] = f'{density}'

            return out_lay

        except Exception:
            print('Ошибка в чтении файла .LAY')
            return

if __name__ == '__main__':
    # x = DataParcer(r'C:\Users\Никита\Dropbox\work_cloud\source_cont\entry_data\Wpala\ABIK_LOCAL.PAR').par_decoder()
    x = DataParcer(r'C:\work\tzp_8\KUVSH.LAY').lay_decoder()
    print(x)

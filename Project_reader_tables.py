import locale
import os
import numpy as np


def check_folder(path):
    prj_name = []
    for f in os.listdir(path):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            prj_name.append(f)
    if len(prj_name) == 0:
        return

    try:
        with open(os.path.join(path, rf'{prj_name[0]}'), 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(os.path.join(path, rf'{prj_name[0]}'), 'r',
                  encoding=locale.getpreferredencoding()) as file:
            lines = file.readlines()

    out = {}
    for i in range(len(lines)):
        if '<Grd name>' in lines[i]:
            out.setdefault('GRD', lines[i + 1].strip())
        if '<Tok name>' in lines[i]:
            out.setdefault('TOK', lines[i + 1].strip())
        if '<Layers name>' in lines[i]:
            out.setdefault('LAY', lines[i + 1].strip())
        if '<Particles-Layers name>' in lines[i]:
            out.setdefault('PL', lines[i + 1].strip())
        if '<Particles name>' in lines[i]:
            out.setdefault('PAR', lines[i + 1].strip())

    return out


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

        string_num = 4  # <Тип(0-неизвестен,1-электрон,2-позитрон,3-квант,4-протон,5-дейтрон,6-а/частица), Название>
        particle_type_dict = {}

        for num in range(L[0]):
            string_num += 1
            particle_type = int(lines[string_num].split()[0])

            string_num += 1  # <Номер, заряд(эл.), масса(г), самосогл.(0-нет,1-да), торм.(0-нет,1-эл.,2-пр.),

            part = {}

            string_num += 1  # <Номер, заряд(эл.), масса(г), самосогл.(0-нет,1-да) + 1 str

            string_num += 3  # <Количество процессов>
            string_num += 1  # <Количество процессов> + 2 str

            end = string_num + int(lines[string_num]) * 2
            string_num += 1  # <Номер процесса, процесс(0-нет,1-есть)
            start = string_num + 1

            tmp = {}
            for i in range(start, end + 1, 2):
                key = self.decode_dictionary.get(int(lines[i].split()[0]))
                value = list(map(int, lines[i].split()[1:]))
                tmp.update({key: value})

            part.update({num: tmp})
            particle_type_dict.update(({num: particle_type}))

            string_num = end

            self.dict_list.append(part)
            string_num += 2  # переход к следующему кластеру (последняя строка с цифрами в процессах)

        return self.dict_list, particle_type_dict

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
            conductivity = []
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
                conductivity.append(int(lines[line].strip().split()[1]))

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

            return out_lay, conductivity

        except Exception:
            print('Ошибка в чтении файла .LAY')
            return

    def pl_decoder(self):
        #### .PL DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines_pl = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines_pl = file.readlines()
        try:
            particle_count = int(lines_pl[2])
            layers = int(lines_pl[6])
            line = 8  # <Layer numbers>
            layers_numbers = np.array(lines_pl[line].strip().split(), dtype=int)
            line += 1  # <Движение частицы в слое (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>

            part_move = []
            for i in range(particle_count):
                line += 1
                part_move.append(lines_pl[line].strip().split())
            part_move = np.array(part_move, dtype=int)

            line += 1  # <Объемный источник (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>
            line += particle_count + 1
            line += 1  # <Частица номер>

            surface_source = {}

            for i in range(particle_count):
                line += 1
                lay_number = int(lines_pl[line].strip())

                key_list = []
                for j in range(layers):
                    line += 1
                    key_list.append(lines_pl[line].split())

                key_list = np.array(key_list, dtype=int)
                surface_source.update({lay_number: key_list})
                line += 1  # <Расчет плотности тока (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>

            line += particle_count + 1  # <Ионизационное торможение (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>

            io_brake = []
            for i in range(particle_count):
                line += 1
                io_brake.append(lines_pl[line].strip().split())
            io_brake = np.array(io_brake, dtype=int)

            line += 1  # <Источник ионизации (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>

            return part_move, io_brake, layers_numbers

        except Exception:
            print('Ошибка в чтении файла .PL')
            return


if __name__ == '__main__':
    x, y = DataParcer(r'C:\Work\Test_projects\wpala\shpala_new.PAR').par_decoder()
    # x = DataParcer(r'C:\Work\Test_projects\wpala\shpala_new.PL').pl_decoder()
    print(x)
    print(y)

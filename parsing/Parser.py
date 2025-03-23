import pandas as pd
import datetime
import re
import psycopg
import os

class Parser:
    def __init__(self, path):
        self.df = pd.read_excel(path)
        while len(self.df.columns) != 7:
            self.df = self.df.drop(columns=self.df.columns[-1])
        self.df.columns = ["id", "resource", "day", "area", "house_counts", "address", "start"]
        self.df = self.df.dropna()
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.drop(index=0)
        self.df = self.df.set_index('id').reset_index(drop=True)
        self.db_ip = '192.168.114.242'
        self.db_port = 5432
        self.db_user = 'postgres'
        self.db_name = 'public_service'
        self.db_passwd = 'root7654123'

    def parse_resource(self, resource):
        resource_type = None
        resource_org = None
        resource_phone = None
        if len(resource) > 0:
            resource_type = resource.pop(0)
        if len(resource) > 0:
            resource_org = resource.pop(0)
        if len(resource) > 0:
            resource_phone = resource.pop(0)
        return resource_type, resource_org, resource_phone

    def parse_addresses(self, district, input_str):
        """
        Функция принимает:
        district – строку с названием района;
        input_str – строку с адресами домов в человекочитаемом виде.
        Возвращает JSON-строку, содержащую список адресов, где каждая запись имеет вид:
        { "Район": <district>, "улица": <street>, "дом": <дом> }

        Особенности:
          - Если после названия улицы (которое может состоять из нескольких слов) не указаны номера домов,
            в поле "дом" проставляется строка "all".
          - Если номер дома задан диапазоном вида "3-5" (и обе части – целые числа), диапазон разворачивается
            в последовательность номеров.
          - Если сегмент содержит слова, указывающие на прочие работы (например, "плановое", "аварийное", "подвоз"),
            такой сегмент пропускается.

        Алгоритм:
          1. Разбивает входную строку на сегменты по символу ";" или переводу строки.
          2. Для каждого сегмента пытается выделить название улицы и номера домов.
             Для этого применяется регулярное выражение, которое ищет название улицы (одно или несколько слов)
             и, опционально, номера домов (начинающиеся с цифры). Если номера не обнаружены – будем считать, что адрес
             задан как вся улица ("all").
          3. Если после первого токена (который может содержать и название улицы, и первый номер)
             имеются ещё токены (разделённые запятыми), они считаются дополнительными номерами домов.
          4. Каждый отдельный номер (а также развернутые диапазоны) записываются в итоговый список.
        """
        addresses = []
        if "аварийное" in input_str.lower():
            reason = "Аварийное"
            comment = input_str[input_str.lower().find("аварийное"):input_str.lower().find("подвоз")]
        elif "плановое" in input_str.lower():
            reason = "Плановое"
            comment = input_str[input_str.lower().find("плановое"):input_str.lower().find("подвоз")]
        else:
            reason = ''
            comment = ''
        water_id = input_str.lower().find("подвоз")
        if water_id != -1:
            water_delivery = input_str[water_id:]
        else:
            water_delivery = ''
        # Разбиваем входную строку по символу ";" или переводу строки.
        segments = re.split(r";\s*", input_str)
        # Ключевые слова для пропуска сегментов, не являющихся адресами
        skip_keywords = ("плановое", "аварийное", "подвоз")
        # Регулярное выражение для выделения названия улицы и, опционально, первого номера дома.
        # Оно ищет название улицы (все символы до первого пробела, за которым следует цифра) – если таковая имеется,
        # а если нет – берется вся строка как название.
        street_pattern = re.compile(r"^(?P<street>.+?)(?=\s+\d|$)(?:\s+(?P<house>[\d].*))?$")

        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            if seg.lower().startswith(skip_keywords):
                continue

            # Разбиваем сегмент по запятым
            tokens = [token.strip() for token in seg.split(",") if token.strip()]
            if not tokens:
                continue

            # Из первого токена пытаемся выделить название улицы и (опционально) первый номер дома.
            m = street_pattern.match(tokens[0])
            if m:
                street = m.group("street").strip()
                first_house = m.group("house").strip() if m.group("house") else None
            else:
                # Если не удалось – считаем, что весь токен – название улицы
                street = tokens[0]
                first_house = None

            house_list = []
            if first_house:
                house_list.append(first_house)
            # Если после первого токена есть дополнительные, они считаются номерами домов.
            if len(tokens) > 1:
                for token in tokens[1:]:
                    if token:
                        house_list.append(token)
            # Если номеров домов не найдено, добавить запись с домом "all"
            if not house_list:
                addresses.append({"district": district, "street": street, "house": "all"})
            else:
                # Обрабатываем каждый номер: если он задан диапазоном вида "3-5" (и оба числа целые),
                # разворачиваем его в последовательность.
                for item in house_list:
                    m_range = re.match(r"^(\d+)-(\d+)$", item)
                    if m_range:
                        start = int(m_range.group(1))
                        end = int(m_range.group(2))
                        for num in range(start, end + 1):
                            addresses.append({"district": district, "street": street, "house": str(num)})
                    else:
                        addresses.append({"district": district, "street": street, "house": item.split()[0]})

        return addresses, reason, comment, water_delivery

    def parse_time(self, time_):
        try:
            months = {'января': 1,
                       'февраля': 2,
                       'марта': 3,
                       'апреля': 4,
                       'мая': 5,
                       'июня': 6,
                       'июля': 7,
                       'августа': 8,
                       'сентября': 9,
                       'октября': 10,
                       'ноября': 11,
                       'декабря': 12}
            start, stop = time_.split('\n')
            start = start.split()
            start_time_h = int(start[2].split('-')[0])
            start_time_m = int(start[2].split('-')[1])
            start_time = datetime.datetime(year=datetime.datetime.now().year,
                                           month=months[start[1]],
                                           day=int(start[0]),
                                           hour=start_time_h,
                                           minute=start_time_m)

            stop = stop.split()
            stop_time_h = int(stop[2].split('-')[0])
            stop_time_m = int(stop[2].split('-')[1])
            stop_time = datetime.datetime(year=datetime.datetime.now().year,
                                          month=months[stop[1]],
                                          day=int(stop[0]),
                                          hour=stop_time_h,
                                          minute=stop_time_m)
            return True, start_time, stop_time
        except:
            return False, None, None

    def parse(self):
        con = psycopg.connect(host=self.db_ip,
                              user=self.db_user,
                              password=self.db_passwd,
                              port=self.db_port,
                              dbname=self.db_name)
        cur = con.cursor()
        for i in range(len(self.df)):
            resource = self.df.loc[i, "resource"].split('\n')
            resource_type, resource_org, resource_phone = self.parse_resource(resource)
            area = self.df.loc[i, "area"]
            address = self.df.loc[i, "address"]
            addresses, reason, comment, water_delivery = self.parse_addresses(area, address)
            start = self.df.loc[i, 'start']
            status, start_time, stop_time = self.parse_time(start)
            query = "INSERT INTO aborts (type, reason, organization, phone_number, comment, water_delivery, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (resource_type, reason, resource_org, resource_phone, comment, water_delivery, start_time, stop_time))
            con.commit()
            query = "SELECT id FROM aborts ORDER BY id DESC fetch first 1 rows only"
            cur.execute(query)
            abort_id = cur.fetchone()[0]
            for address in addresses:
                query = ("INSERT INTO addresses (district, street, house) " 
                         "SELECT %s, %s, %s "
                         "WHERE NOT EXISTS("
                         "SELECT id FROM addresses WHERE district=%s AND street=%s AND house=%s)")
                cur.execute(query, (address['district'], address['street'], address['house'], address['district'], address['street'], address['house']))
                con.commit()
                query = ("SELECT id "
                         "FROM addresses "
                         "WHERE district=%s AND street=%s AND house=%s")
                cur.execute(query, (address['district'], address['street'], address['house']))
                address_id = cur.fetchone()[0]
                query = "INSERT INTO aborts_addresses (abort_id, address_id) VALUES (%s, %s)"
                cur.execute(query, (abort_id, address_id))
                con.commit()
        con.close()

if __name__ == "__main__":
    for path in os.listdir('dataset'):
        parser_ = Parser(f"dataset/{path}")
        parser_.parse()



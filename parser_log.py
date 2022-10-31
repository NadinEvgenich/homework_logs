import argparse
import re
import json
from collections import Counter, deque

parser = argparse.ArgumentParser(description='Process access.log')
parser.add_argument('-f', dest='file', action='store', required=True, help='Path to logfile')
args = parser.parse_args()


def reader(filename):
    reg_ip = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    reg_method = r'(POST|GET|PUT|DELETE|HEAD|OPTIONS)\b'
    reg_time = r'\d\d\d*$'
    reg_date = r'\[[\w\s/:+-]*\]'
    reg_url = r'\"https?://(\S*)\"'

    with open(filename) as file:
        requests = 0  # Счетчик запросов
        ip_list = []  # Список всех IP адресов
        method_list = []  # Список всех методов
        biggest_time = deque(['1'], maxlen=3)  # Список с наибольшим временем запроса
        biggest_request = deque(maxlen=3)  # Список запросов с наибольшим временем
        for line in file:
            requests += 1  # Подсчет количества строк
            try:
                ip = re.findall(reg_ip, line)
                ip_list.append(ip[0])  # Добавление адреса ip в список
            except IndexError:
                pass
            try:
                method = re.findall(reg_method, line)
                method_list.append(method[0])  # Добавление метода в список
            except IndexError:
                pass
            # Пополнение списка топ 3 самых долгих запросов
            time = re.findall(reg_time, line)
            int_time = int(time[0])
            for i in biggest_time:
                int_i = int(i[0])
                if int_time > int_i:
                    biggest_request.appendleft(line)
                    biggest_time.appendleft(time)
                    break

    top3ip = Counter(ip_list).most_common(3)  # Топ 3 ip адресов
    method_count = Counter(method_list)  # Словарь с количеством использования всех методов

    biggest_request_list = []
    for line in biggest_request:
        method = re.search(reg_method, line).group(0)
        host = re.search(reg_ip, line).group(0)
        request_duration = re.search(reg_time, line).group(0).replace('\n', '')
        date = re.search(reg_date, line).group(0)
        is_url = re.search(reg_url, line)
        url = is_url.group(0)[1:-1] if is_url else '-'
        request_info = {
            'ip': host,
            'date': date,
            'method': method,
            'url': url,
            'duration': int(request_duration),
        }
        biggest_request_list.append(request_info)

    json_file = {
        "top_ips": top3ip,
        "top_longest": biggest_request_list,
        "total_stat": [
            {
                "GET": method_count["GET"],
                "POST": method_count["POST"],
                "PUT": method_count["PUT"],
                "DELETE": method_count["DELETE"],
                "HEAD": method_count["HEAD"]
            }
        ],
        "total_requests": requests
    }
    print(json.dumps(json_file, indent=4))

    with open("result.json", "w", encoding="utf-8") as file:
        json_schema = json.dumps(json_file, indent=4)
        file.write(json_schema)


if __name__ == '__main__':
    reader(args.file)

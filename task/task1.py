#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
from datetime import datetime
import json
import jsonschema
from jsonschema import validate


def main():
    trains = []
    while True:
        command = get_command()
        if command == 'exit':
            break
        elif command == 'add':
            trains.append(add())
            if len(trains) > 1:
                trains.sort(key=lambda item: item.get('destination', ''))
        elif command == 'list':
            print_list(trains)
        elif command.startswith('select '):
            select(command, trains)
        elif command.startswith("save "):
            parts = command.split(maxsplit=1)
            file_name = parts[1]
            save_workers(file_name, trains)

        elif command.startswith("load "):
            parts = command.split(maxsplit=1)
            file_name = parts[1]
            trains = load_workers(file_name)
        elif command == 'help':
            print_help()
        else:
            print(f"Неизвестная команда {command}", file=sys.stderr)


def get_command():
    return input(">>> ").lower()


def add():
    destination = input("Название пункта назначения? ")
    number = int(input("Номер поезда? "))
    time = input("Время отправления ЧЧ:ММ? ")
    time = datetime.strptime(time, '%H:%M')
    train = {
        'destination': destination,
        'number': number,
        'time': time,
    }
    return train


def print_list(trains):
    line = '+-{}-+-{}-+-{}-+-{}-+'.format(
        '-' * 4,
        '-' * 28,
        '-' * 14,
        '-' * 19
    )
    print(line)
    print(
        '| {:^4} | {:^28} | {:^14} | {:^19} |'.format(
            "No",
            "Название пункта назначения",
            "Номер поезда",
            "Время отправления"
        )
    )
    print(line)
    for idx, train in enumerate(trains, 1):
        print(
            '| {:>4} | {:<28} | {:<14} | {:>19} |'.format(
                idx,
                train.get('destination', ''),
                train.get('number', ''),
                train.get('time', 0).strftime("%H:%M")
            )
        )
    print(line)


def print_help():
    print("Список команд:\n")
    print("add - добавить отправление;")
    print("list - вывести список отправлений;")
    print("select <ЧЧ:ММ> - вывод на экран информации о "
          "поездах, отправляющихся после этого времени;")
    print("save <имя файла.json> - сохранить в файл")
    print("load <имя файла.json> - загрузить из файла")
    print("help - отобразить справку;")
    print("exit - завершить работу с программой.")


def select(command, trains):
    count = 0
    parts = command.split(' ', maxsplit=1)
    time = datetime.strptime(parts[1], '%H:%M')
    for train in trains:
        if train.get("time") > time:
            count += 1
            print(
                '{:>4}: {} {}'.format(
                    count,
                    train.get('destination', ''),
                    train.get("number")
                )
            )
    if count == 0:
        print("Отправлений позже этого времени нет.")


def save_workers(file_name, staff):
    if file_name.split('.', maxsplit=1)[-1] != "json":
        print("Несоответствующий формат файла", file=sys.stderr)
        return False
    try:
        list_of_files = os.listdir(os.path.split(os.getcwd())[0])
        index = list_of_files.index('.gitignore')
        flag = True
    except ValueError:
        flag = False
        print("Файл .gitignore не найден", file=sys.stderr)

    if flag:
        file = f"{os.path.split(os.getcwd())[0]}/.gitignore"
        with open(file, 'a', encoding="utf-8") as git_file:
            git_file.write(f"{file_name}\n")

    for i in staff:
        i['time'] = i['time'].time().strftime("%H:%M")
    with open(file_name, "w", encoding="utf-8") as fout:
        json.dump(staff, fout, ensure_ascii=False, indent=4)
    return True


def validate_json(json_data):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "number": {"type": "number"},
                "time": {"type": "string"},
            }
        },
    }

    try:
        validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


def load_workers(file_name):
    if file_name.split('.', maxsplit=1)[-1] != "json":
        print("Несоответствующий формат файла", file=sys.stderr)
        return []

    if not os.path.exists(f"{os.getcwd()}/{file_name}"):
        print("Файл не существует", file=sys.stderr)
        return []

    with open(file_name, "r", encoding="utf-8") as fin:
        data = []
        try:
            data = json.load(fin)
            flag = validate_json(data)
        except Exception as e:
            print("Некоректный файл", file=sys.stderr)
            flag = False
        if flag:
            for i in data:
                i['time'] = datetime.strptime(i['time'], '%H:%M')
            return data
        else:
            return []


if __name__ == '__main__':
    main()

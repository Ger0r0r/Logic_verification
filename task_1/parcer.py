import matplotlib.pyplot as plt
import json
import re
import sys

json_name = sys.argv[1]
tests_inputs = sys.argv[2]

# json_name = "task_example.json"
# tests_inputs = "test_new.txt"

f = open(json_name, "r")
data = json.load(f)

operators = data["gates"]
num_input = data["schematics"]["inw"]
num_output = data["schematics"]["outw"]
raw_nodes = data["schematics"]["gates"]
raw_links = data["schematics"]["drivers"]
out_nodes = data["schematics"]["output"]

node = {
	"name" : "",
	"type" : "",
	# 0 - not visited, 1 - visited, 2 - done, 3 - undefined
	"status" : 3,
	"num_in" : 0,
	"num_out" : 0,
	"table" : "z",
	"in" : "z",
	"out" : "z",
    "name_in" : "z"
}

nodes = []

for i in range(len(raw_nodes)):
    temp = node.copy()
    n_name = list(raw_nodes.keys())[i]
    n_type = raw_nodes[n_name]
    temp["name"] = n_name
    temp["type"] = n_type
    n_in = operators[n_type]["inw"]
    n_out = operators[n_type]["outw"]
    n_table = operators[n_type]["table"]
    temp["num_in"] = n_in
    temp["num_out"] = n_out
    temp["table"] = n_table
    temp["in"] = ["z"] * n_in
    temp["out"] = ["z"] * n_out
    temp["name_in"] = ["z"] * n_in

    nodes.append(temp)

def get_name_number (raw_name):
    # print(raw_name)
    name = ''
    number = ''

    for char in raw_name:
        if char.isalpha():
            name += char
        elif char.isdigit():
            number += char

    # print(raw_name, name, number)
    return name, number

# print(raw_links)

for i in range(len(nodes)):
    for target, source in list(raw_links.items()):
        t_name, t_num = get_name_number(target)
        # print(t_name, nodes[i]["name"])
        if (t_name == nodes[i]["name"]):
            # print("FIND "+t_name)
            # print(nodes[i]["name_in"])
            # print(t_num, type(t_num))
            nodes[i]["name_in"][int(t_num)] = source
            # print()
            del raw_links[target]
    # print(raw_links)

# print(raw_links)
# print(nodes)

# Функция для вычисления выходов схемы
def calculate_outputs(data, inputs, outputs):
    # Все ноды теперь надо занулить -- существуют, но не посещены
    for i in data:
        i["status"] = 0

    # Список текущих задач с установленным порядком
    degree = 0
    task = []
    for i in list(outputs):
        # print(type(i),i)
        if (isinstance(i, str)):
            single_task, trash = get_name_number(i)
            task.append(single_task)

    # print(task)

    def find_by_raw_name (raw_name, data):
        name, trash = get_name_number(raw_name)
        return find_by_name(name, data)

    def find_by_name(name, data):
        for index, item in enumerate(data):
            if item['name'] == name:
                return item, index
        return None, -1

    def find_last_unvisited (task, data):
        for i in range(len(task)):
            name, trash = get_name_number(task[-1-i])
            gate_by_name, trash = find_by_name(name, data)
            if (gate_by_name["status"] == 0):
                return len(task) - 1 - i

    def try_work(task_input, data, init_input):
        gate_in = ['z']*len(task_input)
        res = 1
        for i in range(len(task_input)):
            if isinstance(task_input[i], str):
                name, number = get_name_number(task_input[i])
                gate, gate_i = find_by_name(name, data)
                state = gate["status"]
                if (state == 2):
                    # print("FUUUCK")
                    # print(gate)
                    # print(gate["out"])
                    # print(gate["out"][int(number)])
                    gate_in[i] = gate["out"][int(number)]
                    # print("TRY_WORK STATE 2",gate_in)
                else:
                    res = 0
            else:
                gate_in[i] = init_input[task_input[i]]
                # print("TRY_WORK ELSE",gate_in)

        # print("TRY_WORK",gate_in)
        return res, gate_in

    def add_new_tasks (task_input, task, data):
        res = 0
        for i in range(len(task_input)):
            if isinstance(task_input[i], str):
                name, number = get_name_number(task_input[i])
                gate, gate_i = find_by_name(name, data)
                if (name not in task) and (gate["status"] == 0):
                    # print("add task",name)
                    task.append(name)
                    # print(task)
                    res = 1
        return res, task

    def set_out(gate):

        def number_like_list(number, total_digits):
            bin_number = bin(number)[2:]
            return list(str(bin_number).zfill(total_digits))

        # print(gate)
        num_of_in = gate["num_in"]
        num_of_out = gate["num_out"]
        # print("NUM INS",num_of_in)
        # print("NUM OUTS",num_of_out)

        table_i = 0

        for i in range(num_of_in):
            # print(gate["in"])
            # print(gate["in"][i])
            # print(int(gate["in"][i]))
            table_i += int(gate["in"][i]) * pow(2, i)


        temp_res = gate["table"][table_i]
        # print("RES OF TABLE", temp_res)
        gate["out"] = number_like_list(temp_res, num_of_out)

        return gate


    def do_task (task, i, data, init_input):
        gate, gate_i = find_by_name(task[i], data)
        gate["status"] = 1

        gate_inputs = gate["name_in"]
        is_done, new_gate_in = try_work(gate_inputs, data, init_input)
        if (is_done):
            gate["status"] = 2
            gate["in"] = new_gate_in

            gate = set_out(gate)

            task.pop(i)
            new_i = len(task) - 1

        else:
            is_added, task = add_new_tasks(gate_inputs, task, data)
            # print(task)
            if (is_added):
                new_i = len(task) - 1
            else:
                new_i = i - 1

        return task, new_i

    # 1) смотрим на последнюю задачу: если она не посещена, то отмечаем как посещённую
    # 2) если можем выполнить, то выполняем, отмечая это (повторить)
    # 3) если нельзя выполнить из-за отсутствия задач, то добавляем задачи (повторить)
    # 4) если нельзя выполнить из-за неготовности задач, то увеличиваем степень и возвращаемся на предыдущую задачу (повторить, но в 1 пункте смотрим на предпоследнюю задачу)
    current_task = len(task) - 1
    while (len(task)):
        task, current_task = do_task(task, current_task, data, inputs)

    def take_result(outputs, data, inputs):
        result = [" "] * len(outputs)
        for i in range(len(outputs)):
            # print(outputs[i])
            if isinstance(outputs[i], str):
                name, number = get_name_number(outputs[i])
                gate, gate_i = find_by_name(name, data)
                result[i] = gate["out"][int(number)]
            else:
                result[i] = inputs[int(number)]
        return result

    # print("!!!RESULTS!!!")
    result = take_result(outputs, data, inputs)
    return result


def reverse_pins(pins):
    return ''.join(reversed(pins))

with open(tests_inputs, 'r') as file:
    lines = file.readlines()  # Получаем список строк
    for line in lines:
        # print(line)
        # print(int(line, 16))
        # print(bin(int(line, 16)))
        # print(bin(int(line, 16))[2:])
        # print(bin(int(line, 16))[2:].zfill(num_input))

        test = bin(int(line, 0))[2:].zfill(num_input)
        # test = line.strip()
        # print(test, type(test))
        # for i in test:
        #     print(i)
        # print(type(test))

        test = reverse_pins(test)
        outputs = calculate_outputs(nodes, test, out_nodes)
        outputs = ''.join(map(str, outputs))
        outputs = reverse_pins(outputs)
        outputs = int(outputs, 2)
        print(f"0x{outputs}")

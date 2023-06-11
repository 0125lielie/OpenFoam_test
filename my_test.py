import argparse
import json
import random
import subprocess
import os
import numpy as np

def run_simulation(data, endTime, reynolds_number, inlet_velocity, nu):
    # 更新参数值
    data['flow_properties']['reynolds_stresses'][0] = reynolds_number
    data['flow_properties']['inlet_velocity'] = inlet_velocity
    data['flow_properties']['nu'] = nu

    # 为文件名创建一个有效的 inlet_velocity 字符串表示
    inlet_velocity_str = '_'.join([str(x) for x in inlet_velocity])

    data['file_properties']['case_name'] = f"NACA_0012_kw_SST_y+_1_Re_{reynolds_number}_endTime_{endTime}_inlet_velocity_{inlet_velocity_str}_nu_{nu}"

    # 覆写原始 JSON 文件
    with open('./examplessettingsairfoil.json', 'w') as f:
        # 写入修改的参数
        json.dump(data, f, indent=4)

    # 使用修改后的 JSON 文件运行 OpenFOAMCaseGenerator.py
    subprocess.run(["python3", "OpenFOAMCaseGenerator.py", "--input=./examplessettingsairfoil.json"])

    # 运行每个生成的案例的 OpenFOAM
    case_directory = data['file_properties']['case_name']
    allrun_file_path = "./" + os.path.join(case_directory, "Allrun")
    subprocess.run(["chmod", "+x", allrun_file_path])
    with open(
            f"./output_Re_{reynolds_number}_endTime_{endTime}_inlet_velocity_{inlet_velocity_str}_nu_{nu}.txt",
            'a') as output_file:
        subprocess.run(allrun_file_path, shell=True, stdout=output_file)
        # 在每次运行后在输出文件中添加分隔线
        output_file.write(
            "\n" + "*" * 40 + f"\n这是 endTime: {endTime}, reynolds_number: {reynolds_number}, inlet_velocity: {inlet_velocity}, nu: {nu} 的运行结束\n" + "*" * 40 + "\n")

    # 运行后清理案例目录
    subprocess.run(["rm", "-rf", case_directory])


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_type', choices=['endTime', 'parallel'], required=True)
    args = parser.parse_args()

    # 读取原始 JSON 文件
    with open('./examplessettingsairfoil.json', 'r') as f:
        data = json.load(f)

    # 当命令行参数输入是'endTime'
    if args.test_type == 'endTime':
        # 修改 'endTime' 值和 'case_name'
        for endTime in [0.05, 0.1, 0.15]:  # 在这里指定想要的 endTime
            for _ in range(10):  # 变异的测试用例数量
                reynolds_number = random.uniform(1, 2)  # reynolds_number变异范围
                inlet_velocity = list(np.random.uniform(1, 2, size=3))  # inlet_velocity变异范围
                nu = random.uniform(1e-07, 1e-05)  # nu变异范围
                run_simulation(data, endTime, reynolds_number, inlet_velocity, nu)
    # 当命令行参数输入是'parallel'
    elif args.test_type == 'parallel':
        # 修改 'number_of_processors' 值和 'case_name'
        for num_processors in range(1, 3):# 在这里指定想要的 num_processors
            data['parallel_properties']['number_of_processors'] = num_processors
            for _ in range(10):  # 变异的测试用例数量
                reynolds_number = random.uniform(1, 2)
                inlet_velocity = list(np.random.uniform(1, 2, size=3))
                nu = random.uniform(1e-07, 1e-05)
                run_simulation(data, num_processors, reynolds_number, inlet_velocity, nu)

if __name__ == "__main__":
    main()
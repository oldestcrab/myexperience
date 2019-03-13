# -*- coding:utf-8 -*-
import os
import shutil

def rename(old_path, name=1):
    """
    对文件夹内文件统一命名
    :params old_path: 文件夹绝对路径
    :params name: 命名规则
    """
    # 遍历文件夹
    for file in os.listdir(old_path):
        # 获取文件绝对路径
        old_file_path = os.path.join(old_path, file)
        # print(old_file_path)
        # 判断是否文件夹，是则跳过
        if os.path.isdir(old_file_path):
            continue
        # 获取文件名
        filename = os.path.splitext(file)[0]
        # 获取文件后缀名
        filetype = os.path.splitext(file)[1]
        # 文件路径+新名字
        new_file_path = os.path.join(old_path, str(name)+filetype)
        # 重命名
        try:
            os.rename(old_file_path, new_file_path)
        except:
            print('文件已存在', old_file_path)
        # 自增1
        name += 1
    
def move(old_path, step=30, name=1):
    """
    对文件夹内文件统一移动
    :params old_path: 文件夹绝对路径
    :params step: 步长
    :params name: 新目录命名规则
    """
    # 获取目录下所有文件
    file_list = os.listdir(old_path)
    # 对文件进行排序
    file_list.sort()
    # print(file_list)
    # 确定每个文件夹放多少文件
    for count in range(0, len(file_list)-1, step):
        stop = min(count+step,len(file_list)-1)
        # 移动step个文件
        for i in range(count, stop):
            # 原本的文件绝对路径
            old_file_path = os.path.join(old_path, str(i+1)+'.gif')
            # 文件新路径
            new_path = os.path.join(old_path, str(name))
            # 如果目录不存在，则创建
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            # 判断是否文件夹，是则跳过
            if os.path.isdir(old_file_path):
                continue
            # 移动文件
            try:
                shutil.move(old_file_path, new_path)
            except:
                pass
        # 自增1
        name += 1


if __name__ == '__main__':
    # 文件夹路径
    old_path = r'C:/GIF'
    rename(old_path)
    move(old_path)
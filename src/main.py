# 界面采用python tkinter  
# 配置文件，config.json  
# 界面上左侧有一个可以选择的List，读取配置文件中games中的name，显示在List中。单选。
# 默认选择第一个
# 界面上右侧要有两个label，分别显示两个模拟器的存档路径，分两行。
# 下面有3个按钮，分别是：
# 1、同步yuzu到ryujinx   
# 2、同步ryujinx到yuzu  
# 3、自动同步，即通过监控两个模拟器的存档路径，如果有更新，就自动同步到另一个模拟器的存档路径下。  
# 同步的时候，要有二次确认，防止误操作。另外，在同步之前，要做备份，备份的文件名为：存档名+时间戳，这样可以防止误操作。
# 存档是一个目录，里面有很多文件，所以判断最后修改时间的时候要遍历目录中所有的文件，并用最后的修改时间做最后修改时间。
# 备份的时候要将整个目录备份。

import json
import os
import shutil
import time
from tkinter import *
from tkinter import messagebox
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# 读取配置文件
with open("config.json", "r") as f:
    config = json.load(f)

# 获取游戏列表
games = config["games"]

# 备份存档
def backup_save(save_path):
    backup_path = save_path + "_" + str(int(time.time()))
    shutil.copytree(save_path, backup_path)
    return backup_path

# 同步存档
def sync_save(src_path, dst_path):
    # 备份源和目标存档
    backup_src = backup_save(src_path)
    backup_dst = backup_save(dst_path)

    # 删除目标存档并将源存档复制到目标路径
    shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path)

    messagebox.showinfo("同步成功", f"已从 {src_path} 同步到 {dst_path}\n备份源存档：{backup_src}\n备份目标存档：{backup_dst}")

# 确认同步操作
def confirm_sync(src_path, dst_path):
    if messagebox.askyesno("确认同步", f"确定要从 {src_path} 同步到 {dst_path} 吗？"):
        sync_save(src_path, dst_path)
    else:
        messagebox.showinfo("同步取消", "同步操作已取消")


# 选择游戏事件处理
def on_game_select(event):
    selected_game = games[listbox.curselection()[0]]
    yuzu_path_var.set(selected_game["yuzu_save_path"])
    ryujinx_path_var.set(selected_game["ryujinx_save_path"])

# 监控文件夹变化并自动同步
class AutoSyncHandler(FileSystemEventHandler):
    def __init__(self, sync_paths):
        self.sync_paths = sync_paths

    def on_modified(self, event):
        for src_path, dst_path in self.sync_paths:
            if event.src_path.startswith(src_path):
                sync_save(src_path, dst_path)

# 获取文件夹最后修改时间
def get_last_modified_time(dir_path):
    return max(os.path.getmtime(os.path.join(dir_path, file)) for file in os.listdir(dir_path))

# 开启自动同步
def start_auto_sync():
    for game in games:
        yuzu_time = get_last_modified_time(game["yuzu_save_path"])
        ryujinx_time = get_last_modified_time(game["ryujinx_save_path"])
        if yuzu_time > ryujinx_time:
            sync_save(game["yuzu_save_path"], game["ryujinx_save_path"])
        elif ryujinx_time > yuzu_time:
            sync_save(game["ryujinx_save_path"], game["yuzu_save_path"])

# 创建界面
root = Tk()
root.title("存档同步工具")

# 创建游戏列表
listbox = Listbox(root, selectmode=SINGLE)
for game in games:
    listbox.insert(END, game["name"])
listbox.bind("<<ListboxSelect>>", on_game_select)
listbox.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
listbox.selection_set(0)

# 创建存档路径标签
yuzu_path_var = StringVar()
ryujinx_path_var = StringVar()
yuzu_path_label = Label(root, textvariable=yuzu_path_var)
ryujinx_path_label = Label(root, textvariable=ryujinx_path_var)
yuzu_path_label.grid(row=0, column=1, padx=10, pady=10, sticky=W)
ryujinx_path_label.grid(row=1, column=1, padx=10, pady=10, sticky=W)

# 创建同步按钮
sync_yuzu_to_ryujinx_button = Button(root, text="同步yuzu到ryujinx", command=lambda: confirm_sync(yuzu_path_var.get(), ryujinx_path_var.get()))
sync_ryujinx_to_yuzu_button = Button(root, text="同步ryujinx到yuzu", command=lambda: confirm_sync(ryujinx_path_var.get(), yuzu_path_var.get()))
sync_yuzu_to_ryujinx_button.grid(row=2, column=1, padx=10, pady=10)
sync_ryujinx_to_yuzu_button.grid(row=3, column=1, padx=10, pady=10)

# 创建自动同步按钮
auto_sync_button = Button(root, text="自动同步", command=start_auto_sync)
auto_sync_button.grid(row=4, column=1, padx=10, pady=10)

# 初始化存档路径
on_game_select(None)

# 运行界面
root.mainloop()

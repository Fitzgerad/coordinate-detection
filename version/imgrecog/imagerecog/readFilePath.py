from tkinter import filedialog, Tk
import os

READ_FILE = 0
SAVE_FILE = 1

def getHint(mood):
    if mood == READ_FILE:
        title = "选择图片所在文件夹"
    elif mood == SAVE_FILE:
        title = "选择结果保存路径"
    else:
        title = None
    return title

def getFilePath(mood=READ_FILE):
    # 设置文件对话框会显示的文件类型
    my_filetypes = [('all files', '.*'), ('text files', '.txt')]

    title = getHint(mood)
    root = Tk()
    root.wm_withdraw()
    file_path = filedialog.askdirectory(initialdir=os.getcwd(),
                                        title=title)
    root.destroy()
    root.mainloop()
    return file_path
import os
import sys
import zipfile
import shutil
from tkinter import filedialog, Tk
from win32com import client as wc

READ_FILE = 0
SAVE_FILE = 1

def getHint(mood):
    if mood == READ_FILE:
        title = "选择文档所在文件夹"
    elif mood == SAVE_FILE:
        title = "选择结果保存路径"
    else:
        title = None
    return title

def getFilePath(mood=READ_FILE):
    title = getHint(mood)
    root = Tk()
    root.wm_withdraw()
    file_path = filedialog.askdirectory(initialdir=os.getcwd(),
                                        title=title)
    root.destroy()
    root.mainloop()
    return file_path

def getFiles(r_dir, s_dir):
    files = os.listdir(r_dir)
    if os.path.exists(s_dir):
        shutil.rmtree(s_dir)
    os.makedirs(s_dir)
    for file in files:
        full_path = os.path.join(r_dir, file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if not os.path.isdir(full_path):
            name = os.path.splitext(file)[0]
            suffix = os.path.splitext(file)[-1]
            if suffix == '.doc' and name[0] != '~':
                os.makedirs(temp_dir, exist_ok=True)
                doc2zip(r_dir, name)
                if hasPic():
                    shutil.copyfile(os.path.join(r_dir, file),
                                    os.path.join(s_dir, file))
            elif suffix == '.docx':
                os.makedirs(temp_dir, exist_ok=True)
                shutil.copyfile(os.path.join(r_dir, file),
                                os.path.join(temp_dir, temp_zip))
                if hasPic():
                    shutil.copyfile(os.path.join(r_dir, file),
                                    os.path.join(s_dir, file))
            elif suffix in ['.jpg', '.png']:
                shutil.copyfile(os.path.join(r_dir, file),
                                os.path.join(s_dir, file))
        else:
            getFiles(os.path.join(r_dir, file),
                     os.path.join(s_dir, file),)
    if os.listdir(s_dir) == []:
        shutil.rmtree(s_dir)

def doc2zip(r_dir, name):
    doc = word.Documents.Open(os.path.normcase(os.path.join(r_dir, name + '.doc')))
    doc.SaveAs(os.path.join(temp_dir, name + '.docx'), 12)
    doc.Close()
    os.rename(os.path.join(temp_dir, name + '.docx'),
                  os.path.join(temp_dir, temp_zip))

def hasPic():
    raw_file = os.path.join(temp_dir, temp_zip)
    try:
        f = zipfile.ZipFile(raw_file, 'r')
    except:
        return False
    for file in f.namelist():
        f.extract(file, temp_dir)
    f.close()
    imgs_dir = os.path.join(temp_dir, 'word/media')
    if os.path.exists(imgs_dir):
        imgs = os.listdir(imgs_dir)
        if imgs != []:
            return True
    return False

if __name__ == '__main__':
    word = wc.Dispatch("Word.Application")
    read_dir = getFilePath(READ_FILE)
    if read_dir == '':
        sys.exit()
    save_dir = read_dir + '_bk'
    temp_dir = read_dir + '_tmp1234'
    temp_zip = 'temp.zip'

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    try:
        getFiles(read_dir, save_dir)
    except:
        os.makedirs(os.path.join(save_dir, 'error_occurred'))

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


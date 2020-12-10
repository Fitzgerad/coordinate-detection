import identify

class Test_item():
    def __init__(self):
        a = 0
    def error(self):
        return 0
    def update(self, n):
        return 0

class Test_w():
    def __init__(self):
        self.items = Test_item()

    def item(self, n):
        return self.items

if __name__ == "__main__":
    list_image_path = ['basemap/测试/02.jpg']
    widget_file_list = Test_w()
    identify.main(list_image_path, widget_file_list)
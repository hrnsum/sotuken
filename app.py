import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from ultralytics import YOLO
import os, time, datetime, threading, subprocess, cv2, shutil
import customtkinter

FONT_TYPE = "meiryo"

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 15)
        self.geometry("1000x650")
        self.title("YOLOPlus")
        self.resizable(width="False",height="False")
        self.setup_form()

    
    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        frame1 = customtkinter.CTkFrame(master=self,width=500)
        frame1.place(x=150, y=50)
        global file_path, filepath_entry
        file_path = customtkinter.StringVar()
        filepath_entry = customtkinter.CTkEntry(frame1, width=500, font=self.fonts,textvariable=file_path)
        filepath_entry.place(x=0, y=0)

        self.button = customtkinter.CTkButton(master=self, text="参照", command=self.click_refer_button, font=self.fonts,width=80)
        self.button.place(x=670, y=50)
        self.button2 = customtkinter.CTkButton(master=self, text="表示", command=self.click_display_button, font=self.fonts,width=80)
        self.button2.place(x=770, y=50)
        self.yolo_button = customtkinter.CTkButton(self, text=u'画像認識', command=self.click_detect_button)
        self.yolo_button.place(x=870,y=50)
    
        ########## 画像の縦横比率を維持してリサイズする関数 ##########
    def resizing(self,img,width):
        height = round(img.height * width/ img.width)
        return img.resize((width,height))
    

    ########## 参照の関数 ##########
    def click_refer_button(self):
        fTyp = [("JPEG",".jpg"),("PNG",".png")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        filepath = filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
        file_path.set(filepath)

    ########## 表示の関数 ##########
    def click_display_button(self):
        tval = filepath_entry.get()
        print("入力されたパス")
        print(tval)
        # ファイル名取得
        list = tval.split("/")   
        global filename
        filename = str(list[-1])
        print("ファイル名表示")
        print(list[-1])
        # 画像保存
        img = Image.open(tval)
        global img_resize, display 
        img_resize = self.resizing(img,600)
        img_resize.save("C:/GUI/img/" + filename)
        resized_img = Image.open("C:/GUI/img/" + filename)
        # 画像表示
        display = ImageTk.PhotoImage(resized_img)
        canvas = customtkinter.CTkCanvas(width=600, height=700,bg="#333", bd=5,highlightbackground="green")
        canvas.place(x=100,y=200)
        canvas.create_image(305,375,image=display)
        
    ########## 画像認識の関数 ##########
    def click_detect_button(self):
        global img_resize
        img_resize.save("C:/GUI/yolov5/data/images/" + "yolo_" + filename)
        shutil.rmtree("C:/GUI/yolov5/runs/detect/")
        os.mkdir("C:/GUI/yolov5/runs/detect/")
        command = "python yolov5/detect.py --weights yolov5s.pt --source yolov5/data/images/" + "yolo_" + filename
        subprocess.call(command,shell=True)
        path ="C:/GUI/yolov5/runs/detect/"
        files = os.listdir(path)
        print(files)
        img = Image.open("C:/GUI/yolov5/runs/detect/"+ files[-1] + "/" + "yolo_" + filename)
        # 画像保存
        self.img_resize = self.resizing(img,380)
        self.img_resize.save("C:/GUI/img/" + "yolo_" + filename)
        self.resized_img = Image.open("C:/GUI/img/" + "yolo_" + filename)
        print(self.resized_img)
        # 画像表示
        global display2,canvas2
        display2 = ImageTk.PhotoImage(self.resized_img)
        print(display2)
        self.canvas2 = tk.Canvas(width=400, height=500 ,bg="#333", bd=5, highlightbackground="red")
        self.canvas2.place(x=500,y=100)
        self.canvas2.create_image(207.5,250,image=display2)

    def button_function(self):
        print(self.textbox.get())


if __name__ == "__main__":
    app = App()
    app.mainloop()



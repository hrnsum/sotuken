import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from ultralytics import YOLO
import os, time, datetime, threading, subprocess, cv2, shutil
import customtkinter

FONT_TYPE = "meiryo"

class App(customtkinter.CTk):
    # 初期設定
    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 18)
        self.geometry("1000x660")
        self.title("YOLOPlus")
        self.resizable(width="False",height="False")
        self.setup_form()
    ########## 見た目作成部分 ##########
    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        # ファイル名テキストボックス
        frame1 = customtkinter.CTkFrame(master=self,width=584,height=35)
        frame1.place(x=66, y=20)
        global file_path, filepath_entry
        file_path = customtkinter.StringVar()
        filepath_entry = customtkinter.CTkEntry(frame1, width=584, font=self.fonts,textvariable=file_path)
        filepath_entry.place(x=0, y=0)
    
        self.button = customtkinter.CTkButton(master=self, text="参照", command=self.click_refer_button, font=self.fonts,width=80,text_color="#000")
        self.button.place(x=670, y=20)
        self.button2 = customtkinter.CTkButton(master=self, text="表示", command=self.click_display_button, font=self.fonts,width=80,text_color="#000")
        self.button2.place(x=770, y=20)
        self.refine_button = customtkinter.CTkButton(self, text=u'高画質化', command=self.click_refine_button, font=self.fonts,width=150,height=70,text_color="#000")
        self.refine_button.place(x=108,y=560)
        self.yolo_button = customtkinter.CTkButton(self, text=u'画像認識', command=self.click_detect_button, font=self.fonts,width=150,height=70,text_color="#000")
        self.yolo_button.place(x=278,y=560)
        self.yolo_button2 = customtkinter.CTkButton(self, text=u'●', command=self.click_camera_button, font=self.fonts,width=30,height=30,fg_color="red",border_color="#fff",border_width=1)
        self.yolo_button2.place(x=890,y=20)

    
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
        canvas = customtkinter.CTkCanvas(width=600, height=700,bg="#34343c", highlightbackground="#2ca474")
        canvas.place(x=100,y=120)
        canvas.create_image(305,365,image=display)
        
    ########## 画像認識の関数 ##########
    def click_detect_button(self):
        global img_resize
        img_resize.save("C:/GUI/yolov8/data/images/" + "yolo_" + filename)
        shutil.rmtree("C:/GUI/runs/detect/")
        os.mkdir("C:/GUI/runs/detect/")
        command = "yolo task=detect mode=predict model=yolov8x.pt source=""C:/GUI/yolov8/data/images/" + "yolo_" + filename
        subprocess.call(command,shell=True)
        path ="C:/GUI/runs/detect/"
        files = os.listdir(path)
        print(files)
        img = Image.open("C:/GUI/runs/detect/"+ files[-1] + "/" + "yolo_" + filename)
        # 画像保存
        self.img_resize = self.resizing(img,600)
        self.img_resize.save("C:/GUI/img/" + "yolo_" + filename)
        self.resized_img = Image.open("C:/GUI/img/" + "yolo_" + filename)
        print(self.resized_img)
        # 画像表示
        global display2,canvas2
        display2 = ImageTk.PhotoImage(self.resized_img)
        print(display2)
        self.canvas2 = customtkinter.CTkCanvas(width=600, height=700 ,bg="#34343c", highlightbackground="red")
        self.canvas2.place(x=780,y=120)
        self.canvas2.create_image(305,365,image=display2)
    
    ########## カメラ起動して物体検知、画像保存する関数（撮影開始ボタンを押すと実行される） ##########
    def click_camera_button(self):
        self.judge = 0
        try:
            shutil.rmtree("C:/GUI/runs/detect/")
        except:
            print("I can't find!!!")
        ##### 画像が保存されたか確認、されてたらそのときの日時を取得する関数 #####
        def check_get_time():
            if self.judge == 1:
                return
            print('Connecting ...')
            path = "C:/GUI/runs/detect/predict/crops/person/"
            try:
                global directory, detect_time, saved_number
                directory = os.listdir(path)
                length_small = len(directory)
                detect_time = []
                saved_number = []
                while True:
                    if self.judge == 1:
                        break
                    print("画像が保存されたかの確認処理")
                    directory = os.listdir(path)
                    length_large = len(directory)
                    print("検出回数")
                    print(length_small,length_large)
                
                    if length_small < length_large:
                        print("新しい画像が保存されました")
                        detect_time.append(str(datetime.datetime.now().replace(microsecond=0))) #日時取得
                        num = length_large - length_small
                        saved_number.append(num)
                        length_small = length_large
                        print("一度の検知で保存された画像枚数のデータ：")
                        print(saved_number)
                        print("検知した日時のデータ：：")
                        print(detect_time)
                        time.sleep(1)
            except:
                time.sleep(1)
                check_get_time()
        thread1 = threading.Thread(target=check_get_time) # 上のcheck_get_time関数は別のスレッドで実行（並列処理）
        thread1.start()
        # 検知したときに画像を保存
        def save_frame_img(self):
                    self.datas = []
                    j = 0 # 時刻参照用
                    k = 0 # 画像参照用
                    print(saved_number,detect_time)
                    shutil.rmtree("C:/GUI/result/detected_imgs/")
                    os.mkdir("C:/GUI/result/detected_imgs")
                    for n in saved_number:
                        i = 0 #n回に到達するまでのカウント用
                        while i <= n:
                            edit = str(detect_time[j]).replace(":","-").replace(" ","_")
                            d = edit + "_"+ directory[k]
                            self.datas.append(d)
                            img = Image.open("C:/GUI/runs/detect/predict/crops/person/" + directory[k])
                            # 画像リサイズ
                            self.img_resize = self.resizing(img,250)
                            self.img_resize.save("C:/GUI/result/detected_imgs/" + self.datas[k])
                            i = i + 1
                            k = k + 1
                        j = j + 1
                    print(self.datas)
        
        model = YOLO('yolov8n.pt')
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                global results
                results = model(frame,show=True,save=True,save_crop=True)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.judge = self.judge + 1
                    cap.release()
                    cv2.destroyAllWindows()
                    save_frame_img(self)
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
    
    def click_refine_button(self):
        print("clicked!!!")
        global img_resize
        img_resize.save("C:/GUI/SwinIR/testsets/RealSRSet+5images/" + filename)
        command = "python main_test_swinir.py --task real_sr --scale 4 --large_model --model_path model_zoo/swinir/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth --folder_lq SwinIR/testsets/RealSRSet+5images"
        subprocess.run(command,shell=True)
        
        img = Image.open("C:/GUI/SwinIR/results/swinir_real_sr_x4_large/" + filename)
        img_resize = self.resizing(img,600)
        img_resize.save("C:/GUI/img/" + filename)
        resized_img = Image.open("C:/GUI/SwinIR/results/swinir_real_sr_x4_large/" + filename)

        display = ImageTk.PhotoImage(resized_img)
        self.canvas1 = tk.Canvas(width=400, height=500,bg="#000", relief="solid", bd=5, highlightbackground="red")
        self.place(x=60,y=100)
        self.canvas1.create_image(200,250,image=display)

if __name__ == "__main__":
    app = App()
    app.mainloop()
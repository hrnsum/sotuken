import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from ultralytics import YOLO
import os, time, datetime, threading, subprocess, cv2, shutil

class Application(tk.Frame):
    ########## 初期設定 ##########
    def __init__(self,master):
        super().__init__(master)
        self.pack()
        self.master.geometry("1000x650")
        self.master.resizable(width="False",height="False")
        self.master.title("YOLOplus")

    ########## 画像の縦横比率を維持してリサイズする関数 ##########
    def resizing(img,width):
        height = round(img.height * width/ img.width)
        return img.resize((width,height))
    
    ########## 参照の関数（参照ボタンを押すと実行される） ##########
    def click_refer_button(self):
        fTyp = [("JPEG",".jpg"),("PNG",".png")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        filepath = filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
        file_path.set(filepath)

    ########## 表示の関数（表示ボタンを押すと実行される） ##########
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
        img_resize = Application.resizing(img,380)
        img_resize.save("C:/GUI/img/" + filename)
        resized_img = Image.open("C:/GUI/img/" + filename)
        # 画像表示
        display = ImageTk.PhotoImage(resized_img)
        canvas = tk.Canvas(width=400, height=500,bg="#000", bd=5,highlightbackground="red")
        canvas.place(x=67,y=100)
        canvas.create_image(207.5,250,image=display)

    ########## 高画質化の関数（高画質化ボタンを押すと実行される） ##########
    def click_refine_button(self):
        global img_resize, display
        img_resize.save("C:/GUI/SwinIR/testsets/RealSRSet+5images/" + filename)
        command = "python SwinIR/main_test_swinir.py --task real_sr --scale 4 --large_model --model_path model_zoo/swinir/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth --folder_lq SwinIR/testsets/RealSRSet+5images"
        subprocess.run(command,shell=True)
        img = Image.open("C:/GUI/SwinIR/results/swinir_real_sr_x4_large/" + filename)
        # 画像保存
        img_resize = Application.resizing(img,380)
        img_resize.save("C:/GUI/img/" + filename)
        resized_img = Image.open("C:/GUI/SwinIR/results/swinir_real_sr_x4_large/" + filename)
        # 画像表示
        display = ImageTk.PhotoImage(resized_img)
        self.canvas1 = tk.Canvas(width=400, height=500,bg="#333", relief="solid", bd=5, highlightbackground="red")
        self.place(x=60,y=100)
        self.canvas1.create_image(207.5,250,image=display)

    ########## 画像認識の関数（画像認識ボタンを押すと実行される） ##########
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
        self.img_resize = Application.resizing(img,380)
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

        def save_frame_img(self):
                    Application.datas = []
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
                            self.img_resize = Application.resizing(img,250)
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


########## こっから下はアプリの見た目（ボタンとか）##########
def main():
    win = tk.Tk()
    app = Application(master=win)
    frame1 = ttk.Frame(app,padding=10)
    frame1.grid()
    # ラベル
    s = tk.StringVar()
    s.set("ファイル名")
    label1 = ttk.Label(frame1,textvariable=s)
    label1.grid(row=0,column=0)
    # ファイル名を入力するテキストボックス
    global file_path, filepath_entry
    file_path = tk.StringVar()
    filepath_entry = ttk.Entry(frame1,textvariable=file_path,width=50)
    filepath_entry.grid(row=0,column=1)
    
    # 参照ボタン
    refer_button = ttk.Button(app,text=u"参照",command=app.click_refer_button)
    refer_button.grid(row=0, column=2)
    # 表示ボタン
    display_button = ttk.Button(app, text=u'表示', command=app.click_display_button)
    display_button.grid(row=0, column=3)
    # 高画質化ボタン
    refine_button = ttk.Button(app, text=u'高画質化', command=app.click_refine_button)
    refine_button.grid(row=1, column=2)
    # 画像認識ボタン
    yolo_button = ttk.Button(app, text=u'画像認識', command=app.click_detect_button)
    yolo_button.grid(row=1, column=3)
    # 撮影開始ボタン
    yolo_button2 = ttk.Button(app, text=u'撮影開始', command=app.click_camera_button)
    yolo_button2.grid(row=1, column=4)

    app.mainloop()
if __name__ == "__main__":
    main()

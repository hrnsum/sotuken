from ultralytics import YOLO

source = "gazou/beetle_test.png" # 自身が検出したいデータの位置
model = YOLO('best.pt') # 学習した重みデータ

model.predict(source, save=True, imgsz=640, conf=0.5)
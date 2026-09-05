from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage 
import cv2
import numpy as np
import time 
import requests

class Detection(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, token, location, receiver):
        super(Detection, self).__init__()
        self.token = token
        self.location = location
        self.receiver = receiver
        self.running = False

    def run(self):
        self.running = True

        net = cv2.dnn.readNet("weights/yolov4.weights", "cfg/yolov4.cfg")

        with open("obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        
        layer_names = net.getLayerNames()
        output_layers = net.getUnconnectedOutLayers().flatten()
        output_layers = [layer_names[i - 1] for i in output_layers]

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time()

        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()

            if not ret:
                continue

            height, width, channels = frame.shape

            blob = cv2.dnn.blobFromImage(
                frame,
                0.00392,
                (416, 416),
                (0, 0, 0),
                True,
                crop=False
            )

            net.setInput(blob)
            outs = net.forward(output_layers)

            class_ids = []
            confidences = []
            boxes = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    # ✅ Only weapon class (assumed class 0)
                    if class_id != 0:
                        continue

                    # ✅ 75% CONFIDENCE THRESHOLD
                    if confidence > 0.75:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # ✅ Strict NMS Settings
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.75, 0.3)

            if len(indexes) > 0:
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]

                    color = (0, 0, 255)

                    percentage = int(confidence * 100)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(
                        frame,
                        f"{label} {percentage}%",
                        (x, y - 10),
                        font,
                        2,
                        color,
                        2
                    )

                    # Alert every 10 seconds only
                    elapsed_time = time.time() - starting_time
                    if elapsed_time >= 10:
                        starting_time = time.time()
                        self.save_detection(frame)

            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytesPerLine = channels * width
            convertToQtFormat = QImage(
                rgbImage.data,
                width,
                height,
                bytesPerLine,
                QImage.Format_RGB888
            )
            p = convertToQtFormat.scaled(854, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

    def save_detection(self, frame):
        cv2.imwrite("save_frame/frame.jpg", frame)
        print("Frame Saved")
        self.post_detection()

    def post_detection(self):
        try:
            url = 'http://127.0.0.1:8000/api/images/'
            headers = {'Authorization': 'Token ' + self.token}
            files = {'image': open('save_frame/frame.jpg', 'rb')}
            data = {
                'user_ID': self.token,
                'location': self.location,
                'alert_receiver': self.receiver
            }

            response = requests.post(url, files=files, headers=headers, data=data)

            if response.ok:
                print('Alert was sent to the server')
            else:
                print('Unable to send alert to the server')

        except Exception as e:
            print('REAL ERROR:', e)
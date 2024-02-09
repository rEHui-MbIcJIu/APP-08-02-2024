#!/usr/bin/python
import serial
import argparse
import cv2
import time


class QrReader:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        # self.cap.set(cv2.CAP_PROP_FOCUS, 40)

        self.detector = cv2.QRCodeDetector()

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def try_read(self, tries):
        try_cnt = tries
        while True:
            _, img = self.cap.read()
            (h, w) = img.shape[:2]
            (cX, cY) = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D((cX, cY), 200, 1.0)
            img = cv2.warpAffine(img, M, (w, h))
            img = img[0 : h // 3 * 2, w // 2 : w]
            data, bbox, _ = self.detector.detectAndDecode(img)
            if data:
                cv2.polylines(img, bbox.astype(int), True, (0, 255, 0), 5)
            else:
                try_cnt -= 1

            if try_cnt == 0 or data:
                return data, img


class MotorController:
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = None
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.write_timeout = None

        try:
            self.ser.open()
        except Exception as e:
            print("error open serial port: " + str(e))
            exit()

        if not self.ser.isOpen():
            print("cannot open serial port")
            exit()

        self.ser.flushInput()
        self.ser.flushOutput()

        start_msg = self.ser.readline()
        if start_msg != b"START\r\n":
            print("Wrong start message", start_msg)
            exit()

    def __del__(self):
        self.ser.close()

    def send_cmd(self, cmd):
        if cmd != None:
            self.ser.write(cmd)
        self.ser.flushOutput()

        resp = self.ser.readline()
        if resp != b"OK\r\n":
            print("Wrong response", resp)
            exit()

    def home(self):
        self.send_cmd(b"H")

    def move(self, item_n):
        self.send_cmd(b"M%d" % (item_n))

    def move_camera(self, item_n):
        self.send_cmd(b"C%d" % (item_n))

    def take(self):
        self.send_cmd(b"T")

    def put(self):
        self.send_cmd(b"P")


def scan_all(qr, controller):
    items = []
    for i in range(9):
        controller.move_camera(i)
        qr_data, img = qr.try_read(100)
        img_s = cv2.resize(img, (500, 500))
        cv2.imshow("QR Reader", img_s)
        cv2.waitKey(1)
        items.append(qr_data)

    return items

def find_item_index(item, items_all):
    for item_cmp in items_all:
        if item.lower() == item_cmp.lower():
            return items_all.index(item_cmp)
    return None

def bring_item(item_n, controller):
    controller.move(item_n)
    controller.take()
    controller.put()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Storage bot controller")
    parser.add_argument("port", help="Serial port")
    parser.add_argument("items", help="Items to take")
    args = parser.parse_args()

    controller = MotorController(args.port)
    controller.home()
    qr = QrReader()

    items_all = scan_all(qr, controller)
    print(items_all)
    items_req = args.items.split(";")
    print(items_req)
    for item_find in items_req:
        item_n = find_item_index(item_find, items_all)
        if item_n != None:
            bring_item(item_n, controller)
        else:
            print(item_find, "Not found!")

    time.sleep(2)

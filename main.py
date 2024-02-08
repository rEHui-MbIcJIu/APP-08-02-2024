import requests
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast

KV = """
<CB@OneLineAvatarIconListItem>:
    IconLeftWidget:
        id: i1
        icon: "wrench"
    IconRightWidget:
        icon: "check-box"
        MDCheckbox:
            on_active:
                app.save_checked(*args,root.text,root.ids.i1.icon,root)

BoxLayout:
    orientation: "vertical"
    MDTopAppBar:
        pos_hint:{"center_x":.5, "center_y":.95}
        title: "Автокомплектовщик"
        
    ScrollView:
        size_hint_y:.9
        MDList:
            id: scroll
            CB:
                text: "Деталь №1"
                icon: "check-box"
            CB:
                text: "Деталь №2"
                icon: "pencil"
            CB:
                text: "Деталь №3"
                icon: "pencil"
            CB:
                text: "Деталь №4"
                icon: "pencil"
            CB:
                text: "Деталь №5"
                icon: "pencil"
            CB:
                text: "Деталь №6"
                icon: "pencil"
            CB:
                text: "Деталь №7"
                icon: "pencil"
            CB:
                text: "Деталь №8"
                icon: "pencil"
            CB:
                text: "Деталь №9"
                icon: "pencil"

    MDRaisedButton:
        id: cm
        pos_hint:{'center_x':0.9, 'center_y':1.0}
        text: "Save"
        on_release: app.send()
"""


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.url = "http://192.168.1.70:8080"  # url on local net

    def build(self):
        return Builder.load_string(KV)

    def save_checked(self, checkbox, value, a, c, w):
        # a - text
        # value - state(True/False) on and off
        # c - icon
        # checkbox and w - kivy args
        if value:
            print(checkbox, value, a, c, w)
            self.data.append(a[-1:])
        else:
            self.data.remove(a[-1:])

    def send(self):
        body = {
            "requested_list": self.data
        }
        print(body)
        headers = {
            'Content-Type': 'application/json'
        }
        if self.data != None or self.data != []:
            api_response = requests.post(self.url + "/send_list", headers=headers, data=json.dumps(body))
            # response = json.loads(api_response.text) - load response or whatever
            toast("Запрос выполнен")


MainApp().run()

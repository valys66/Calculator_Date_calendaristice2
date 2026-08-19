[app]
title = Calculator Date
package.name = datecalculator
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 24
android.ndk = 25b
android.accept_sdk_licenses = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1

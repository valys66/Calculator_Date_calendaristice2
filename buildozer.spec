[app]
title = Calculator Date
package.name = datecalculator
package.domain = org.test
source.dir = .
source.include_exts = py,kv
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Setări stabile de Android SDK/NDK
android.api = 31
android.minapi = 24
android.ndk = 23b
android.archs = arm64-v8a
android.accept_sdk_licenses = True

# Dezactivăm modulele SDL de care nu avem nevoie pentru un calculator
p4a.bootstrap = sdl2
p4a.local_recipes = 

[buildozer]
log_level = 2
warn_on_root = 1

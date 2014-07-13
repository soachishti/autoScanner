import os
import site
import sys
import glob
from cx_Freeze import setup, Executable

siteDir = site.getsitepackages()[1]
includeDllPath = os.path.join(siteDir, "gnome")

# missingDll = glob.glob(includeDllPath + "\\" + '*.dll')

missingDLL = ['libffi-6.dll',
              'libgirepository-1.0-1.dll',
              'libgio-2.0-0.dll',
              'libglib-2.0-0.dll',
              'libintl-8.dll',
              'libgmodule-2.0-0.dll',
              'libgobject-2.0-0.dll',
              'libzzz.dll',
              'libwinpthread-1.dll',
              'libgtk-3-0.dll',
              'libgdk-3-0.dll',
              'libcairo-gobject-2.dll',
              'libfontconfig-1.dll',
              'libxmlxpat.dll',
              'libfreetype-6.dll',
              'libpng16-16.dll',
              'libgdk_pixbuf-2.0-0.dll',
              'libjpeg-8.dll',
              'libopenraw-7.dll',
              'librsvg-2-2.dll',
              'libpango-1.0-0.dll',
              'libpangocairo-1.0-0.dll',
              'libpangoft2-1.0-0.dll',
              'libharfbuzz-gobject-0.dll',
              'libpangowin32-1.0-0.dll',
              'libwebp-4.dll',
              'libatk-1.0-0.dll',
              'libgnutls-26.dll',
              'libproxy.dll',
              'libp11-kit-0.dll',
              ]


includeFiles = []
for DLL in missingDLL:
    includeFiles.append((os.path.join(includeDllPath, DLL), DLL))

#gtkLibs= ['etc','lib','share']

gtkLibs = ['lib\\gdk-pixbuf-2.0',
           'lib\\girepository-1.0',
           'share\\glib-2.0',
           'lib\\gtk-3.0']

for lib in gtkLibs:
    includeFiles.append((os.path.join(includeDllPath, lib), lib))

includeFiles.append(("includes"))
includeFiles.append(("LICENSE"))

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="autoScanner",
    author="SOAChishti",
    version="1.1",
    description="GUI of Twain and SANE API with auto scanning.",
    options={'build_exe': {
        'compressed': True,
        'includes': ["gi"],
        'excludes': ['wx', 'email', 'pydoc_data', 'curses'],
        'packages': ["gi"],
        'include_files': includeFiles
    }},
    executables=[
        Executable(script = "autoScanner.py",
                    icon = "includes\\icon.ico",
                   base=base
                   )
    ]
)

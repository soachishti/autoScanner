import os
import site
import sys
from cx_Freeze import setup, Executable

siteDir = site.getsitepackages()[1]
includeDllPath = os.path.join(siteDir, "gnome")

missinDLL = [
    'libffi-6.dll',
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
]


gtkLibs = ['lib', 'share\\glib-2.0']

include_files = []
for dll in missinDLL:
    include_files.append((os.path.join(includeDllPath, dll), dll))

include_files.append(('includes','includes'))

for lib in gtkLibs:
    include_files.append((os.path.join(includeDllPath, lib), lib))

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("main.py",
               base=base)]

buildOptions = dict(compressed=True,
                    includes=["gi"],
                    packages=["gi"],
                    include_files=include_files
                    )

setup(name="autoScanner",
      author="SOAChishti",
      version="0.1",
      description="Automatic Scanner",
      author_email="soachishti[at]outlook.com",
      options=dict(build_exe=buildOptions),
      executables=executables
      )

# Build from a Python environment containing requirements-build.txt.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files,collect_submodules
root=Path(SPECPATH).parent
resources=[(str(root/'data'),'resources/data'),
    (str(root/'player'),'resources/player'),
    (str(root/'docs/GUIDE-STF.txt'),'resources/docs'),
    (str(root/'docs/GUIDE-STF.en.txt'),'resources/docs'),
    (str(root/'README.en.md'),'resources'),
    (str(root/'README.md'),'resources'),
    (str(root/'THIRD_PARTY.md'),'resources'),
    (str(root/'LICENSE'),'resources'),
    (str(root/'build/notices'),'resources/notices')]
datas=resources+collect_data_files('imageio_ffmpeg')
a=Analysis([str(root/'tools/app.py')],pathex=[str(root/'tools')],
    binaries=[],datas=datas,hiddenimports=collect_submodules('yt_dlp'),
    excludes=['matplotlib','scipy','pandas','IPython','pytest','notebook'])
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='STVideo',
    console=False,debug=False,strip=False,upx=False,
    version=str(root/'packaging/windows-version.txt'))

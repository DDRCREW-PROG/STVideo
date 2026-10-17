"""Build the standalone app, portable ZIP and optional Inno Setup installer."""
from pathlib import Path
import argparse,hashlib,importlib.metadata,json,os,shutil,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/python'))
from app_runtime import VERSION

def run(args):
    subprocess.run([str(a) for a in args],check=True,cwd=ROOT)

def notices():
    import imageio_ffmpeg
    dest=ROOT/'build/notices';dest.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'licenses',dest/'licenses',dirs_exist_ok=True)
    versions={}
    for name in ['numpy','Pillow','imageio-ffmpeg','yt-dlp','pyinstaller']:
        distribution=importlib.metadata.distribution(name);versions[name]=distribution.version
        for f in distribution.files or []:
            if any(word in Path(f).name.lower() for word in ('license','licence','copying','notice')):
                source=Path(distribution.locate_file(f))
                if source.is_file():
                    target=dest/name/str(f).replace('..','_');target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source,target)
    python_license=Path(sys.base_prefix)/'LICENSE.txt'
    if python_license.exists():shutil.copy2(python_license,dest/'Python-LICENSE.txt')
    for folder in (Path(sys.base_prefix)/'tcl').glob('*'):
        if folder.is_dir():
            for license in folder.glob('license*'):
                shutil.copy2(license,dest/(folder.name+'-'+license.name))
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    result=subprocess.run([ffmpeg,'-version'],capture_output=True,text=True,check=True)
    (dest/'FFmpeg-version.txt').write_text(result.stdout,encoding='utf-8')
    (dest/'FFmpeg-sources.txt').write_text(
        'The embedded FFmpeg binary is distributed by imageio-ffmpeg.\n'
        'Binary and source provenance: https://github.com/imageio/imageio-ffmpeg\n'
        'Windows binary supplier: https://www.gyan.dev/ffmpeg/builds/\n'
        'FFmpeg source: https://ffmpeg.org/releases/ (see exact version in FFmpeg-version.txt).\n'
        'Build configuration and dependency list: FFmpeg-version.txt.\n'
        'This binary enables GPL and version3. See https://ffmpeg.org/legal.html .\n',encoding='utf-8')
    manifest={'application':VERSION,'python':sys.version,'dependencies':versions,
        'ffmpeg_sha256':hashlib.sha256(Path(ffmpeg).read_bytes()).hexdigest(),
        'player_sha256':hashlib.sha256((ROOT/'player/STFPLAY.PRG').read_bytes()).hexdigest()}
    (dest/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def source_archive():
    dest=ROOT/f'dist/STVideo-{VERSION}-sources.zip'
    selected=['README.en.md','README.md','LICENSE','THIRD_PARTY.md','requirements.txt','requirements-build.txt',
        'ENCODER.cmd','INSTALLER-DEPENDANCES.cmd','.gitignore','packaging','data','player','licenses']
    docs=['docs/GUIDE-STF.en.txt','docs/GUIDE-STF.txt','docs/BUILD-WINDOWS.md','docs/FORMAT-STV.md','docs/VALIDATION.md']
    tools=['app.py','app_runtime.py','encoder_gui.pyw','encoder_ui.py','encode.py','quality.py',
        'build_windows.py','build.ps1','translations.py','test_ym.py','test_palette.py','test_output_names.py','test_encoder_ui.py']
    files=[]
    for relative in selected+docs+['src/player.s']+['tools/'+n for n in tools]:
        p=ROOT/relative
        if p.is_file():files.append(p)
        elif p.is_dir():files.extend(f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
        else:raise FileNotFoundError(p)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in sorted(set(files)):archive.write(f,'STVideo-'+VERSION+'/'+str(f.relative_to(ROOT)))
    return dest

def main():
    p=argparse.ArgumentParser();p.add_argument('--inno',type=Path);p.add_argument('--skip-freeze',action='store_true');args=p.parse_args()
    if not (ROOT/'player/STFPLAY.PRG').exists():raise SystemExit('Recompiler le lecteur ou fournir player/STFPLAY.PRG.')
    (ROOT/'dist').mkdir(exist_ok=True);notices()
    if not args.skip_freeze:
        run([sys.executable,'-m','PyInstaller','--noconfirm','--distpath',ROOT/'dist/frozen',
            '--workpath',ROOT/'build/pyinstaller',ROOT/'packaging/STVideo.spec'])
    portable=ROOT/f'dist/portable-{VERSION}';portable.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'dist/frozen/STVideo.exe',portable/'STVideo.exe')
    for relative in ['README.en.md','README.md','LICENSE','THIRD_PARTY.md']:
        shutil.copy2(ROOT/relative,portable/relative)
    guide=portable/'Guide-STF.txt';shutil.copy2(ROOT/'docs/GUIDE-STF.txt',guide)
    shutil.copy2(ROOT/'docs/GUIDE-STF.en.txt',portable/'Guide-STF.en.txt')
    target_notices=portable/'notices';shutil.copytree(ROOT/'build/notices',target_notices,dirs_exist_ok=True)
    source=source_archive();shutil.copy2(source,portable/source.name)
    zip_path=ROOT/f'dist/STVideo-{VERSION}-Windows-portable.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as archive:
        for f in sorted(portable.rglob('*')):
            if f.is_file():archive.write(f,'STVideo/'+str(f.relative_to(portable)))
    if args.inno:run([args.inno,f'/DAppSource={portable}',ROOT/'packaging/windows-installer.iss'])
    files=[p for p in (ROOT/'dist').iterdir() if p.is_file()]
    sums='\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in files if p.name!='SHA256SUMS.txt')+'\n'
    (ROOT/'dist/SHA256SUMS.txt').write_text(sums,encoding='ascii')
    print('Distribution prÃªte :',ROOT/'dist',flush=True)

if __name__=='__main__':main()

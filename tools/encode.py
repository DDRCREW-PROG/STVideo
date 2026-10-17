"""PC video -> native ST bitplanes, legacy LAV2 and STF/YM stream.

FFmpeg decodes the source; the Atari never decompresses video.
"""
from pathlib import Path
import argparse, json, os, struct, subprocess, sys, tempfile, wave
from app_runtime import ROOT
from translations import translate
sys.path.insert(0, str(ROOT/'vendor/python'))
import numpy as np
from PIL import Image
import imageio_ffmpeg
from quality import perceptual_palette,perceptual_indices,scene_groups,SingleWriteYM,LookaheadYM,ym_levels

BLOCK = 32768
RATE = 12288

def planar(indices):
    pixels = np.asarray(indices, dtype=np.uint8).reshape(200,20,16)
    bits = ((pixels[...,None] >> np.arange(4)) & 1).transpose(0,1,3,2)
    return np.packbits(bits,axis=-1,bitorder='big').tobytes()

def unplanar(blob):
    bits = np.unpackbits(np.frombuffer(blob,dtype=np.uint8).reshape(200,20,4,2),axis=-1)
    return (bits.transpose(0,1,3,2)*(1 << np.arange(4))).sum(axis=-1).astype('uint8').reshape(200,320)

def palette_for(frames):
    # Sample the whole batch, so motion does not redefine the palette each frame.
    samples = np.concatenate([np.asarray(f)[::4,::4].reshape(-1,3) for f in frames])
    quant = Image.fromarray(samples.reshape(1,-1,3)).quantize(colors=16,method=Image.Quantize.MEDIANCUT)
    # Pillow returns only the colors actually present on flat/sparse images.
    # Keep a fixed hardware palette without inventing black entries on white frames.
    rgb = np.asarray(quant.getpalette()[:48],dtype=np.int32).reshape(-1,3)
    if not len(rgb):raise ValueError('Empty image palette')
    if len(rgb)<16:rgb=np.pad(rgb,((0,16-len(rgb)),(0,0)),mode='edge')
    rgb = np.rint(np.rint(rgb*7/255)*255/7).astype('uint8')
    # Fixed ordering makes index zero the darkest entry (useful for borders).
    rgb = rgb[np.argsort(rgb.astype(float) @ [0.299,0.587,0.114])]
    p = Image.new('P',(1,1)); p.putpalette(rgb.flatten().tolist()+rgb[0].tolist()*240)
    levels = np.rint(rgb.astype(float)*7/255).astype(int)
    words = (levels[:,0]<<8)|(levels[:,1]<<4)|levels[:,2]
    return p,rgb,struct.pack('>16H',*words)

def quantize(frame, pal, rgb, dither,quality='classic',strength=.7):
    if dither=='adaptive' or (quality=='perceptual' and dither=='none'):
        a=perceptual_indices(frame,rgb,dither=='adaptive',strength)
        return planar(a),Image.fromarray(rgb[a])
    if dither == 'ordered':
        bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
        offsets=np.tile((bayer-7.5)*2,(50,80))[...,None]
        frame=Image.fromarray(np.clip(np.asarray(frame,dtype=float)+offsets,0,255).astype('uint8'))
    mode=Image.Dither.FLOYDSTEINBERG if dither=='floyd' else Image.Dither.NONE
    indexed=frame.quantize(palette=pal,dither=mode)
    # Pillow's padded palette contains black duplicate entries; normalize them.
    a=np.asarray(indexed).copy();a[a>=16]=0
    return planar(a),Image.fromarray(rgb[a])

def ym_table():
    values=ym_levels(ROOT)
    # 256 PCM levels -> three volume commands, using measured nonlinear DAC.
    targets=np.linspace(values.min(),values.max(),256)
    states=abs(values[:,None]-targets[None,:]).argmin(axis=0)
    return b''.join(struct.pack('>III',0x08000000|((int(s)&15)<<8),
        0x09000000|(((int(s)>>4)&15)<<8),0x0a000000|(((int(s)>>8)&15)<<8)) for s in states)

def run(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[-2500:])
    return p.stdout

def audio_filters(profile,rate):
    if profile=='none':return []
    cutoff=min({'gentle':3800,'strong':2900,'voice':3200}[profile],rate*.4)
    noise={'gentle':6,'strong':12,'voice':10}[profile]
    high=100 if profile=='voice' else 45
    chain=f'highpass=f={high},afftdn=nr={noise}:nf=-50:tn=1,lowpass=f={cutoff}:p=2'
    if profile in ('strong','voice'):
        chain+=',agate=threshold=0.003:ratio=2:attack=12:release=150:range=0.15'
    return ['-af',chain]

def comparison(frame,group,output,name):
    from PIL import ImageDraw,ImageFont
    old=palette_for(group);optimized=perceptual_palette(group,old)
    panels=[('Source préparée (320x200)',frame),
        ('Ancienne palette, sans trame',quantize(frame,*old[:2],'none')[1]),
        ('ST optimisé, sans trame',quantize(frame,*optimized[:2],'none','perceptual')[1]),
        ('ST optimisé, trame adaptative',quantize(frame,*optimized[:2],'adaptive','perceptual')[1])]
    canvas=Image.new('RGB',(640,452),(24,27,34));draw=ImageDraw.Draw(canvas)
    try:font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    except OSError:font=ImageFont.load_default()
    for i,(label,picture) in enumerate(panels):
        x=(i%2)*320;y=(i//2)*226
        draw.text((x+6,y+3),label,font=font,fill='white');canvas.paste(picture,(x,y+26))
    canvas.save(output/f'{name}-COMPARAISON.png')

def reserve_name(output,requested):
    import re,unicodedata
    name=unicodedata.normalize('NFKD',requested.strip()).encode('ascii','ignore').decode().upper()
    if name.endswith(('.STV','.LAV')):name=name[:-4]
    name=name.replace(' ','_')
    if not re.fullmatch(r'[A-Z0-9_]{1,8}',name):
        raise ValueError('Nom du clip : 1 à 8 lettres/chiffres ou _, pour la compatibilité Atari.')
    if name in {'CON','PRN','AUX','NUL'} or re.fullmatch(r'(COM|LPT)[1-9]',name):
        raise ValueError('Ce nom est réservé par Windows. Choisissez un autre nom de clip.')
    def occupied(candidate):
        return ((output/f'{candidate}.STV').exists() or (output/f'{candidate}.LAV').exists()
                or any(output.glob(f'{candidate}-*')))
    for i in range(100000):
        suffix=str(i).zfill(3)
        candidate=name if i==0 else name[:8-len(suffix)]+suffix
        if occupied(candidate):continue
        lock=output/f'.{candidate}.encode.lock'
        try:
            with lock.open('x'):pass
        except FileExistsError:continue
        if occupied(candidate):lock.unlink();continue
        return candidate,lock
    raise ValueError('Trop de fichiers avec ce nom : choisissez un autre nom de clip.')

def encode(args):
    output=Path(args.output).resolve(); output.mkdir(parents=True,exist_ok=True)
    name,lock=reserve_name(output,args.name)
    if getattr(args,'language','fr')=='en':
        print(f'Output name: {name}\nST file: {output / (name+".STV")}',flush=True)
    else:
        print(f'Nom retenu : {name}\nFichier ST : {output / (name+".STV")}',flush=True)
    try:return encode_reserved(args,output,name)
    finally:lock.unlink(missing_ok=True)

def encode_reserved(args,output,name):
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    source=args.input
    stf_step=1 if args.stf_fps==25 else 2
    stf_rate=RATE if stf_step==1 else 8192
    with tempfile.TemporaryDirectory(prefix='st-video-') as tmp:
        tmp=Path(tmp)
        if source.startswith(('https://','http://')):
            from yt_dlp import YoutubeDL
            with YoutubeDL({'outtmpl':str(tmp/'source.%(ext)s'),'noplaylist':True,
                'format':'bestvideo+bestaudio/best','ffmpeg_location':ffmpeg}) as dl:
                info=dl.extract_info(source,download=True)
                source=dl.prepare_filename(info)
                if not Path(source).exists():
                    candidates=[p for p in tmp.glob('source.*') if p.suffix not in ('.part','.ytdl')]
                    if len(candidates)!=1: raise RuntimeError('Cannot identify downloaded media')
                    source=str(candidates[0])
        common=[ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-y']
        seek=['-ss',str(args.start)] if args.start else []
        duration=['-t',str(args.duration)] if args.duration else []
        vf='fps=25,scale=320:200:force_original_aspect_ratio=decrease:flags=lanczos,pad=320:200:(ow-iw)/2:(oh-ih)/2,setsar=1'
        if args.stretch: vf='fps=25,scale=320:200:flags=lanczos,setsar=1'
        if args.video_clean:vf='hqdn3d=1.5:1.5:3:3,'+vf
        sharpness=args.sharpness
        if args.sharpen and sharpness=='none':sharpness='soft'
        if sharpness!='none':
            amount={'soft':.35,'sharp':.65,'strong':1.0}[sharpness]
            vf+=f',unsharp=5:5:{amount}:3:3:0'
        raw=tmp/'frames.rgb'
        run(common+seek+['-i',source]+duration+['-an','-vf',vf,'-pix_fmt','rgb24','-f','rawvideo',str(raw)])
        n=raw.stat().st_size//192000
        if not n: raise ValueError('No video frames')
        # This format is enormous by design: fail explicitly before TOS file limits.
        if (n+1)*BLOCK>=2**31: raise ValueError('Clip exceeds 2 GiB; use --start and --duration to split it')
        audio={}
        for rate in [stf_rate,12517]:
            try:
                pcm=run(common+seek+['-i',source]+duration+['-vn','-ac','1']+audio_filters(args.audio_filter,rate)+['-ar',str(rate),'-acodec','pcm_f32le','-f','f32le','-'])
            except RuntimeError as e:
                if 'does not contain any stream' not in str(e) and 'matches no streams' not in str(e): raise
                pcm=b''
            need=(n*rate+24)//25
            samples=np.frombuffer(pcm,dtype='<f4').astype(np.float64)
            samples=np.pad(samples[:need],(0,max(0,need-len(samples))))
            if args.normalize and len(samples):
                peak=float(np.max(np.abs(samples)))
                if peak>1e-6:samples*=min(4.,.85/peak)
            samples*=10**(args.audio_gain/20)
            # Short edge ramps remove start/end clicks without changing timing.
            edge=min(round(rate*.004),len(samples)//2)
            if edge:
                samples[:edge]*=np.linspace(0,1,edge)
                samples[-edge:]*=np.linspace(1,0,edge)
            audio[rate]=np.clip(np.rint(samples*127+128),0,255).astype(np.uint8).tobytes()
            with wave.open(str(output/f'{name}-AUDIO{rate}.WAV'),'wb') as w:
                w.setnchannels(1);w.setsampwidth(1);w.setframerate(rate);w.writeframes(audio[rate])
        lav=output/f'{name}.LAV';stf=output/f'{name}.STV'
        lh=bytearray(BLOCK);lh[:6]=b'STEAV2';struct.pack_into('>I',lh,6,n)
        lh[256:256+4008]=audio[12517][:4008].ljust(4008,b'\x80').translate(bytes.maketrans(bytes(range(256)),bytes((i+128)%256 for i in range(256))))
        codec={'smooth':SingleWriteYM,'optimal':LookaheadYM}.get(args.audio_codec)
        codec=codec(ROOT) if codec else None
        sh=bytearray(BLOCK);sh[:8]=b'STFVID3\0' if args.audio_codec=='optimal' else (b'STFVID2\0' if codec else b'STFVID1\0');struct.pack_into('>III',sh,8,(n+stf_step-1)//stf_step,stf_rate,25 if stf_step==1 else 1250)
        sh[256:3328]=codec.table() if codec else ym_table()
        signed=bytes((i+128)%256 for i in range(256));audio_pos=4008
        previews=[];comparison_saved=False
        with raw.open('rb') as src,lav.open('wb') as lf,stf.open('wb') as sf:
            lf.write(lh);sf.write(sh)
            i=0
            while i<n:
                frames=[Image.frombytes('RGB',(320,200),src.read(192000)) for _ in range(min(args.palette_frames,n-i))]
                groups=list(scene_groups(frames,args.scene_cuts))
                prepared=[]
                for group in groups:
                    palette=palette_for(group)
                    if args.quality=='perceptual':palette=perceptual_palette(group,palette)
                    if not comparison_saved:
                        for candidate in group:
                            values=np.asarray(candidate)
                            if values.mean()>12 and values.std()>18:
                                comparison(candidate,group,output,name);comparison_saved=True;break
                    prepared.extend((frame,palette) for frame in group)
                for frame,(pal,rgb,words) in prepared:
                    bitmap,preview=quantize(frame,pal,rgb,args.dither,args.quality,args.dither_strength)
                    block=bytearray(BLOCK);block[:32000]=bitmap;block[32000:32032]=words
                    a=audio[12517][audio_pos:audio_pos+504].ljust(504,b'\x80').translate(signed)
                    block[32032:32536]=a;block[32536:32544]=f'Fram{i%10000:04d}'.encode()
                    lf.write(block)
                    # Match STEAV's ring-buffer lookahead and overlaps exactly.
                    audio_pos+=504
                    if i%16==7:audio_pos-=28
                    if i%16==15:audio_pos-=24
                    if i%stf_step==0:
                        start=i*stf_rate//25;end=(i+stf_step)*stf_rate//25
                        block[32032:32768]=bytes(736)
                        chunk=audio[stf_rate][start:end].ljust(end-start,b'\x80')
                        if codec:
                            chunk,initial=codec.encode(chunk)
                            block[32744:32756]=initial
                        block[32032:32032+end-start]=chunk
                        struct.pack_into('>H',block,32760,end-start)
                        sf.write(block)
                    if len(previews)<100:previews.append(preview)
                    if i==0:preview.save(output/f'{name}-PREVIEW.png')
                    i+=1
                print(f'{i}/{n} frames',flush=True)
        if previews:previews[0].save(output/f'{name}-PREVIEW.gif',save_all=True,append_images=previews[1:],duration=40,loop=0)
        if not comparison_saved and previews:comparison(previews[0],[previews[0]],output,name)
        report={'frames':n,'fps':25,'seconds':n/25,'resolution':[320,200],
            'colors':16,'palette':'ST 512 colors, 3 bits/channel','dither':args.dither,
            'output_name':name,'output_directory':str(output),
            'palette_frames':args.palette_frames,'bytes_per_second':BLOCK*25,
            'quality':args.quality,'scene_cuts':args.scene_cuts,'dither_strength':args.dither_strength,
            'audio_codec':args.audio_codec,'audio_filter':args.audio_filter,
            'normalize':args.normalize,'audio_gain_db':args.audio_gain,
            'video_clean':args.video_clean,'sharpness':sharpness,
            'lav':str(lav),'stf':str(stf),'stf_audio_rate':stf_rate,
            'stf_fps':args.stf_fps,'stf_bytes_per_second':BLOCK*args.stf_fps,
            'note':'Hatari GEMDOS does not measure physical ACSI speed.'}
        (output/f'{name}-REPORT.json').write_text(json.dumps(report,indent=2))
        import shutil
        player=ROOT/'player/STFPLAY.PRG'
        if not player.exists():player=ROOT/'build/hdd/STFPLAY.PRG'
        if player.exists() and player.resolve()!=(output/'STFPLAY.PRG').resolve():shutil.copy2(player,output/'STFPLAY.PRG')
        print(json.dumps(report,indent=2))

def main():
    p=argparse.ArgumentParser(description='Encode a local video or supported URL for ST/STE')
    p.add_argument('input');p.add_argument('-o','--output',default=str(ROOT/'build/hdd'))
    p.add_argument('--language',choices=['fr','en'],default='fr',help='Language for encoder messages')
    p.add_argument('--name',default='VIDEO',help='Nom Atari du clip (1 à 8 caractères). Numérotation automatique en cas de collision.')
    p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float)
    p.add_argument('--dither',choices=['ordered','floyd','none','adaptive'],default='adaptive')
    p.add_argument('--quality',choices=['classic','perceptual'],default='perceptual')
    p.add_argument('--dither-strength',type=float,default=.7)
    p.add_argument('--scene-cuts',action=argparse.BooleanOptionalAction,default=True)
    p.add_argument('--audio-codec',choices=['classic','smooth','optimal'],default='classic')
    p.add_argument('--audio-filter',choices=['none','gentle','strong','voice'],default='gentle')
    p.add_argument('--normalize',action=argparse.BooleanOptionalAction,default=True)
    p.add_argument('--audio-gain',type=float,default=0)
    p.add_argument('--video-clean',action='store_true')
    p.add_argument('--sharpen',action='store_true')
    p.add_argument('--sharpness',choices=['none','soft','sharp','strong'],default='none')
    p.add_argument('--palette-frames',type=int,default=25)
    p.add_argument('--stretch',action='store_true')
    p.add_argument('--stf-fps',type=float,choices=[25,12.5],default=25,
                   help='25 fps/12 kHz, or 12.5 fps/8 kHz for slower ACSI storage. LAV remains 25 fps.')
    args=p.parse_args()
    if args.start<0 or (args.duration is not None and args.duration<=0) or args.palette_frames<1:p.error('Invalid time or palette interval')
    if not 0<=args.dither_strength<=1 or not -24<=args.audio_gain<=12:p.error('Dither strength: 0..1; gain: -24..12 dB')
    try:encode(args)
    except (RuntimeError,ValueError,OSError) as e:p.exit(1,translate(str(e),args.language)+'\n')

if __name__=='__main__':main()

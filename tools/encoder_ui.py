"""Windows encoder UI, with hardware profiles and an integrated STF guide."""
from pathlib import Path
import json,os,queue,subprocess,sys,tempfile,threading,tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkinter.scrolledtext import ScrolledText
from app_runtime import ROOT,VERSION,default_output,worker_command
from translations import translate,option_code,ABOUT_EN

DITHERS={'Trame fixe (stable)':'ordered','Trame adaptative':'adaptive','Sans dithering':'none','Diffusion Floyd':'floyd'}
QUALITIES={'Palette ST optimisée':'perceptual','Palette classique rapide':'classic'}
CODECS={'Réglage audio optimisé pour STF (plus lent)':'optimal','Audio optimisé pour STE':'classic','YM léger (expérimental)':'smooth'}
FILTERS={'Léger':'gentle','Désactivé':'none','Renforcé':'strong','Voix':'voice'}
SHARPNESS={'Naturelle':'none','Légère':'soft','Plus nette':'sharp','Très nette':'strong'}

class EncoderApp:
    def __init__(self,app):
        self.app=app;self.events=queue.Queue();self.busy=False
        self.lang="fr";self.option_widgets=[];self.language=tk.StringVar(value="Français")
        self.config_path=Path(os.environ.get("LOCALAPPDATA",str(Path.home()/".config")))/"STVideo"/"settings.json"
        app.title(f'ST Vidéo {VERSION} — Encodeur Atari ST / STF / STE')
        width=min(940,max(760,app.winfo_screenwidth()-80))
        height=min(860,max(560,app.winfo_screenheight()-100))
        app.geometry(f'{width}x{height}');app.minsize(760,560)
        style=ttk.Style(app)
        if 'vista' in style.theme_names():style.theme_use('vista')
        style.configure('Title.TLabel',font=('Segoe UI',18,'bold'))
        self.source=tk.StringVar(value=sys.argv[1] if len(sys.argv)>1 else '')
        self.destination=tk.StringVar(value=sys.argv[2] if len(sys.argv)>2 else str(default_output()))
        self.clip_name=tk.StringVar(value='VIDEO');self.start=tk.StringVar(value='0');self.duration=tk.StringVar()
        self.fps=tk.StringVar();self.dither=tk.StringVar();self.quality=tk.StringVar();self.audio_codec=tk.StringVar()
        self.audio_filter=tk.StringVar(value='Léger');self.normalize=tk.BooleanVar(value=True)
        self.scene_cuts=tk.BooleanVar(value=True);self.video_clean=tk.BooleanVar(value=False)
        self.sharpness=tk.StringVar(value='Naturelle');self.strength=tk.DoubleVar(value=.7)
        shell=ttk.Frame(app,padding=16);shell.pack(fill='both',expand=True)
        header=ttk.Frame(shell);header.pack(fill='x')
        ttk.Label(header,text='ST Vidéo',style='Title.TLabel').pack(side='left')
        language_menu=ttk.Combobox(header,textvariable=self.language,values=['Français','English'],state='readonly',width=12)
        language_menu.pack(side='right')
        ttk.Label(header,text='Langue / Language').pack(side='right',padx=8)
        language_menu.bind('<<ComboboxSelected>>',lambda event:self.set_language('en' if self.language.get()=='English' else 'fr'))
        ttk.Label(shell,text='Vos vidéos sur Atari • 320 × 200 • 16 couleurs parmi 512 • PAL').pack(anchor='w',pady=(2,12))
        self.book=ttk.Notebook(shell);self.book.pack(fill='both',expand=True)
        page=ttk.Frame(self.book);self.book.add(page,text='  Encodage  ')
        self.guide_page=ttk.Frame(self.book,padding=12);self.book.add(self.guide_page,text='  Guide STF  ')
        about=ttk.Frame(self.book,padding=12);self.book.add(about,text='  À propos  ')
        canvas=tk.Canvas(page,highlightthickness=0)
        scrollbar=ttk.Scrollbar(page,orient='vertical',command=canvas.yview)
        scrollbar.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        form=ttk.Frame(canvas,padding=12);self.form_window=canvas.create_window((0,0),window=form,anchor='nw')
        form.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(self.form_window,width=e.width))
        canvas.bind('<MouseWheel>',lambda e:canvas.yview_scroll(-int(e.delta/120),'units'))
        profiles=ttk.LabelFrame(form,text='Démarrage rapide',padding=10);profiles.pack(fill='x',pady=(0,10))
        controls=ttk.Frame(profiles);controls.pack(fill='x');self.profile_buttons=[]
        for text,mode in [('Réglages STF / ACSI conseillés','stf'),('Réglages STE / débit rapide','ste')]:
            b=ttk.Button(controls,text=text,command=lambda m=mode:self.preset(m));b.pack(side='left',padx=(0,8));self.profile_buttons.append(b)
        self.profile_note=ttk.Label(profiles,wraplength=680);self.profile_note.pack(anchor='w',fill='x',pady=(8,0))
        profiles.bind('<Configure>',lambda e:self.profile_note.configure(wraplength=max(200,e.width-24)))
        files=ttk.LabelFrame(form,text='Source et destination',padding=10);files.pack(fill='x',pady=(0,10))
        self.entry(files,'Fichier vidéo ou URL',self.source,lambda:self.source.set(filedialog.askopenfilename() or self.source.get()))
        self.entry(files,'Dossier de sortie',self.destination,lambda:self.destination.set(filedialog.askdirectory() or self.destination.get()))
        fields=ttk.Frame(files);fields.pack(fill='x',pady=(4,0))
        for col,(label,var,hint) in enumerate([
            ('Nom du clip',self.clip_name,'8 caractères maximum ; numérotation automatique'),
            ('Début (secondes)',self.start,'0 = début du fichier'),
            ('Durée (secondes)',self.duration,'Laisser vide pour tout encoder')]):
            cell=ttk.Frame(fields);cell.grid(row=0,column=col,sticky='nsew',padx=(0,12) if col<2 else 0)
            fields.columnconfigure(col,weight=2 if col==0 else 1)
            ttk.Label(cell,text=label).pack(anchor='w')
            ttk.Entry(cell,textvariable=var,width=12).pack(fill='x',pady=(3,3))
            caption=ttk.Label(cell,text=hint,wraplength=230);caption.pack(anchor='w',fill='x')
            cell.bind('<Configure>',lambda e,w=caption:w.configure(wraplength=max(90,e.width)))
        image=ttk.LabelFrame(form,text='Image',padding=10);image.pack(fill='x',pady=(0,10))
        self.choice(image,'Palette',self.quality,QUALITIES)
        self.choice(image,'Tramage (dithering)',self.dither,DITHERS)
        options=ttk.Frame(image);options.pack(fill='x',pady=4)
        ttk.Checkbutton(options,text='Détecter les changements de plan',variable=self.scene_cuts).pack(anchor='w')
        ttk.Checkbutton(options,text='Nettoyer le bruit vidéo',variable=self.video_clean).pack(anchor='w')
        self.choice(image,'Netteté',self.sharpness,SHARPNESS)
        line=ttk.Frame(image);line.pack(fill='x',pady=4)
        ttk.Label(line,text='Intensité de la trame adaptative').pack(side='left')
        ttk.Scale(line,variable=self.strength,from_=0,to=1).pack(side='left',fill='x',expand=True,padx=12)
        audio=ttk.LabelFrame(form,text='Son et cadence',padding=10);audio.pack(fill='x',pady=(0,10))
        self.choice(audio,'Restitution audio',self.audio_codec,CODECS)
        self.choice(audio,'Nettoyage du son',self.audio_filter,FILTERS)
        ttk.Checkbutton(audio,text='Renforcer les sources faibles (maximum +12 dB)',variable=self.normalize).pack(anchor='w',pady=4)
        self.choice(audio,'Images par seconde du fichier STV',self.fps,['12.5','25'])
        self.rate_note=ttk.Label(audio,wraplength=680);self.rate_note.pack(fill='x',pady=(6,0))
        audio.bind('<Configure>',lambda e:self.rate_note.configure(wraplength=max(200,e.width-24)))
        self.fps.trace_add('write',lambda *args:self.update_rate())
        # Tk does not bubble child wheel events to the parent canvas. Bind
        # each form widget so scrolling also works over entries and menus.
        def scroll_form(event):
            canvas.yview_scroll(-int(event.delta/120),'units')
            return 'break'
        def bind_wheel(widget):
            widget.bind('<MouseWheel>',scroll_form)
            for child in widget.winfo_children():bind_wheel(child)
        bind_wheel(form)
        guide=ROOT/'docs'/'GUIDE-STF.txt'
        self.guide_view=self.document(self.guide_page,guide.read_text(encoding='utf-8') if guide.exists() else 'Consultez le README fourni avec l’application.')
        self.about_view=self.document(about,'ST Vidéo '+VERSION+'\n\nEncodeur Windows et lecteur 68000 pour Atari ST / STF / STE.\n\nProjet de David Ascenso, développé à partir de ses essais vidéo sur Atari.\n\nLe PC prépare les images et le son ; le ST lit les données natives, sans décompression vidéo.\nLe lecteur fourni est STFPLAY.PRG. Shift droit ouvre le sélecteur ; Échap quitte.\n\nLes fichiers STV1, STV2 et STV3 sont pris en charge. Pour profiter du DMA du STE, choisir Audio optimisé pour STE avant l’encodage.\n\nLes composants tiers et leurs licences sont décrits dans THIRD_PARTY.md, fourni avec les sources et l’application.\nAucun clip personnel ni ROM TOS n’est inclus.')
        footer=ttk.Frame(shell);footer.pack(fill='x',pady=(12,0))
        self.preview_button=ttk.Button(footer,text='Essayer sur 5 secondes',command=lambda:self.encode(True));self.preview_button.pack(side='left')
        self.encode_button=ttk.Button(footer,text='Encoder la vidéo',command=self.encode);self.encode_button.pack(side='right')
        ttk.Button(footer,text='Ouvrir le dossier',command=self.open_output).pack(side='right',padx=8)
        self.status=tk.StringVar(value='Prêt. Commencez par un essai de 5 secondes.')
        ttk.Label(shell,textvariable=self.status,wraplength=700).pack(anchor='w',pady=(8,4))
        self.log=ScrolledText(shell,height=5,wrap='word',font=('Consolas',9));self.log.pack(fill='x')
        self.status_key='Prêt. Commencez par un essai de 5 secondes.';self.status_suffix=''
        self.about_french=self.about_view.get('1.0','end-1c')
        self.static_texts=[]
        def remember(widget):
            if 'text' in widget.keys() and not ('textvariable' in widget.keys() and widget.cget('textvariable')):
                value=str(widget.cget('text'))
                if value:self.static_texts.append((widget,value))
            for child in widget.winfo_children():remember(child)
        remember(shell)
        self.tab_texts=[self.book.tab(i,'text') for i in range(3)]
        self.preset('stf')
        try:saved=json.loads(self.config_path.read_text(encoding='utf-8')).get('language','fr')
        except (OSError,ValueError):saved='fr'
        self.set_language(saved if saved in ('fr','en') else 'fr',persist=False)
        app.protocol('WM_DELETE_WINDOW',self.close);app.after(150,self.poll)

    def tr(self,text):
        return translate(text,self.lang)

    def set_status(self,key,suffix=''):
        self.status_key=key;self.status_suffix=suffix
        self.status.set(self.tr(key)+suffix)

    def set_language(self,language,persist=True):
        previous=self.lang;self.lang=language
        self.language.set('English' if language=='en' else 'Français')
        self.app.title(f'ST Vidéo {VERSION} — '+('Atari ST / STF / STE encoder' if language=='en' else 'Encodeur Atari ST / STF / STE'))
        for widget,original in self.static_texts:widget.configure(text=self.tr(original))
        for var,combo,options in self.option_widgets:
            code=option_code(options,var.get())
            combo.configure(values=[self.tr(label) for label in options])
            var.set(next(self.tr(label) for label,value in options.items() if value==code))
        for i,text in enumerate(self.tab_texts):self.book.tab(i,text=self.tr(text))
        guide=ROOT/'docs'/('GUIDE-STF.en.txt' if language=='en' else 'GUIDE-STF.txt')
        self.replace_document(self.guide_view,guide.read_text(encoding='utf-8') if guide.exists() else self.tr('Consultez le README fourni avec l’application.'))
        self.replace_document(self.about_view,ABOUT_EN.format(version=VERSION) if language=='en' else self.about_french)
        self.update_profile_note();self.update_rate();self.set_status(self.status_key,self.status_suffix)
        if persist:
            try:
                self.config_path.parent.mkdir(parents=True,exist_ok=True)
                self.config_path.write_text(json.dumps({'language':language}),encoding='utf-8')
            except OSError:pass

    def replace_document(self,view,text):
        position=view.yview()[0]
        view.configure(state='normal');view.delete('1.0','end');view.insert('1.0',text)
        view.configure(state='disabled');view.yview_moveto(position)

    def entry(self,parent,label,var,command):
        ttk.Label(parent,text=label).pack(anchor='w',pady=(3,0))
        row=ttk.Frame(parent);row.pack(fill='x',pady=(3,7))
        ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text='Parcourir…',command=command).pack(side='left',padx=(8,0))

    def choice(self,parent,label,var,values):
        row=ttk.Frame(parent);row.pack(fill='x',pady=4)
        ttk.Label(row,text=label).pack(anchor='w')
        combo=ttk.Combobox(row,textvariable=var,values=list(values),state='readonly')
        combo.pack(fill='x',pady=(3,0))
        if isinstance(values,dict):self.option_widgets.append((var,combo,values))

    def document(self,parent,text):
        view=ScrolledText(parent,wrap='word',font=('Segoe UI',11),padx=10,pady=10)
        view.insert('1.0',text);view.configure(state='disabled');view.pack(fill='both',expand=True)
        return view

    def preset(self,mode):
        self.profile_mode=mode
        self.quality.set(self.tr('Palette ST optimisée'));self.dither.set(self.tr('Trame fixe (stable)'))
        self.scene_cuts.set(True);self.audio_filter.set(self.tr('Léger'));self.normalize.set(True)
        self.fps.set('12.5' if mode=='stf' else '25')
        self.audio_codec.set(self.tr('Réglage audio optimisé pour STF (plus lent)' if mode=='stf' else 'Audio optimisé pour STE'))
        self.update_profile_note()

    def update_profile_note(self):
        mode=self.profile_mode
        self.profile_note.configure(text=self.tr('STF / ACSI : 12,5 images/s, trame fixe, palette optimisée et audio STF. Ce réglage a fonctionné sur le STF du créateur ; le débit dépend de votre stockage.' if mode=='stf' else 'STE : audio DMA et 25 images/s. Le DMA améliore le son, mais ne rend pas le disque plus rapide : choisir 12,5 images/s si nécessaire.'))

    def update_rate(self):
        slow=self.fps.get()=='12.5'
        self.rate_note.configure(text=self.tr('STV : environ 410 ko/s, audio préparé à 8 192 Hz. Conseillé pour commencer sur STF avec stockage ACSI.' if slow else 'STV : environ 819 ko/s, audio préparé à 12 288 Hz. Un débit soutenu avec de la marge est nécessaire ; 25 images/s n’est pas garanti.'))

    def arguments(self,preview):
        if not self.source.get().strip():raise ValueError(self.tr('Choisissez une vidéo ou saisissez une URL.'))
        try:
            start=float(self.start.get() or '0');duration=float(self.duration.get()) if self.duration.get().strip() else None
        except ValueError:raise ValueError(self.tr('Le début et la durée doivent être des nombres en secondes (exemple : 12.5).'))
        if start<0 or (duration is not None and duration<=0):raise ValueError(self.tr('Le début doit être positif ou nul et la durée strictement positive.'))
        output=Path(self.destination.get()).expanduser().resolve()
        if preview:output=output/'APERCU'
        self.active_output=output
        args=[self.source.get().strip(),'-o',str(output),'--name',self.clip_name.get().strip() or 'VIDEO','--start',str(start),
            '--language',self.lang,'--dither',option_code(DITHERS,self.dither.get()),'--stf-fps',self.fps.get(),'--quality',option_code(QUALITIES,self.quality.get()),
            '--dither-strength',str(self.strength.get()),'--audio-codec',option_code(CODECS,self.audio_codec.get()),
            '--audio-filter',option_code(FILTERS,self.audio_filter.get()),'--normalize' if self.normalize.get() else '--no-normalize',
            '--scene-cuts' if self.scene_cuts.get() else '--no-scene-cuts','--sharpness',option_code(SHARPNESS,self.sharpness.get())]
        if preview:args+=['--duration','5']
        elif duration is not None:args+=['--duration',str(duration)]
        if self.video_clean.get():args+=['--video-clean']
        return args

    def encode(self,preview=False):
        if self.busy:return
        try:args=self.arguments(preview)
        except ValueError as error:messagebox.showerror(self.tr('Réglages'),str(error));return
        self.busy=True;self.log.delete('1.0','end');self.set_status('Encodage en cours… Le précalcul audio STF peut prendre du temps.')
        for button in [self.preview_button,self.encode_button]+self.profile_buttons:button.configure(state='disabled')
        threading.Thread(target=self.worker,args=(args,),daemon=True).start()

    def worker(self,args):
        try:
            with tempfile.TemporaryDirectory(prefix='stvideo-worker-') as tmp:
                log=Path(tmp)/'encode.log'
                proc=subprocess.Popen(worker_command(log,args),creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                position=0
                while True:
                    done=proc.poll()
                    if log.exists():
                        with log.open('r',encoding='utf-8',errors='replace') as stream:
                            stream.seek(position);chunk=stream.read();position=stream.tell()
                        if chunk:self.events.put(('log',chunk))
                    if done is not None:break
                    try:proc.wait(timeout=.15)
                    except subprocess.TimeoutExpired:pass
                self.events.put(('done',done))
        except Exception as error:
            self.events.put(('log',str(error)+'\n'));self.events.put(('done',1))

    def poll(self):
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=='log':self.log.insert('end',value);self.log.see('end')
                else:
                    self.busy=False
                    for button in [self.preview_button,self.encode_button]+self.profile_buttons:button.configure(state='normal')
                    self.set_status('Terminé : ',str(self.active_output)) if value==0 else self.set_status('L’encodage a échoué. Consultez le détail ci-dessous.')
        except queue.Empty:pass
        self.app.after(150,self.poll)

    def open_output(self):
        path=Path(self.destination.get()).expanduser();path.mkdir(parents=True,exist_ok=True)
        if os.name=='nt':os.startfile(path)

    def close(self):
        if self.busy:messagebox.showinfo(self.tr('Encodage en cours'),self.tr('Attendez la fin de l’encodage avant de fermer la fenêtre.'));return
        self.app.destroy()

def main():
    app=tk.Tk();EncoderApp(app);app.mainloop()

if __name__=='__main__':main()

# ST Vidéo

[Français](README.md) · **English**

I'm **David Ascenso**. I started this project with my Atari video encoder,
player and real-machine experiments. This version adds a Windows interface,
optimised palettes and improved STF audio. It offers 320 × 200 video,
16 colours from the ST’s 512-colour grid, mono audio and PAL playback
at **12.5 or 25 fps**.

Download the Windows [installer or portable edition](https://github.com/DDRCREW-PROG/STVideo/releases/latest).

## Windows installation

- `STVideo-1.0.1-Setup.exe`: Windows 10/11 x64 installer, for the current
  user, with a Start menu shortcut and an uninstaller.
- `STVideo-1.0.1-Windows-portable.zip`: extract the folder and run `STVideo.exe`.
- `STVideo-1.0.1-sources.zip`: source code, Atari player and build instructions.

Python and FFmpeg are bundled. Choose **English** in the **Langue / Language**
selector at the top of the application. Your language choice is remembered.
The installer also offers French and English.

## Recommended STF settings

Click **Recommended STF / ACSI settings**. This selects:

- **12.5 fps**;
- **Fixed pattern (stable)** dithering;
- **Optimised ST palette**;
- **Optimised STF audio (slower encoding)**;
- Light audio cleanup and quiet-source boost.

“Slower encoding” means additional calculation on the PC, not slow-motion
playback. Start with **Try a 5-second preview**, then test the STV on your
actual Atari before encoding a longer clip. Copy `<NAME>.STV` and the supplied
`STFPLAY.PRG` to Atari storage. Run the player in colour low resolution on PAL.
**Right Shift** opens the file selector; **Escape** exits.

See the integrated **STF guide** tab or [the English guide](docs/GUIDE-STF.en.txt).

## Real-machine results and storage speed

I tested playback on my STF with ACSI/SD storage: 25 fps slows down, while
12.5 fps works well. These results describe my setup; other STF machines
and ACSI interfaces may behave differently.

| STV rate | Sustained file data, excluding delays |
| --- | --- |
| 12.5 fps | 409,600 bytes/s, about 410 kB/s |
| 25 fps | 819,200 bytes/s, about 819 kB/s |

A nominal 800–900 kB/s leaves little headroom at 25 fps. Drivers, latency and
file-system pauses matter. I did not record my STF's RAM size during this test;
emulator tests include 8 MHz and 512 KB. Hatari’s host-folder drive does not
represent physical ACSI throughput.

The film keeps its original duration at 12.5 fps. Audio is prepared at
8,192 Hz, compared with 12,288 Hz at 25 fps. Smoothness depends on motion.

## Audio modes

| Setting | STF | STE |
| --- | --- | --- |
| Optimised STF audio | Continuous, precalculated YM commands (STV3) | Same YM output; no DMA |
| Optimised STE audio | Classic YM playback (STV1) | Automatic DMA PCM output |
| Lightweight YM | Experimental single-write YM (STV2) | Same YM output |

An STF-optimised clip does not switch to DMA on an STE. Encode again using
the STE setting for its cleaner DMA output. The STE still needs sufficient
storage throughput; 12.5 fps can be selected with STE audio too.

The PC does all colour optimisation, filtering and audio preparation. The
68000 player reads native bitplanes and prepared audio rather than decoding
a compressed modern video. Optimisation reduces some YM artefacts, but
does not make STF audio equivalent to the STE DAC.

## Outputs

Existing clips are never overwritten: names receive an automatic numeric
suffix. STV includes its audio. The LAV export is separate and **always
remains at 25 fps**. WAVs, image previews and a JSON report are also generated.
Preview runs use the `APERCU` subfolder.

STV occupies about 24.6 MB/minute at 12.5 fps or 49.2 MB/minute at 25 fps.
The full Windows output folder is larger because of the other exports.
Split long content with Start/Duration before the 2 GiB file limit.
Local files work offline; URL input depends on Internet access and yt-dlp’s
support for the site. No personal clips, emulator or TOS ROM is distributed.

## Build from source

Use Python 3.12 x64 on Windows:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe tools\app.py
.venv\Scripts\python.exe -m unittest discover -s tools -p "test_*.py"
.venv\Scripts\python.exe tools\build_windows.py --inno "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

The supplied Atari binary is in `player/STFPLAY.PRG`; assembly source is in
`src/player.s`. Rebuild it using vasm and `tools/build.ps1 -Assembler <path>`.
The Windows build produces a standalone executable, portable/source ZIPs,
an optional Inno Setup installer and SHA-256 checksums in `dist`.

The template `packaging/github-actions-windows.yml` can build Windows packages after the repository owner installs it in `.github/workflows/`. Development captures,
personal paths, video clips and ROMs are excluded from the source archive.

GPL-2.0-or-later: see [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY.md).
This does not change the rights applying to users’ media. The measured YM
level table is credited to Paulo Simoes and distributed with Hatari.

# Setup on a fresh machine

A `git clone` only gives you the tracked source (notebooks, `tools/local_chat.py`, training
data, README). This guide rebuilds everything that is **not** in git / is machine-local:
the Python venv, the ~6 GB model weights, Ollama + its quantized model, and the
`LocalQwenChat` executable + Start Menu shortcut.

Tested on Windows 11 + Python 3.10 using Git Bash. Commands call the venv interpreter
directly (`.venv/Scripts/python.exe`), so there's nothing to "activate".

## 0. Prerequisites
Windows 10/11, Python 3.10+ on PATH (`python --version`), Git, and `winget`.

## 1. Clone (skip if already cloned)
```bash
git clone https://github.com/andyhudson80/local-llm-lab.git
cd local-llm-lab
```

## 2. Python environment (CPU)
> **Pin torch to 2.6.0+cpu.** The newest torch CPU wheel (2.12) fails to load on this
> hardware with `OSError: [WinError 1114] ... c10.dll` (broken DLL init in that wheel).
> 2.6.0 works. Install torch from the CPU index FIRST, then the rest.
```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
.venv/Scripts/python.exe -m pip install -r requirements.txt
```
Sanity check (expect `2.6.0+cpu` and a transformers 5.x):
```bash
.venv/Scripts/python.exe -c "import torch, transformers; print(torch.__version__, transformers.__version__)"
```

## 3. Register the Jupyter kernel
```bash
.venv/Scripts/python.exe -m ipykernel install --user --name llmlab --display-name "Python (llmlab)"
```

## 4. Run the lab notebook (downloads the ~6 GB model on first run)
```bash
.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=llmlab --ExecutePreprocessor.timeout=3600 \
  notebooks/local_llm_lab.ipynb
```
- First run downloads Qwen2.5-3B (~6 GB) to `~/.cache/huggingface` (cached afterwards).
- CPU generation is slow; a full run is ~10–20 min. The fine-tuned cells (§13/§14) hold two
  model copies (~12 GB RAM) — fine on 16 GB but close.
- `--inplace` writes outputs into the notebook; `git restore notebooks/local_llm_lab.ipynb`
  afterwards if you want it back to the clean committed version.
- §13/§14 only run the fine-tuned path if an adapter exists at
  `models/adapters/qwen2.5-3b-tldr/`; otherwise they skip gracefully. Train one via
  `finetune/colab_finetune.ipynb` on a free Colab GPU, then unzip the result into that folder.

## 5. Ollama fast path (responsive 4-bit chat)
```bash
winget install --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
"$LOCALAPPDATA/Programs/Ollama/ollama.exe" pull qwen2.5:3b   # ~2 GB, one-time
```
Ollama runs a local server on `127.0.0.1:11434` and auto-starts on login. Fully offline once
the model is pulled.

## 6. Build the chat launcher + Start Menu shortcut
```bash
.venv/Scripts/python.exe -m pip install pyinstaller
( cd tools && ../.venv/Scripts/python.exe -m PyInstaller --onefile --console --name LocalQwenChat \
    --distpath ./dist --workpath ./build --specpath ./build local_chat.py )
```
Then create the shortcut (PowerShell):
```powershell
$exe = "$PWD\tools\dist\LocalQwenChat.exe"
$lnk = Join-Path ([Environment]::GetFolderPath('Programs')) "Local Qwen Chat.lnk"
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath = $exe; $s.WorkingDirectory = (Split-Path $exe); $s.Save()
```
Search "Local Qwen Chat" in the Start menu (right-click → Pin to Start). One conversation per
window; `/reset` clears it; `/exit` quits. The exe is gitignored — rebuild it per machine.

## Gotchas seen on this project
- **torch:** pin `2.6.0+cpu`; the latest wheel crashes with WinError 1114 (step 2).
- **transformers must be 5.x.** A stale *global* Python here had transformers 4.24 / torch 1.12 —
  never use it; always use the project `.venv`.
- **Anaconda on PATH** can shadow the venv and load conflicting DLLs. If a torch/notebook
  command throws odd DLL or encoding errors, strip anaconda from PATH for that command.
- **Rebuilding the exe:** stop any running instance first or the file is locked —
  `powershell -c "Stop-Process -Name LocalQwenChat -Force -ErrorAction SilentlyContinue"`.
- **Colab fine-tuning** (`finetune/colab_finetune.ipynb`): installs Unsloth from PyPI and pins
  `transformers<=5.5.0` + `trl<=0.24.0` so a modern Unsloth resolves with the
  `processing_class` / `SFTConfig` API. If you hit stale-package errors, do
  **Runtime → Disconnect and delete runtime** and re-run from the top.

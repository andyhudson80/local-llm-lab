# Local LLM Lab — notes for Claude

Runs Qwen2.5-3B-Instruct locally on CPU. Three paths: the `transformers` notebook
(`notebooks/local_llm_lab.ipynb`), the Ollama 4-bit fast path (`tools/local_chat.py` →
`LocalQwenChat.exe`), and Colab LoRA fine-tuning (`finetune/colab_finetune.ipynb`).

## Fresh-machine setup
Follow **[SETUP.md](SETUP.md)** to rebuild everything that is gitignored / machine-local:
the `.venv`, the ~6 GB model weights, Ollama + its model, and the chat exe + Start Menu
shortcut. A clone alone only brings the tracked source.

## Key gotchas (don't relearn these)
- Always use the project **`.venv`**, never the global Python (it has ancient
  torch 1.12 / transformers 4.24).
- **Pin `torch==2.6.0+cpu`** — the latest CPU wheel fails to load with
  `WinError 1114 ... c10.dll` on this hardware.
- **transformers must be 5.x** for the notebook (`dtype=` arg, `apply_chat_template(..., return_dict=True)`).
- **Anaconda is on PATH** and can load conflicting DLLs; strip it from PATH for torch/notebook
  commands if you see odd DLL/encoding errors.
- After editing `tools/local_chat.py`, **rebuild the exe** with PyInstaller and stop any
  running `LocalQwenChat.exe` first (it locks the file).
- The committed notebooks are kept **output-free**; run to a temp file or `git restore` after
  executing if you don't want outputs committed.

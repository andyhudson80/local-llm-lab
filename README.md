# Local LLM Lab

A hands-on lab for **running a real open-source LLM on a regular laptop** (CPU-only), understanding how
it works by looking through the code, and experimenting with **fine-tuning**.

The model is **[Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)** — a genuinely
capable ~3-billion-parameter open model that's small enough to run on 16 GB of RAM, and not gated behind
a license signup.

> **This is a learning lab, not a frontier-model replacement.** A 3B model running on a CPU will answer
> basic questions, summarise, and chat, but it will be slow and will sometimes be confidently wrong.
> That's expected — watching *where* it breaks is part of the point.

## The three paths

| Path | Tool | Speed | Use it to... |
|------|------|-------|--------------|
| **Understand** | Hugging Face `transformers` | Slow (CPU) | Look inside: tokenizer, architecture, logits, the generation loop |
| **Chat (fast)** | [Ollama](https://ollama.com) | Fast | Actually use the model interactively day-to-day |
| **Fine-tune** | Google Colab (free GPU) | — | Train a LoRA adapter, then run it locally |

The **main notebook**, [`notebooks/local_llm_lab.ipynb`](notebooks/local_llm_lab.ipynb), walks through
all of this cell by cell. Start there.

## Your hardware (what to expect)

Built and tested on: **Intel Core i7-1250U, 16 GB RAM, integrated Intel Iris Xe (no NVIDIA GPU).**

- The 3B model loaded in `transformers` uses **bfloat16 (~6 GB RAM)**. It works, but expect only a
  **few tokens per second** on CPU. Keep generations short while exploring.
- For responsive chatting, use **Ollama**, which runs a 4-bit quantized version (~2 GB) and is much
  faster.
- No CUDA GPU means fine-tuning happens **on Colab**, not locally (see [`finetune/`](finetune/)).

## Setup

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install PyTorch (CPU build) first, then the rest
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 3. Register a Jupyter kernel for this env
python -m ipykernel install --user --name local-llm-lab --display-name "Local LLM Lab (.venv)"

# 4. Launch Jupyter and open notebooks/local_llm_lab.ipynb
jupyter notebook
```

The first run of the model-loading cell downloads ~6 GB of weights from Hugging Face (cached afterwards).

### Optional: Ollama (the fast chat path)

1. Install from [ollama.com](https://ollama.com/download).
2. Pull and run the model:
   ```powershell
   ollama run qwen2.5:3b
   ```
3. It also serves a local API on `http://localhost:11434` — the notebook has a cell that uses it.

## Fine-tuning

See [`finetune/README.md`](finetune/README.md). In short: edit `finetune/data/train.jsonl` (easiest via
the notebook), run `finetune/colab_finetune.ipynb` on a free Colab GPU, download the adapter into
`models/adapters/`, then load it locally from the main notebook.

## Project layout

```
local-llm-lab/
├── README.md                     # you are here
├── requirements.txt
├── notebooks/
│   └── local_llm_lab.ipynb       # ★ main notebook — start here
├── finetune/
│   ├── colab_finetune.ipynb      # QLoRA training (run on Colab)
│   ├── data/train.jsonl          # your fine-tuning examples
│   └── README.md
└── models/                       # downloaded adapters (gitignored)
```

## License / attribution

Qwen2.5 is released by Alibaba Cloud under the Qwen license. This lab is for personal learning.

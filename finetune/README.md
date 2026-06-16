# Fine-tuning workflow (QLoRA on Google Colab)

Your laptop has no NVIDIA GPU, so we **train on a free Colab GPU** and then run the result locally.
This is the standard, recommended workflow — fine-tuning is GPU-hungry, but the resulting adapter is
tiny (a few MB) and runs fine on your CPU.

## What you're training

A **LoRA adapter** for `Qwen2.5-3B-Instruct`. LoRA (Low-Rank Adaptation) freezes the original model
and trains a small set of extra weights "on top". QLoRA is the same idea but the base model is loaded
in 4-bit to save memory, which is what lets it fit on a free Colab T4.

**Important expectation:** fine-tuning teaches **style, tone, and format** far more reliably than it
teaches **new facts**. The sample dataset here teaches the model to always end answers with a
`TL;DR:` line — an effect you can clearly see before vs. after.

## Step by step

1. **Edit your data.** Add examples to [`data/train.jsonl`](data/train.jsonl). One JSON object per line,
   each with a `messages` list (a user turn + an assistant turn). The easiest way to add examples is the
   "Build your dataset" cell in [`../notebooks/local_llm_lab.ipynb`](../notebooks/local_llm_lab.ipynb).

2. **Open the Colab notebook.** Upload [`colab_finetune.ipynb`](colab_finetune.ipynb) to
   [Google Colab](https://colab.research.google.com/), or open it from GitHub once this repo is pushed
   (File → Open notebook → GitHub).

3. **Set the runtime to GPU.** In Colab: Runtime → Change runtime type → T4 GPU.

4. **Run the cells top to bottom.** You'll be prompted to upload your `train.jsonl`. Training a few
   hundred steps on a small dataset takes only a few minutes on a T4.

5. **Download the adapter.** The last cell zips the adapter and downloads it. Unzip it into
   `models/adapters/qwen2.5-3b-tldr/` in this project (create the folder if needed).

6. **Run it locally.** Back in the main notebook, the "Run the fine-tuned model locally" cell loads the
   base model + your adapter with `peft` and compares output before vs. after fine-tuning.

## Data format

```json
{"messages": [{"role": "user", "content": "What is the capital of France?"}, {"role": "assistant", "content": "The capital of France is Paris.\n\nTL;DR: Paris."}]}
```

- One object **per line** (this is JSON Lines, not a JSON array).
- Aim for at least ~20-50 examples for a noticeable effect; the 6 seed examples are just a starting point.
- Keep the style consistent — consistency is what the model picks up.

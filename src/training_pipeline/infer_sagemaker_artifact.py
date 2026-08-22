import argparse
from pathlib import Path


ALPACA_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response:
{}"""


def run_inference(
    adapter_path: Path,
    prompt: str,
    max_new_tokens: int,
) -> None:
    import torch
    from peft import PeftConfig, PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter path does not exist: {adapter_path}")

    config = PeftConfig.from_pretrained(adapter_path)

    # The SageMaker adapter was trained from "unsloth/tinyllama-bnb-4bit".
    # That repository is a 4-bit bitsandbytes/Unsloth packaging of TinyLlama,
    # which is appropriate on SageMaker's CUDA GPU but awkward to load on a
    # local Mac/MPS machine. For this local smoke test, load the regular
    # TinyLlama checkpoint instead and attach the LoRA adapter to it.
    #
    # This works because the LoRA adapter stores small weight deltas for named
    # TinyLlama/Llama modules such as q_proj, k_proj, v_proj, o_proj, gate_proj,
    # up_proj, and down_proj. As long as the replacement base has the same
    # architecture/module layout, PEFT can apply those adapter weights. Do not
    # swap this to a different model family such as Mistral, Qwen, or Llama 3.
    base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    if torch.cuda.is_available():
        device = "cuda"
        torch_dtype = torch.bfloat16
    elif torch.backends.mps.is_available():
        device = "mps"
        torch_dtype = torch.float16
    else:
        device = "cpu"
        torch_dtype = torch.float32

    print(f"Loading base model: {base_model_name}")
    print(f"Loading adapter: {adapter_path}")
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(model, adapter_path)
    model.to(device)
    model.eval()

    text = ALPACA_TEMPLATE.format(prompt, "")
    inputs = tokenizer([text], return_tensors="pt").to(device)

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    with torch.inference_mode():
        model.generate(
            **inputs,
            streamer=streamer,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=Path("artifacts/sagemaker/output_sft/checkpoint-1"),
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Write a paragraph to introduce supervised fine-tuning.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=160)
    args = parser.parse_args()

    run_inference(
        adapter_path=args.adapter_path,
        prompt=args.prompt,
        max_new_tokens=args.max_new_tokens,
    )

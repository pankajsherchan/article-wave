from typing import Any, Optional

from transformers import TextStreamer
from download_dataset import DatasetClient

ALPACA_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response:
{}"""
def format_samples_sft(examples: dict, eos_token: str = "") -> dict:
    text = []

    for instruction, output in zip(
        examples["instruction"],
        examples["content"],
        strict=False,
    ):
        message = ALPACA_TEMPLATE.format(instruction, output) + eos_token
        text.append(message)

    return {"text": text}


def load_model(
    model_name: str,
    max_seq_length: int,
    load_in_4bit: bool,
    lora_rank: int,
    lora_alpha: int,
    lora_dropout: float,
    target_modules: list[str],
    chat_template: str,
) -> tuple[Any, Any]:

    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template


    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
    )

    tokenizer = get_chat_template(
        tokenizer,
        chat_template=chat_template,
    )

    return model, tokenizer



def finetune(
    model_name: str,
    output_dir: str,
    dataset_id: str,
    max_seq_length: int = 2048,
    load_in_4bit: bool = True,
    lora_rank: int = 32,
    lora_alpha: int = 32,
    lora_dropout: float = 0.0,
    target_modules: list[str] | None = None,
    chat_template: str = "chatml",
    learning_rate: float = 3e-4,
    num_train_epochs: int = 3,
    per_device_train_batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    is_dummy: bool = False,
):
    from datasets import concatenate_datasets, load_dataset
    from transformers import TrainingArguments
    from trl import SFTTrainer
    from unsloth import is_bfloat16_supported

    if target_modules is None:
        target_modules = [
            "q_proj",
            "k_proj",
            "v_proj",
            "up_proj",
            "down_proj",
            "o_proj",
            "gate_proj",
        ]

    model, tokenizer = load_model(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        lora_rank=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
        chat_template=chat_template,
    )

    eos_token = tokenizer.eos_token


    dataset_client = DatasetClient()
    custom_dataset = dataset_client.download_dataset(dataset_id=dataset_id, split="train")

    if is_dummy:
        num_train_epochs = 1
        dummy_size = min(20, len(custom_dataset))
        custom_dataset = custom_dataset.select(range(dummy_size))
        print(f"Dummy mode: using {dummy_size} samples for {num_train_epochs} epoch.")

    dataset = custom_dataset

    dataset = dataset.map(
        lambda examples: format_samples_sft(examples, eos_token=eos_token),
        batched=True,
        remove_columns=dataset.column_names,
    )


    dataset = dataset.train_test_split(test_size=0.05)
    print("Training dataset example:")
    print(dataset["train"][0]["text"][:1000])

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=not is_dummy,
        args=TrainingArguments(
            learning_rate=learning_rate,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            per_device_eval_batch_size=per_device_train_batch_size,
            warmup_steps=10,
            output_dir=output_dir,
            report_to="comet_ml",
            seed=0,
        ),
    )

    trainer.train()

    return model, tokenizer

def preview_dataset_formatting(
    dataset_id: str,
    split: str = "train",
    eos_token: str = "",
) -> None:
    dataset_client = DatasetClient()
    dataset = dataset_client.download_dataset(dataset_id=dataset_id, split=split)

    formatted_dataset = dataset.map(
        lambda examples: format_samples_sft(examples, eos_token=eos_token),
        batched=True,
        remove_columns=dataset.column_names,
    )

    print("Original dataset:")
    print(dataset)
    print(dataset[0])

    print("\nFormatted dataset:")
    print(formatted_dataset)
    print(formatted_dataset[0]["text"][:1000])

def inference(
    model: Any,
    tokenizer: Any,
    prompt: str = "Write a paragraph to introduce supervised fine-tuning.",
    max_new_tokens: int = 256
) -> None:
    from unsloth import FastLanguageModel, is_bfloat16_supported

    model = FastLanguageModel.for_inference(model)
    message = ALPACA_TEMPLATE.format(prompt, "")
    inputs = tokenizer([message], return_tensors="pt").to("cuda")

    text_streamer = TextStreamer(tokenizer)

    model.generate(
        **inputs, streamer=text_streamer, max_new_tokens=max_new_tokens, use_cache=True
    )

def save_model(
    model: Any,
    tokenizer: Any,
    output_dir: str,
    push_to_hub: bool = False,
    repo_id: Optional[str] = None,
) -> None:
    model.save_pretrained_merged(output_dir, tokenizer, save_method="merged_16bit")

    if push_to_hub and repo_id:
        print(f"Saving model to '{repo_id}'")  # noqa
        model.push_to_hub_merged(repo_id, tokenizer, save_method="merged_16bit")


if __name__ == "__main__":
    import argparse
    import os
    from pathlib import Path

    def str_to_bool(value: str) -> bool:
        return str(value).lower() in {"true", "1", "yes"}

    parser = argparse.ArgumentParser()

    parser.add_argument("--base_model_name", type=str, default="meta-llama/Llama-3.1-8B")
    parser.add_argument("--dataset_id", type=str, required=True)
    parser.add_argument("--num_train_epochs", type=int, default=3)
    parser.add_argument("--per_device_train_batch_size", type=int, default=2)
    parser.add_argument("--learning_rate", type=float, default=3e-4)
    parser.add_argument("--model_output_huggingface_workspace", type=str)
    parser.add_argument("--is_dummy", type=str_to_bool, default=False)

    parser.add_argument("--output_data_dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--model_dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--n_gpus", type=str, default=os.environ["SM_NUM_GPUS"])

    args = parser.parse_args()

    output_dir_sft = Path(args.model_dir) / "output_sft"

    model, tokenizer = finetune(
        model_name=args.base_model_name,
        output_dir=str(output_dir_sft),
        dataset_id=args.dataset_id,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        learning_rate=args.learning_rate,
        is_dummy=args.is_dummy,
    )

    inference(model, tokenizer)

    # base_model_suffix = args.base_model_name.split("/")[-1]
    # sft_output_model_repo_id = (
    #     f"{args.model_output_huggingface_workspace}/ArticleWave-{base_model_suffix}"
    # )

    # save_model(
    #     model,
    #     tokenizer,
    #     "model_sft",
    #     push_to_hub=True,
    #     repo_id=sft_output_model_repo_id,
    # )

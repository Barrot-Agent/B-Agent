import os
import traceback
from datetime import datetime

class EndpointHandler:
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()
        self.status = "online"

        self.gemma_model = None
        self.gemma_tokenizer = None
        self.gemma_id = os.getenv("BARROT_GEMMA_MODEL", "google/gemma-4-E2B-it")

        self.qwen_model = None
        self.qwen_processor = None
        self.qwen_id = os.getenv("BARROT_QWEN_MODEL", "Qwen/Qwen2-VL-2B-Instruct")

    def _ensure_gemma(self):
        if self.gemma_model is not None and self.gemma_tokenizer is not None:
            return
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.gemma_tokenizer = AutoTokenizer.from_pretrained(self.gemma_id)
        self.gemma_model = AutoModelForCausalLM.from_pretrained(
            self.gemma_id,
            torch_dtype="auto",
            device_map="auto"
        )

    def _ensure_qwen(self):
        if self.qwen_model is not None and self.qwen_processor is not None:
            return
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
        self.qwen_processor = AutoProcessor.from_pretrained(self.qwen_id)
        self.qwen_model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.qwen_id,
            torch_dtype="auto",
            device_map="auto"
        )

    def _run_gemma(self, prompt):
        import torch
        self._ensure_gemma()
        messages = [
            {"role": "system", "content": "You are BARROT-Ω reasoning core."},
            {"role": "user", "content": prompt}
        ]
        inputs = self.gemma_tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.gemma_model.device)

        with torch.no_grad():
            outputs = self.gemma_model.generate(
                inputs,
                max_new_tokens=192,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        text = self.gemma_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {
            "backend": "gemma4",
            "model": self.gemma_id,
            "response": text,
            "timestamp": self.timestamp,
            "status": "gemma_live"
        }

    def _run_qwen(self, prompt):
        import torch
        self._ensure_qwen()
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ],
            }
        ]
        text_prompt = self.qwen_processor.apply_chat_template(
            conversation,
            add_generation_prompt=True
        )
        inputs = self.qwen_processor(
            text=[text_prompt],
            padding=True,
            return_tensors="pt"
        ).to(self.qwen_model.device)

        with torch.no_grad():
            generated_ids = self.qwen_model.generate(**inputs, max_new_tokens=192)
        output_text = self.qwen_processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        return {
            "backend": "qwen_vl",
            "model": self.qwen_id,
            "response": output_text,
            "timestamp": self.timestamp,
            "status": "qwen_live"
        }

    def __call__(self, payload):
        inputs = payload.get("inputs", "no input")
        params = payload.get("parameters", {})
        backend = params.get("backend", "gemma4")

        try:
            if backend == "qwen_vl":
                return self._run_qwen(inputs)
            if backend == "gemma4":
                return self._run_gemma(inputs)
            return {
                "backend": "mrp",
                "model": "barrot_mrp",
                "response": f"MRP Engine: {inputs}",
                "frames": params.get("frames", []),
                "timestamp": self.timestamp,
                "status": "mrp_online"
            }
        except Exception as e:
            return {
                "backend": backend,
                "response": f"{backend} failure: {type(e).__name__}: {e}",
                "trace": traceback.format_exc(limit=2),
                "timestamp": self.timestamp,
                "status": "backend_error"
            }

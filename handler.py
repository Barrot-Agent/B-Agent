import os
import traceback
from datetime import datetime

class EndpointHandler:
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()
        self.status = "online"
        self._model = None
        self._tokenizer = None
        self._load_error = None
        self.model_id = os.getenv("BARROT_GEMMA_MODEL", "google/gemma-4-E2B-it")

    def _ensure_model(self):
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)

            dtype = "auto"
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=dtype,
                device_map="auto"
            )
        except Exception as e:
            self._load_error = f"{type(e).__name__}: {e}"
            raise

    def _gemma_generate(self, prompt):
        import torch

        self._ensure_model()

        messages = [
            {
                "role": "system",
                "content": "You are BARROT-Ω running on Gemma 4. Be concise, accurate, and operational."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            inputs = self._tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt"
            )

            if hasattr(self._model, "device"):
                inputs = inputs.to(self._model.device)

            with torch.no_grad():
                outputs = self._model.generate(
                    inputs,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )

            text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            if prompt in text:
                text = text.split(prompt, 1)[-1].strip()

            return {
                "model": self.model_id,
                "response": text.strip(),
                "timestamp": self.timestamp,
                "status": "gemma_live"
            }

        except Exception as e:
            return {
                "model": self.model_id,
                "response": f"Gemma generation failed: {type(e).__name__}: {e}",
                "trace": traceback.format_exc(limit=2),
                "timestamp": self.timestamp,
                "status": "gemma_error"
            }

    def __call__(self, payload):
        inputs = payload.get("inputs", "no input")
        params = payload.get("parameters", {})

        if isinstance(inputs, str) and (
            "gemma" in inputs.lower()
            or "gemma 4" in inputs.lower()
            or params.get("backend") == "gemma4"
        ):
            try:
                return self._gemma_generate(inputs)
            except Exception as e:
                return {
                    "model": self.model_id,
                    "response": f"Gemma load failed: {type(e).__name__}: {e}",
                    "timestamp": self.timestamp,
                    "status": "gemma_load_error"
                }

        return {
            "model": "barrot_mrp",
            "response": f"MRP Engine: {inputs}",
            "frames": params.get("frames", []),
            "timestamp": self.timestamp,
            "status": "mrp_online"
        }

import json
import time
from typing import Any, Dict, List, Optional

import requests


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "codegemma:7b"
    ):
        self.base_url = base_url
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response from the model"""

        start_time = time.time()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,  # TODO: Find the user experience when stream is set to True
        }

        if system_prompt:
            payload["system_prompt"] = system_prompt

        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()

            elapsed_time = time.time() - start_time
            print(f"LLM generation completed in {elapsed_time:.2f}s")

            return result.get("response", "")

        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            raise

    def structured_generation(
        self,
        prompt: str,
        output_format: Dict[str, Any],
        system_prompt: Optional[str] = None,
        max_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """Generate a structured response confirming to the specified format"""

        if system_prompt is None:
            system_prompt = (
                "You are a code analysis assistant. Analyze the code and provide structured output"
                "according to the requested format. Be precise and thorough."
            )

        format_instructions = (
            f"Your response should be a valid JSON that confirm to this structure: {json.dumps(output_format, indent=2)}\n"
            "Do not include any explanations, only output the JSON object"
        )

        full_prompt = f"{prompt}\n\n{format_instructions}"

        response = None
        for attempt in range(max_attempts):
            try:
                response = self.generate(full_prompt, system_prompt)
                json_str = response.strip()

                # Handle potential markdown code blocks
                if json_str.startswith("```json"):
                    json_str = json_str.split("```json")[1]
                if json_str.endswith("```"):
                    json_str = json_str.split("```")[0]

                result = json.loads(json_str.strip())
                return result
            except json.JSONDecodeError as e:
                if attempt == max_attempts - 1:
                    print(f"Failed to parse JSON after {max_attempts} attempts: {e}")
                    print(f"Raw response: {response}")
                    raise
                print(f"Attempt {attempt + 1} failde to parse JSON. Retrying ...")

    def is_available(self) -> bool:
        """Check if ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model.get("name") for model in models]
        except requests.exceptions.RequestException as e:
            print(f"Error listing the models: {e}")
            return []

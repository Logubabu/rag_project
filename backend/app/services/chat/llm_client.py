import httpx
from app.core.config import settings

class LLMClient:
    def __init__(self):
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.hf_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.system_prompt = (
            "You are an AI assistant.\n"
            "Answer ONLY using the supplied context.\n"
            "Never hallucinate.\n"
            "Always include source filenames.\n"
            "If the answer does not exist, reply\n"
            "\"I couldn't find that information in the uploaded documents.\""
        )
        
    async def generate_response(self, question: str, context: str) -> str:
        provider = settings.LLM_PROVIDER.lower()
        
        prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        
        if provider == "groq" and settings.GROQ_API_KEY:
            try:
                return await self._call_groq(prompt)
            except httpx.HTTPStatusError as e:
                print(f"Groq failed: {e}. Details: {e.response.text}. Falling back to HF...")
                if settings.HF_API_KEY:
                    return await self._call_hf(prompt)
                raise
            except Exception as e:
                print(f"Groq failed with general error: {e}. Falling back to HF...")
                if settings.HF_API_KEY:
                    return await self._call_hf(prompt)
                raise
        elif provider == "hf" or settings.HF_API_KEY:
            return await self._call_hf(prompt)
        else:
            raise ValueError("No valid LLM configuration found.")

    async def _call_groq(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.groq_api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_hf(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        # For HF Instruct models, we format with [INST]
        formatted_prompt = f"<s>[INST] {self.system_prompt}\n\n{prompt} [/INST]"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.hf_api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            return str(data)

llm_client = LLMClient()

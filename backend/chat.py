import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import config
from vector_store import vector_store

class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            print(f"Downloading/Loading GGUF LLM model (Torch-free)...")
            
            repo_id = "HuggingFaceTB/SmolLM2-360M-Instruct-GGUF"
            filename = "smollm2-360m-instruct-q4_k_m.gguf"
            
            # This downloads the file to the local HuggingFace cache and returns the path
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
            
            cls._instance.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                verbose=False
            )
        return cls._instance

    def generate_answer(self, query: str) -> dict:
        results = vector_store.search(query, top_k=config.TOP_K)
        
        if not results:
            return {
                "answer": "I couldn't find that information in the uploaded documents.",
                "sources": []
            }
            
        context = "\n\n".join([f"Source: {res['filename']}\nContent: {res['text']}" for res in results])
        
        prompt = f"""<|im_start|>system
You are an AI assistant. Answer ONLY from the provided context. If the answer does not exist, respond exactly with: "I couldn't find that information in the uploaded documents." Always include the source filename in your answer if you find the information.<|im_end|>
<|im_start|>user
Context:
{context}

Question: {query}<|im_end|>
<|im_start|>assistant
"""
        
        try:
            output = self.llm(
                prompt,
                max_tokens=256,
                temperature=0.1,
                stop=["<|im_end|>"]
            )
            answer = output["choices"][0]["text"].strip()
            
            sources = [{"filename": res['filename'], "score": res['score']} for res in results]
            
            # Remove duplicate sources
            unique_sources = []
            seen_filenames = set()
            for s in sources:
                if s["filename"] not in seen_filenames:
                    unique_sources.append(s)
                    seen_filenames.add(s["filename"])
                    
            return {
                "answer": answer,
                "sources": unique_sources
            }
        except Exception as e:
            print(f"Error generating answer: {e}")
            return {
                "answer": "An error occurred while generating the answer.",
                "sources": []
            }

llm_service = LLMService()

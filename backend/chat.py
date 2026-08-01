from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import config
from vector_store import vector_store

class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
            print(f"Loading LLM model {config.LLM_MODEL_NAME} on {cls._instance.device}...")
            
            cls._instance.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL_NAME)
            cls._instance.model = AutoModelForCausalLM.from_pretrained(
                config.LLM_MODEL_NAME, 
                torch_dtype=torch.float16 if cls._instance.device != "cpu" else torch.float32,
                device_map=cls._instance.device
            )
            
            cls._instance.pipe = pipeline(
                "text-generation",
                model=cls._instance.model,
                tokenizer=cls._instance.tokenizer,
                max_new_tokens=256,
                temperature=0.1,
                do_sample=True,
                repetition_penalty=1.1
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
        
        prompt = f"""You are an AI assistant. Answer ONLY from the provided context. If the answer does not exist, respond exactly with: "I couldn't find that information in the uploaded documents." Always include the source filename in your answer if you find the information.

Context:
{context}

Question: {query}
Answer:"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        try:
            outputs = self.pipe(formatted_prompt)
            generated_text = outputs[0]["generated_text"]
            # Extract the actual answer part
            answer = generated_text.split("<|im_start|>assistant")[-1].strip()
            
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

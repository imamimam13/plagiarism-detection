import os
import json
from typing import Dict, Any, Optional
from app.core.config import settings

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

class AIDetectionService:
    def __init__(self):
        self.classifier = None
        self.provider = settings.AI_PROVIDER.lower()
        self.enabled = False
        
        # Check if external provider is configured
        if self.provider in ["openai", "openrouter", "ollama"]:
            if self.provider == "openai" and settings.OPENAI_API_KEY:
                self.enabled = True
            elif self.provider == "openrouter" and settings.OPENROUTER_API_KEY:
                self.enabled = True
            elif self.provider == "ollama" and settings.OLLAMA_BASE_URL:
                self.enabled = True
            
            if self.enabled:
                print(f"Using external AI Provider: {self.provider}")
                return

        # Fallback to local model if properly configured and not Vercel
        if HAS_TRANSFORMERS and not os.getenv("VERCEL"):
            try:
                # We use a pipeline for text classification
                # Note: This will download the model on first run (approx 500MB)
                model_name = "roberta-base-openai-detector"
                self.classifier = pipeline("text-classification", model=model_name)
                self.enabled = True
                print("Using local HuggingFace model for AI detection")
            except Exception as e:
                print(f"Failed to load AI detection model: {e}")

    def _get_client(self):
        """Get the appropriate OpenAI-compatible client"""
        from openai import OpenAI
        
        if self.provider == "openrouter":
            return OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            ), "google/gemma-7b-it" # Default free model or configurable
            
        elif self.provider == "ollama":
            return OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama", # required but unused
            ), "mistral" # Default ollama model
            
        else: # OpenAI
            return OpenAI(api_key=settings.OPENAI_API_KEY), "gpt-3.5-turbo"

    def _detect_with_external_api(self, text: str) -> Dict[str, Any]:
        """Detect AI-generated text using configured External API"""
        try:
            client, model = self._get_client()
            
            prompt = f"""Analyze the following text and determine if it was written by AI or a human.
Respond with ONLY a JSON object with two fields:
- "is_ai": true or false
- "confidence": a number between 0 and 1

Text to analyze:
{text[:2000]}"""
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            content = response.choices[0].message.content
            # Handle potential markdown code block wrapping
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            result = json.loads(content.strip())
            
            return {
                "is_ai": result.get("is_ai", False),
                "score": result.get("confidence", 0.5),
                "confidence": result.get("confidence", 0.5),
                "label": "AI" if result.get("is_ai") else "Human",
                "message": f"Analysis complete ({self.provider})"
            }
        except Exception as e:
            print(f"Error using External API ({self.provider}): {e}")
            return {
                "is_ai": False,
                "score": 0.0,
                "confidence": 0.0,
                "label": "ERROR",
                "message": f"External API error: {str(e)}"
            }

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detects if the text is AI-generated.
        Returns a dictionary with 'is_ai' (bool) and 'score' (float).
        """
        if not self.enabled:
            return {
                "is_ai": False,
                "score": 0.0,
                "confidence": 0.0,
                "label": "UNKNOWN",
                "message": "AI Detection unavailable (Lite Mode or Model missing)"
            }
        
        # Use external API if configured
        if self.provider in ["openai", "openrouter", "ollama"]:
            return self._detect_with_external_api(text)

        # Use local model
        if not self.classifier:
            return {
                "is_ai": False,
                "score": 0.0,
                "confidence": 0.0,
                "label": "UNKNOWN",
                "message": "Local model not available"
            }

        # Chunk text for better detection on long documents
        chunk_size = 1000
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        try:
            results = []
            for chunk in chunks[:5]: # Limit to first 5 chunks for performance
                res = self.classifier(chunk)[0]
                results.append(res)
            
            if not results:
                return {"is_ai": False, "score": 0.0, "confidence": 0.0, "label": "UNKNOWN", "message": "No text to analyze"}

            # Aggregate results (average AI probability)
            ai_scores = []
            for res in results:
                label = res['label']
                score = res['score']
                # 'Fake' usually means AI-generated in these models
                is_ai_chunk = label == 'Fake'
                ai_scores.append(score if is_ai_chunk else (1 - score))
            
            avg_ai_score = sum(ai_scores) / len(ai_scores)
            is_ai = avg_ai_score > 0.5
            
            return {
                "is_ai": is_ai,
                "score": avg_ai_score,
                "confidence": max(ai_scores) if is_ai else (1 - min(ai_scores)),
                "label": "Fake" if is_ai else "Real",
                "message": f"Analysis complete ({len(results)} chunks analyzed)"
            }
        except Exception as e:
            print(f"Error during AI detection: {e}")
            return {
                "is_ai": False,
                "score": 0.0,
                "confidence": 0.0,
                "label": "ERROR",
                "message": str(e)
            }

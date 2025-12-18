"""LLM Interface for Phi-3 via llama.cpp"""
import subprocess
import json
import yaml
from pathlib import Path


class LLMInterface:
    def __init__(self, config_path="agent/config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.binary = self.config['llm']['binary_path']
        self.model = self.config['llm']['model_path']
        self.threads = self.config['llm']['threads']
        self.temp = self.config['llm']['temperature']
        
    def generate(self, prompt, max_tokens=None):
        """Generate completion from Phi-3"""
        if max_tokens is None:
            max_tokens = self.config['llm']['max_tokens']
        
        cmd = [
            self.binary,
            self.model,
            prompt
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"LLM failed: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("LLM generation timeout")
        except Exception as e:
            raise RuntimeError(f"LLM error: {str(e)}")


if __name__ == "__main__":
    # Test the LLM interface
    llm = LLMInterface()
    response = llm.generate("What is 2+2? Answer briefly.")
    print("LLM Response:")
    print(response)

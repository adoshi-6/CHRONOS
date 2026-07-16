from openai import OpenAI
from tools import TOOL_DEFINITIONS

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def generate_response(conversation_history, system_prompt):
    messages = [{"role": "system", "content": system_prompt}] + conversation_history
    
    try:
        # We pass the TOOL_DEFINITIONS schema array straight to the local model
        response = client.chat.completions.create(
            model="qwen2.5-coder", 
            messages=messages,
            tools=TOOL_DEFINITIONS, 
            stream=True
        )
        return response
    except Exception as e:
        print(f"\n[Error communicating with local Ollama: {e}]")
        return None
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Your Hugging Face API Key
HF_API_KEY = "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"

# Load a model from Hugging Face
model_name = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HF_API_KEY)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, use_auth_token=HF_API_KEY)

def get_chatbot_response(user_message):
    """Generate a response from the AI model"""
    input_ids = tokenizer(user_message, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=200)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# Test the chatbot
print(get_chatbot_response("Hello, how are you?"))


#run the model sample
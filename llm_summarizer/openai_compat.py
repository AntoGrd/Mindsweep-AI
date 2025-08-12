import openai

# Wrapper compatible avec openai>=1.0.0 pour chat completions

def chat_completion(messages, model="gpt-5-mini-2025-08-07"):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        #max_tokens=max_tokens,
        #temperature=temperature,
    )
    return response.choices[0].message.content.strip()

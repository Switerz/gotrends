from agent.prompt_loader import load_agent_prompt

prompt = load_agent_prompt()

print(prompt[:3000])
print("\n\nTamanho total do prompt:", len(prompt), "caracteres")
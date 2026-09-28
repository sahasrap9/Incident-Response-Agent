from dotenv import load_dotenv
import os
from hindsight_client import Hindsight
from groq import Groq

load_dotenv()

# Test Hindsight
client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)
client.retain(bank_id="test-bank", content="This is a test memory about incident response.")
results = client.recall(bank_id="test-bank", query="incident response")
print("Hindsight recall result:", [r.text for r in results.results])

# Test Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
completion = groq_client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print("Groq response:", completion.choices[0].message.content)
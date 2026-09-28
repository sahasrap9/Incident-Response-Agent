import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.memory.mental_model import refresh_team_mental_model, get_team_mental_model_content

refresh_team_mental_model()
print("\nRefreshing... this may take a moment.\n")

content = get_team_mental_model_content(wait_for_refresh=True)
print("=== Team-wide Production Reliability Profile ===\n")
print(content)
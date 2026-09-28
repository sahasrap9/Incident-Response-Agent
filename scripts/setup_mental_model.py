import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.memory.mental_model import create_or_get_team_mental_model

mental_model_id = create_or_get_team_mental_model()
print(f"\nMental model ready: {mental_model_id}")
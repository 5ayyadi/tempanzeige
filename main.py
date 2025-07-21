import os
from dotenv import load_dotenv

load_dotenv()

# Example: print a variable from .env
print(os.getenv('MY_VARIABLE', 'Variable not set'))

from dotenv import load_dotenv
import os

def test_environment():
    print("Testing environment variables...")
    load_dotenv()

    # Correct way to check environment variables
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),  # Use the variable name, not the value
        'OPENAI_ORG_ID': os.getenv('OPENAI_ORG_ID'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_DEFAULT_REGION': os.getenv('AWS_DEFAULT_REGION')
    }

    for var_name, value in env_vars.items():
        if value:
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '****'
            print(f"✅ {var_name} is set: {masked_value}")
        else:
            print(f"❌ {var_name} is not set")

if __name__ == "__main__":
    test_environment()
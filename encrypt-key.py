from cryptography.fernet import Fernet

# Generate a key and save it securely (e.g., in an environment variable)
key = Fernet.generate_key()
with open(".encryption_key", "wb") as key_file:
    key_file.write(key)

# Load the key
cipher_suite = Fernet(key)

# Read the contents of .env
with open(".env", "rb") as env_file:
    env_contents = env_file.read()

# Encrypt the .env file
encrypted_env = cipher_suite.encrypt(env_contents)

# Save the encrypted file
with open(".env.encrypted", "wb") as encrypted_env_file:
    encrypted_env_file.write(encrypted_env)
import secrets

# Generate a 256-bit secret key
secret_key = secrets.token_hex(32)  # 32 bytes = 256 bits
print(secret_key)
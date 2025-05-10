import bcrypt

# Sostituisci qui con la password in chiaro che vuoi hashare:
pwd = b"Admin"

# Genera e stampa l'hash
print(bcrypt.hashpw(pwd, bcrypt.gensalt()).decode())


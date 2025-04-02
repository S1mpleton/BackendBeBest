''''shell
# Generate an RSA private key, of size 2048
openssl genrsa -out certs/private.pem 2048
''''

''''shell
# Extract the public key from the pair key of size 2048
openssl rsa -in certs/private.pem -outform PEM -pubout -out certs/public.pem
''''
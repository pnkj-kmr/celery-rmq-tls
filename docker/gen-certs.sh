#!/usr/bin/env bash
# Generate a self-signed CA and server cert for local RabbitMQ TLS dev.
# Idempotent: skips regeneration if certs already exist (use --force to override).
set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")" && pwd)/certs"
FORCE="${1:-}"

if [[ -f "$CERT_DIR/server.crt" && "$FORCE" != "--force" ]]; then
  echo "Certs already exist at $CERT_DIR (pass --force to regenerate)."
  exit 0
fi

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# 1. CA key + self-signed CA cert (10 years)
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
  -subj "/CN=celery-rmq-tls-dev-ca" \
  -out ca.crt

# 2. Server key
openssl genrsa -out server.key 4096

# 3. Server CSR with SAN
cat > server.cnf <<'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions     = v3_req
prompt             = no

[req_distinguished_name]
CN = localhost

[v3_req]
keyUsage         = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName   = @alt

[alt]
DNS.1 = localhost
DNS.2 = rabbitmq
IP.1  = 127.0.0.1
EOF

openssl req -new -key server.key -out server.csr -config server.cnf

# 4. Sign with our CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 825 -sha256 \
  -extfile server.cnf -extensions v3_req

# 5. Permissions: keys 600, certs 644
chmod 600 ca.key server.key
chmod 644 ca.crt server.crt

# 6. Tidy up
rm -f server.csr server.cnf ca.srl

echo "Generated certs in $CERT_DIR:"
ls -la "$CERT_DIR"

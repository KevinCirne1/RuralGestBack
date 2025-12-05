#!/bin/sh

set -e

echo "==> Aplicando migrações do Flask..."

echo "==> Executando flask db upgrade"
flask db upgrade

echo "==> Migrações aplicadas com sucesso!"

# Executa o comando principal do contêiner (o CMD que é o uwsgi)
exec "$@"
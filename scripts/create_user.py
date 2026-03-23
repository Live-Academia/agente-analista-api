#!/usr/bin/env python3
"""CLI para gerar hash bcrypt de senha para uso no AUTH_CONFIG_YAML.

Uso:
    python scripts/create_user.py <senha>

Exemplo:
    python scripts/create_user.py minha-senha-secreta

O hash gerado pode ser colado no AUTH_CONFIG_YAML:

    credentials:
      usernames:
        admin:
          email: admin@empresa.com
          name: Administrador
          password: $2b$12$<hash-aqui>
          roles: [admin]
"""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("Erro: informe a senha como argumento.")
        sys.exit(1)

    try:
        from passlib.context import CryptContext
    except ImportError:
        print("Instale as dependencias: pip install passlib[bcrypt]")
        sys.exit(1)

    password = sys.argv[1]
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash(password)

    print(f"\nHash bcrypt gerado:")
    print(f"  {hashed}")
    print()
    print("Adicione ao AUTH_CONFIG_YAML (variavel de ambiente no Fly.io):")
    print(f"      password: {hashed}")


if __name__ == "__main__":
    main()

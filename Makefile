.PHONY: all run repl test install docker clean help

help:
	@echo "⚡ DevOpsHeroCLI - Comandos de Apoio"
	@echo "  make run       - Inicia a interface TUI completa"
	@echo "  make repl      - Inicia o modo REPL rápido via terminal"
	@echo "  make test      - Executa os testes unitários"
	@echo "  make install   - Configura o ambiente virtual e instala dependências"
	@echo "  make docker    - Constrói e roda a imagem Docker interativa"
	@echo "  make clean     - Remove caches, .venv e arquivos temporários"

install:
	./devopshero.sh --help >/dev/null

run:
	./devopshero.sh

repl:
	./devopshero.sh repl

test:
	@if [ -d ".venv" ]; then \
		.venv/bin/python -m unittest tests/test_simulators.py; \
	else \
		python3 -m unittest tests/test_simulators.py; \
	fi

docker:
	docker compose run --rm devopshero

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

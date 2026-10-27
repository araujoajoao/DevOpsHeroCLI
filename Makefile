.PHONY: all run repl test install docker clean help r s l v d app dmg macos deb install-linux ico

all: run

help:
	@echo "⚡ DevOpsHeroCLI (dh) - Atalhos de Execução Rápida"
	@echo "  make (ou make run) - Inicia a interface visual completa (./dh)"
	@echo "  make r             - Inicia o modo REPL rápido (./dh r)"
	@echo "  make s             - Exibe estatísticas e XP do perfil (./dh s)"
	@echo "  make l             - Lista o catálogo das 80 missões (./dh l)"
	@echo "  make v             - Executa validação de todas as missões (./dh v)"
	@echo "  make d             - Diagnóstico de SO e compatibilidade (./dh d)"
	@echo "  make dmg (ou app)  - Gera instalador macOS (DevOpsHero.dmg na raiz e dist/)"
	@echo "  make deb           - Gera instalador Debian/Ubuntu (.deb) em dist/"
	@echo "  make install-linux - Instala atalho oficial no menu e PATH no Linux"
	@echo "  make test          - Executa a suíte de testes unitários"
	@echo "  make docker        - Executa em contêiner Docker isolado"
	@echo "  make clean         - Limpa arquivos temporários e caches"

install:
	./dh --help >/dev/null

run:
	./dh

r repl:
	./dh r

s stats:
	./dh s

l list:
	./dh l

d doctor:
	./dh d

v verify:
	./dh v

test:
	@if [ -d ".venv" ]; then \
		.venv/bin/python -m unittest discover tests; \
	else \
		python3 -m unittest discover tests; \
	fi

app dmg macos:
	./scripts/build_macos_app.sh

deb:
	python3 scripts/build_linux_deb.py

install-linux:
	./scripts/install_linux.sh

docker:
	docker compose -f docker/docker-compose.yml run --rm devopshero

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete

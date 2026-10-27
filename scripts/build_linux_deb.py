#!/usr/bin/env python3
"""
scripts/build_linux_deb.py - Gera pacote nativo Debian/Ubuntu (.deb) para DevOpsHeroCLI
"""
import io
import os
import sys
import tarfile
import time
from pathlib import Path

def create_ar_archive(members: list[tuple[str, bytes]], output_path: str):
    """
    Gera um arquivo no formato padrão GNU/Debian 'ar' (sem dependências externas).
    Cada membro é uma tupla (nome_arquivo, bytes_conteudo).
    """
    with open(output_path, "wb") as f:
        f.write(b"!<arch>\n")
        for filename, data in members:
            # Header de 60 bytes do formato ar:
            # 16 bytes: nome (terminado com /)
            # 12 bytes: timestamp
            # 6 bytes: owner id
            # 6 bytes: group id
            # 8 bytes: file mode (octal)
            # 10 bytes: tamanho em bytes
            # 2 bytes: magic `\n
            name_field = f"{filename}".ljust(16)[:16]
            mtime_field = str(int(time.time())).ljust(12)[:12]
            uid_field = "0".ljust(6)[:6]
            gid_field = "0".ljust(6)[:6]
            mode_field = "100644".ljust(8)[:8]
            size_field = str(len(data)).ljust(10)[:10]
            header = f"{name_field}{mtime_field}{uid_field}{gid_field}{mode_field}{size_field}`\n".encode("ascii")
            
            f.write(header)
            f.write(data)
            # ar exige alinhamento em 2 bytes
            if len(data) % 2 != 0:
                f.write(b"\n")

def build_deb():
    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    deb_output = dist_dir / "DevOpsHero.deb"

    print("⚡ [Linux Packager] Montando pacote Debian/Ubuntu (.deb)...")

    # 1. debian-binary
    deb_binary = b"2.0\n"

    # 2. control.tar.gz
    control_content = """Package: devopshero
Version: 1.0.0
Section: games
Priority: optional
Architecture: all
Maintainer: Joao Araujo <araujoajoao@gmail.com>
Installed-Size: 1500
Depends: python3 (>= 3.9), python3-venv, python3-pip
Homepage: https://github.com/araujoajoao/DevOpsHeroCLI
Description: DevOpsHero CLI - Jogo Terminal TUI RPG de Incidentes DevOps e SRE
 DevOpsHero é um jogo interativo completo no terminal com 80 incidentes
 reais de infraestrutura, Kubernetes, Docker, Linux, CI/CD e Observabilidade.
""".encode("utf-8")

    control_buf = io.BytesIO()
    with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
        ti = tarfile.TarInfo("control")
        ti.size = len(control_content)
        ti.mtime = int(time.time())
        ti.mode = 0o644
        ti.uname = "root"
        ti.gname = "root"
        tar.addfile(ti, io.BytesIO(control_content))
    control_tar_gz = control_buf.getvalue()

    # 3. data.tar.gz
    # Monta a árvore de diretórios do Linux:
    # /usr/share/devopshero/... (código fonte e launcher)
    # /usr/bin/devopshero e /usr/bin/dh (scripts executáveis)
    # /usr/share/applications/devopshero.desktop
    # /usr/share/icons/hicolor/scalable/apps/devopshero.svg
    data_buf = io.BytesIO()
    with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
        def add_dir(rel_path):
            ti = tarfile.TarInfo(rel_path)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            ti.mtime = int(time.time())
            ti.uname = "root"
            ti.gname = "root"
            tar.addfile(ti)

        def add_file(rel_path, content: bytes, mode=0o644):
            ti = tarfile.TarInfo(rel_path)
            ti.size = len(content)
            ti.mode = mode
            ti.mtime = int(time.time())
            ti.uname = "root"
            ti.gname = "root"
            tar.addfile(ti, io.BytesIO(content))

        # Diretórios base
        dirs = [
            "usr",
            "usr/bin",
            "usr/share",
            "usr/share/applications",
            "usr/share/icons",
            "usr/share/icons/hicolor",
            "usr/share/icons/hicolor/scalable",
            "usr/share/icons/hicolor/scalable/apps",
            "usr/share/devopshero",
            "usr/share/devopshero/devopsherocli",
            "usr/share/devopshero/assets",
        ]
        for d in dirs:
            add_dir(d)

        # Executável wrapper em /usr/bin/devopshero e /usr/bin/dh
        bin_wrapper = """#!/usr/bin/env bash
# Wrapper do DevOpsHero instalado via .deb
exec /usr/share/devopshero/dh "$@"
""".encode("utf-8")
        add_file("usr/bin/devopshero", bin_wrapper, mode=0o755)
        add_file("usr/bin/dh", bin_wrapper, mode=0o755)

        # Arquivo .desktop para integração no menu de apps do Ubuntu/Gnome/KDE
        desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=DevOpsHero
GenericName=DevOps & SRE Terminal RPG
Comment=Jogo terminal TUI com 80 missões de incidentes reais
Icon=devopshero
Exec=devopshero
Terminal=true
Categories=Game;Development;System;Utility;
Keywords=devops;sre;terminal;game;tui;kubernetes;linux;cloud;
StartupNotify=true
""".encode("utf-8")
        add_file("usr/share/applications/devopshero.desktop", desktop_entry, mode=0o644)

        # Ícone oficial SVG
        svg_icon = (repo_root / "assets" / "icon.svg").read_bytes()
        add_file("usr/share/icons/hicolor/scalable/apps/devopshero.svg", svg_icon, mode=0o644)

        # Copiar assets essenciais
        add_file("usr/share/devopshero/assets/icon.svg", svg_icon, mode=0o644)
        if (repo_root / "assets" / "DevOpsHero.icns").exists():
            add_file("usr/share/devopshero/assets/DevOpsHero.icns", (repo_root / "assets" / "DevOpsHero.icns").read_bytes(), mode=0o644)

        # Copiar pyproject.toml
        add_file("usr/share/devopshero/pyproject.toml", (repo_root / "pyproject.toml").read_bytes(), mode=0o644)

        # Copiar dh launcher
        dh_bytes = (repo_root / "dh").read_bytes()
        add_file("usr/share/devopshero/dh", dh_bytes, mode=0o755)

        # Copiar código python do pacote devopsherocli
        cli_dir = repo_root / "devopsherocli"
        for root, subdirs, files in os.walk(cli_dir):
            if "__pycache__" in root:
                continue
            rel_dir = Path(root).relative_to(repo_root)
            deb_dir_path = f"usr/share/devopshero/{rel_dir.as_posix()}"
            add_dir(deb_dir_path)
            for f in files:
                if f.endswith((".pyc", ".pyo")):
                    continue
                file_path = Path(root) / f
                deb_file_path = f"{deb_dir_path}/{f}"
                content = file_path.read_bytes()
                add_file(deb_file_path, content, mode=0o644)

    data_tar_gz = data_buf.getvalue()

    # Cria o arquivo final .deb no formato GNU ar
    create_ar_archive([
        ("debian-binary", deb_binary),
        ("control.tar.gz", control_tar_gz),
        ("data.tar.gz", data_tar_gz),
    ], str(deb_output))

    size_kb = deb_output.stat().st_size / 1024
    print(f"✓ [Linux Packager] Pacote Debian/Ubuntu criado com sucesso: {deb_output} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    build_deb()

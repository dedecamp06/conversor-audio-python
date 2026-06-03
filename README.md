# Transcritor de Áudio para Relatório de Auditoria Operacional

Projeto em Python que:

1. Transcreve um ou mais áudios.
2. Identifica achados relevantes para auditoria operacional.
3. Gera um relatório em PDF com resumo executivo, evidências e recomendações.

## Requisitos

- Python 3.10+
- Dependências do projeto

## Windows (modo fácil)

Pré-requisito único: ter o **Python 3.10+** instalado (marque **"Add Python to PATH"**
durante a instalação). Não é necessário instalar FFmpeg — o `faster-whisper` já traz
o decodificador de áudio embutido.

1. Baixe o projeto com `git clone` (recomendado) ou pelo botão **Code → Download ZIP** do GitHub e extraia.
2. Dê **duplo-clique** no arquivo `iniciar_windows.bat`.

Esse `.bat` cria o ambiente virtual, instala todas as dependências e abre o servidor.
Depois é só acessar http://127.0.0.1:5000 no navegador.

> Nas próximas vezes, basta dar duplo-clique no `iniciar_windows.bat` de novo.

## Instalação (Linux / manual)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

> Para rodar a web sem instalar o pacote, use:
> `python -m auditoria_relatorio.web --host 127.0.0.1 --port 5000`
>
> Se preferir instalar o pacote e ganhar os comandos `auditoria-web` / `auditoria-relatorio`,
> rode `python -m pip install .`. Em caso de erro de build no Windows (`WinError 183`),
> apague as pastas antigas antes: `Remove-Item -Recurse -Force build, *.egg-info`.

## Uso rápido

```bash
auditoria-relatorio \
  --input ./audios \
  --output relatorio_auditoria.pdf \
  --empresa "Empresa Exemplo" \
  --operacao "Operação Logística" \
  --auditor "Nome do Auditor"
```
## Interface web para testes

Inicie o servidor:

```bash
auditoria-web --host 127.0.0.1 --port 5000
```

Depois abra no navegador:

```text
http://127.0.0.1:5000
```

Na interface, envie os áudios e clique em **Transcrever**.

Os relatórios ficam salvos na pasta `pdfs_gerados/` do projeto e aparecem na aba **PDFs gerados** para download.

## Estrutura MVC (interface web)

- `auditoria_relatorio/controllers/`: rotas e fluxo HTTP.
- `auditoria_relatorio/models/`: entidades de domínio da aplicação.
- `auditoria_relatorio/services/`: regras de negócio da interface web.
- `auditoria_relatorio/views/`: renderização e template da interface.

## Parâmetros principais

- `--input`: arquivo de áudio ou pasta com áudios.
- `--output`: caminho do PDF de saída.
- `--empresa`: nome da empresa auditada.
- `--operacao`: nome da operação auditada.
- `--auditor`: responsável pela auditoria.
- `--data-auditoria`: data no formato `DD/MM/AAAA`.
- `--idioma`: idioma da transcrição (ex.: `pt`, `en`).
- `--model`: modelo Whisper (`tiny`, `base`, `small`, `medium`, `large-v3`).
- `--device`: `cpu`, `cuda` ou `auto`.
- `--compute-type`: `int8`, `int8_float16`, `float16`, `float32`.
- `--sem-anexo-transcricao`: não inclui transcrição detalhada no PDF.

## Áudios suportados

`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.wma`, `.mp4`, `.webm`

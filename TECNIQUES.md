# Rascunho de Técnicas do Projeto

Este projeto transforma áudios em um relatório de auditoria operacional em PDF.

## Técnicas e tecnologias usadas

- **Python 3.10+** como base da aplicação.
- **Faster-Whisper** para transcrição de áudio.
- **ReportLab** para geração de PDF.
- **Flask** para interface web de testes.
- **CLI + Web**: duas formas de uso (`auditoria-relatorio` e `auditoria-web`).
- **Arquitetura MVC (na parte web)**:
  - `controllers`: rotas e fluxo HTTP
  - `models`: entidades da aplicação
  - `services`: regras de negócio
  - `views`: renderização da interface

## Resumo simples de como o projeto foi feito

1. O usuário envia um ou mais arquivos de áudio.
2. O sistema transcreve o conteúdo dos áudios.
3. A aplicação identifica pontos relevantes para auditoria.
4. Um PDF final é gerado com resumo, evidências e recomendações.

## Como o projeto foi estruturado

- A aplicação foi organizada em pacotes com separação por responsabilidade.
- Na parte web, o padrão MVC divide bem o fluxo:
  - **Controller** recebe requisições e orquestra o processo.
  - **Service** aplica as regras principais de transcrição e geração do relatório.
  - **Model** representa os dados de domínio.
  - **View** monta a interface para upload e download dos PDFs.
- Também existem pontos de entrada separados para **CLI** e **Web**, facilitando uso local e testes rápidos.

## Como usamos as bibliotecas

- **faster-whisper**: faz a transcrição dos arquivos de áudio (com escolha de modelo/dispositivo).
- **reportlab**: transforma os resultados da transcrição em um PDF estruturado.
- **flask**: expõe a interface web para enviar áudios e baixar relatórios.
- **setuptools**: empacota o projeto e registra os comandos executáveis.

## Entradas e saídas

- **Entrada**: arquivo único ou pasta com áudios.
- **Saída**: relatório em PDF.
- **Formatos suportados**: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.wma`, `.mp4`, `.webm`.

## Comando rápido (web)

```bash
auditoria-web --host 127.0.0.1 --port 5000
```

Depois: abrir `http://127.0.0.1:5000`.

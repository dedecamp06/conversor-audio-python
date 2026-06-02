from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from ..services.analysis_service import analisar_transcricoes
from ..services.report_service import gerar_relatorio_pdf
from ..services.transcription_service import AudioTranscriber, encontrar_audios


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcreve áudios e gera relatório de auditoria operacional em PDF."
    )
    parser.add_argument("--input", required=True, help="Arquivo de áudio ou diretório com áudios.")
    parser.add_argument(
        "--output",
        default="relatorio_auditoria_operacional.pdf",
        help="Caminho do PDF de saída.",
    )
    parser.add_argument("--empresa", default="Não informado", help="Nome da empresa auditada.")
    parser.add_argument("--operacao", required=True, help="Nome da operação auditada.")
    parser.add_argument("--auditor", default="Não informado", help="Nome do auditor.")
    parser.add_argument(
        "--data-auditoria",
        default=dt.date.today().strftime("%d/%m/%Y"),
        help="Data da auditoria (DD/MM/AAAA).",
    )
    parser.add_argument("--idioma", default=None, help="Idioma da transcrição (ex.: pt, en).")
    parser.add_argument(
        "--model",
        default="small",
        help="Modelo do Whisper (tiny, base, small, medium, large-v3).",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda", "auto"],
        help="Dispositivo de inferência.",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        choices=["int8", "int8_float16", "float16", "float32"],
        help="Precisão de cálculo da inferência.",
    )
    parser.add_argument(
        "--sem-anexo-transcricao",
        action="store_true",
        help="Gera o PDF sem anexar a transcrição completa.",
    )
    return parser


def _metadados(args: argparse.Namespace, total_audios: int) -> dict[str, str]:
    return {
        "Empresa": args.empresa,
        "Operação": args.operacao,
        "Auditor": args.auditor,
        "Data da auditoria": args.data_auditoria,
        "Data de emissão": dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Total de áudios": str(total_audios),
    }


def run(args: argparse.Namespace) -> Path:
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_files = encontrar_audios(input_path)
    transcriber = AudioTranscriber(
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
    )
    transcricoes = transcriber.transcrever_varios(audio_files, idioma=args.idioma)
    analise = analisar_transcricoes(transcricoes)
    gerar_relatorio_pdf(
        output_path=output_path,
        metadados=_metadados(args, total_audios=len(audio_files)),
        transcricoes=transcricoes,
        analise=analise,
        anexar_transcricao=not args.sem_anexo_transcricao,
    )
    return output_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        resultado = run(args)
    except (FileNotFoundError, PermissionError, RuntimeError, ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Relatório gerado com sucesso em: {resultado}")


if __name__ == "__main__":
    main()

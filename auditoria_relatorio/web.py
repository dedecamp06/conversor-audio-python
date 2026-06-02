from __future__ import annotations

import argparse

from .controllers.web_controller import create_app


def run_server(host: str, port: int, debug: bool) -> None:
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inicia a interface web para transcrição e relatório de auditoria."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host do servidor web.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor web.")
    parser.add_argument("--debug", action="store_true", help="Ativa modo debug.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

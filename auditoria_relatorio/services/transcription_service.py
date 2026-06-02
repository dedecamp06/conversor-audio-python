from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel

from ..models import AudioTranscript, TranscriptSegment

SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
    ".flac",
    ".aac",
    ".wma",
    ".mp4",
    ".webm",
}


def encontrar_audios(caminho: Path) -> list[Path]:
    if not caminho.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {caminho}")

    if caminho.is_file():
        if caminho.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"Arquivo de áudio não suportado: {caminho.suffix}. "
                f"Use um dos formatos: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
            )
        return [caminho]

    if caminho.is_dir():
        audios = sorted(
            p
            for p in caminho.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
        )
        if not audios:
            raise ValueError(f"Nenhum áudio suportado encontrado em: {caminho}")
        return audios

    raise ValueError(f"Tipo de caminho inválido: {caminho}")


class AudioTranscriber:
    def __init__(self, model_name: str, device: str, compute_type: str) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcrever_arquivo(
        self,
        audio_path: Path,
        idioma: str | None = None,
    ) -> AudioTranscript:
        model = self._get_model()
        segmentos_iter, info = model.transcribe(
            str(audio_path),
            language=idioma,
            vad_filter=True,
            beam_size=5,
        )

        segmentos: list[TranscriptSegment] = []
        partes_texto: list[str] = []

        for segment in segmentos_iter:
            texto = segment.text.strip()
            if not texto:
                continue

            segmentos.append(
                TranscriptSegment(
                    arquivo=audio_path.name,
                    inicio=float(segment.start),
                    fim=float(segment.end),
                    texto=texto,
                )
            )
            partes_texto.append(texto)

        return AudioTranscript(
            arquivo=audio_path,
            idioma=getattr(info, "language", idioma),
            duracao_segundos=float(getattr(info, "duration", 0.0) or 0.0),
            texto_completo=" ".join(partes_texto).strip(),
            segmentos=segmentos,
        )

    def transcrever_varios(
        self,
        audio_paths: list[Path],
        idioma: str | None = None,
    ) -> list[AudioTranscript]:
        transcricoes: list[AudioTranscript] = []
        total = len(audio_paths)
        for index, path in enumerate(audio_paths, start=1):
            print(f"[{index}/{total}] Transcrevendo: {path.name}")
            transcricoes.append(self.transcrever_arquivo(path, idioma=idioma))
        return transcricoes

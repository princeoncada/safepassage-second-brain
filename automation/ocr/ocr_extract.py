from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.ocr.ocr_review_formatter import build_review_markdown, normalize_ocr_lines


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"


@dataclass
class OCRResult:
    text: str
    engine: str
    average_confidence: float | None = None


def supported_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def output_paths(image_path: Path, output_dir: Path) -> tuple[Path, Path]:
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in image_path.stem).strip("-")
    safe_stem = safe_stem or "ocr-image"
    return output_dir / f"{safe_stem}_ocr_raw.txt", output_dir / f"{safe_stem}_ocr_review.md"


def preprocess_image(image_path: Path, output_dir: Path, enabled: bool) -> Path:
    if not enabled:
        return image_path
    try:
        from PIL import Image, ImageEnhance, ImageFilter
    except ImportError:
        return image_path

    output_dir.mkdir(parents=True, exist_ok=True)
    processed_path = output_dir / f"{image_path.stem}_preprocessed.png"
    image = Image.open(image_path)
    image = image.convert("L")
    width, height = image.size
    scale = 2 if max(width, height) < 1800 else 1
    if scale > 1:
        image = image.resize((width * scale, height * scale))
    image = ImageEnhance.Contrast(image).enhance(1.6)
    image = image.filter(ImageFilter.SHARPEN)
    image.save(processed_path)
    return processed_path


def average(values: list[float]) -> float | None:
    usable = [value for value in values if value >= 0]
    if not usable:
        return None
    return sum(usable) / len(usable)


def add_ocr_line(lines: list[str], confidences: list[float], text: Any, score: Any = None) -> None:
    value = str(text or "").strip()
    if not value:
        return
    lines.append(value)
    if score is not None:
        try:
            confidences.append(float(score))
        except (TypeError, ValueError):
            pass


def collect_paddle_result(node: Any, lines: list[str], confidences: list[float]) -> None:
    if node is None:
        return

    if isinstance(node, dict):
        texts = node.get("rec_texts") or node.get("texts")
        scores = node.get("rec_scores") or node.get("scores") or []
        if isinstance(texts, list):
            for index, text in enumerate(texts):
                score = scores[index] if isinstance(scores, list) and index < len(scores) else None
                add_ocr_line(lines, confidences, text, score)
            return
        if isinstance(node.get("text"), str):
            add_ocr_line(lines, confidences, node.get("text"), node.get("score") or node.get("confidence"))
        for nested_key in ("res", "result", "data"):
            if nested_key in node:
                collect_paddle_result(node[nested_key], lines, confidences)
        return

    json_value = getattr(node, "json", None)
    if json_value is not None:
        try:
            collect_paddle_result(json_value() if callable(json_value) else json_value, lines, confidences)
            return
        except TypeError:
            pass

    res_value = getattr(node, "res", None)
    if res_value is not None:
        collect_paddle_result(res_value, lines, confidences)
        return

    if isinstance(node, (list, tuple)):
        if (
            len(node) >= 2
            and isinstance(node[1], (list, tuple))
            and node[1]
            and isinstance(node[1][0], str)
        ):
            score = node[1][1] if len(node[1]) > 1 else None
            add_ocr_line(lines, confidences, node[1][0], score)
            return
        for item in node:
            collect_paddle_result(item, lines, confidences)


def extract_with_paddleocr(image_path: Path) -> OCRResult:
    try:
        from paddleocr import PaddleOCR
    except ImportError as error:
        raise RuntimeError("PaddleOCR is not installed.") from error

    ocr = PaddleOCR(use_textline_orientation=True, lang="en")
    raw_result = ocr.predict(str(image_path))
    lines: list[str] = []
    confidences: list[float] = []
    collect_paddle_result(raw_result, lines, confidences)
    return OCRResult(text="\n".join(lines), engine="paddleocr", average_confidence=average(confidences))


def extract_with_pytesseract(image_path: Path) -> OCRResult:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("pytesseract and Pillow are not installed.") from error

    image = Image.open(image_path)
    data: dict[str, Any] = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    lines_by_key: dict[tuple[int, int, int], list[str]] = {}
    confidences: list[float] = []
    for index, text in enumerate(data.get("text", [])):
        word = str(text).strip()
        if not word:
            continue
        key = (
            int(data.get("block_num", [0])[index]),
            int(data.get("par_num", [0])[index]),
            int(data.get("line_num", [0])[index]),
        )
        lines_by_key.setdefault(key, []).append(word)
        try:
            confidences.append(float(data.get("conf", [-1])[index]) / 100)
        except (TypeError, ValueError):
            pass
    lines = [" ".join(words) for _key, words in sorted(lines_by_key.items())]
    return OCRResult(text="\n".join(lines), engine="pytesseract", average_confidence=average(confidences))


def extract_text(image_path: Path, engine: str) -> OCRResult:
    errors: list[str] = []
    engines = ["paddleocr", "pytesseract"] if engine == "auto" else [engine]
    for candidate in engines:
        try:
            if candidate == "paddleocr":
                return extract_with_paddleocr(image_path)
            if candidate == "pytesseract":
                return extract_with_pytesseract(image_path)
        except RuntimeError as error:
            errors.append(str(error))
    raise SystemExit(
        "No OCR engine is available. Install PaddleOCR, or install pytesseract + Pillow + the Tesseract binary. "
        f"Details: {'; '.join(errors)}"
    )


def process_image(image_path: Path, output_dir: Path, engine: str, preprocess: bool) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path, review_path = output_paths(image_path, output_dir)
    with tempfile.TemporaryDirectory(prefix="safepassage-ocr-") as temp_dir:
        processed_image = preprocess_image(image_path, Path(temp_dir), preprocess)
        result = extract_text(processed_image, engine)

    cleaned_text = normalize_ocr_lines(result.text)
    raw_path.write_text(result.text.strip() + "\n", encoding="utf-8")
    review_path.write_text(
        build_review_markdown(
            source_image=image_path,
            raw_text=result.text,
            cleaned_text=cleaned_text,
            ocr_engine=result.engine,
            average_confidence=result.average_confidence,
        ),
        encoding="utf-8",
    )
    return raw_path, review_path


def collect_images(input_file: Path | None, input_dir: Path | None) -> list[Path]:
    images: list[Path] = []
    if input_file:
        if not supported_image(input_file):
            raise SystemExit(f"Unsupported or missing image file: {input_file}")
        images.append(input_file)
    if input_dir:
        if not input_dir.exists() or not input_dir.is_dir():
            raise SystemExit(f"Input directory does not exist: {input_dir}")
        images.extend(sorted(path for path in input_dir.iterdir() if supported_image(path)))
    if not images:
        raise SystemExit("No supported images found. Use --input or --input-dir with png, jpg, jpeg, or webp files.")
    return images


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract OCR text from local screenshots into reviewable artifacts.")
    parser.add_argument("--input", type=Path, help="Single image file to OCR.")
    parser.add_argument("--input-dir", type=Path, help="Directory of image files to OCR.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for OCR artifacts.")
    parser.add_argument("--engine", choices=["auto", "paddleocr", "pytesseract"], default="auto", help="OCR engine to use.")
    parser.add_argument("--no-preprocess", action="store_true", help="Disable conservative image preprocessing.")
    args = parser.parse_args()

    images = collect_images(args.input, args.input_dir)
    for image_path in images:
        raw_path, review_path = process_image(
            image_path=image_path,
            output_dir=args.output_dir,
            engine=args.engine,
            preprocess=not args.no_preprocess,
        )
        print(f"OCR artifacts written for {image_path}:")
        print(f"- raw: {raw_path}")
        print(f"- review: {review_path}")
    print("Review and edit OCR output before passing text into any ingestion script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

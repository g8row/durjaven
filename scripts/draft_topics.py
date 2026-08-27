#!/usr/bin/env python3
"""Draft the source-backed chapters from the canonical extraction evidence.

The official syllabus remains the chapter specification. For each question this
script gathers the mapped Word-export text, canonical photograph OCR, and any
extra source named in topics/manifest.json, then asks a cheap GPT-5.6 model for
a source-faithful Bulgarian LaTeX body.

Formal and mathematical chapters use Terra; prose and programming chapters use
Luna. Questions 11 and 12 are deliberately skipped because the corpus contains
no source for them. Existing non-placeholder bodies are never overwritten unless
--force is explicit.

    python3 scripts/draft_topics.py --list
    python3 scripts/draft_topics.py --topic 1 --force
    python3 scripts/draft_topics.py --workers 4
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import glob
import json
import os
import re
import subprocess
import sys
import time

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from backends import _call_codex  # noqa: E402

MANIFEST = os.path.join(ROOT, "topics", "manifest.json")
ANNOTATIONS = os.path.join(ROOT, "docs", "konspekt_annotations.json")
BODIES = os.path.join(ROOT, "topics", "bodies")
RUN_DI = os.path.join(ROOT, "run", "di")
RUN_OCR = os.path.join(ROOT, "run", "ocr")
SOURCES_DI = os.path.join(ROOT, "sources", "di")
RUN_DRAFTS = os.path.join(ROOT, "run", "drafts")

# These chapters depend on exact notation, proofs, or reconciliation of several
# formal sources. Everything else is prose/code and is economical on Luna.
TERRA_TOPICS = set(range(1, 9)) | {21, 22} | set(range(28, 36))


def read_text_pages(directory):
    chunks = []
    for path in sorted(glob.glob(os.path.join(directory, "page_*.txt"))):
        text = open(path, encoding="utf-8").read().strip()
        if text:
            chunks.append("--- %s ---\n%s" % (os.path.basename(path), text))
    return "\n\n".join(chunks)


def read_ocr(unit):
    directory = os.path.join(RUN_OCR, unit + "__production")
    chunks = []
    for path in sorted(glob.glob(os.path.join(directory, "page_*.json"))):
        doc = json.load(open(path, encoding="utf-8"))
        if doc.get("blank"):
            chunks.append("--- %s: празна страница ---" % os.path.basename(path))
            continue
        lines = []
        for item in doc.get("items", []):
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            kind = item.get("type", "text")
            if kind == "equation":
                lines.append("[ФОРМУЛА] %s" % content)
            elif kind == "code":
                lines.append("[КОД] %s" % content)
            else:
                lines.append(content)
        if lines:
            chunks.append("--- %s ---\n%s" %
                          (os.path.basename(path), "\n".join(lines)))
    return "\n\n".join(chunks)


def photo_unit(label):
    match = re.match(r"^(\d+)", label or "")
    return "temi_%02d" % int(match.group(1)) if match else None


def pdftotext(path):
    if not os.path.exists(path):
        return ""
    doc = pymupdf.open(path)
    try:
        return "\n\n".join(page.get_text("text").strip() for page in doc).strip()
    finally:
        doc.close()


def add_source(parts, seen, label, text):
    # A few Word-export text streams contain embedded NULs. They are invisible
    # in the source but cannot be passed as a process argument to codex exec.
    text = (text or "").replace("\x00", "").strip()
    if not text or label in seen:
        return
    seen.add(label)
    parts.append("===== ИЗТОЧНИК: %s =====\n%s" % (label, text))


def source_bundle(number, meta):
    parts, seen = [], set()

    pdf = meta.get("pdf")
    if pdf:
        stem = os.path.splitext(os.path.basename(pdf))[0]
        extracted = read_text_pages(os.path.join(RUN_DI, stem))
        add_source(parts, seen, "извлечен текст от %s" % pdf, extracted)
        # 4.pdf and 32.pdf are image-only; their canonical OCR is the text.
        if not extracted:
            add_source(parts, seen, "OCR на %s" % pdf, read_ocr("di_" + stem))

    photos = meta.get("photos")
    if photos:
        unit = photo_unit(photos)
        add_source(parts, seen, "снимки %s" % photos,
                   read_ocr(unit) if unit else "")

    for extra in meta.get("extra", []):
        rel = extra.replace("Задачи/", "Задачи/")
        path = os.path.join(SOURCES_DI, rel)
        base = os.path.basename(extra)
        stem = os.path.splitext(base)[0]
        if extra.endswith(".txt"):
            text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        elif base in {"Logichesko.pdf", "logichesko1.pdf", "logichesko2.pdf",
                      "SA.pdf", "ST.pdf"}:
            text = read_ocr("di_" + stem)
        elif base == "oop2.pdf":
            text = read_ocr("di_oop2_oop2")
        elif base == "SA-SI.pdf":
            text = read_text_pages(os.path.join(RUN_DI, "SA-SI"))
        else:
            text = pdftotext(path)
        add_source(parts, seen, "допълнителен %s" % extra, text)

    return "\n\n".join(parts)


def prompt_for(number, meta, annotation, sources):
    note = meta.get("note", "")
    return r"""Напиши завършена учебна глава на български като LaTeX body за
сборник за държавен изпит по компютърни науки.

ВЪПРОС: %(number)d. %(title)s
ОФИЦИАЛНА АНОТАЦИЯ (това е задължителният обхват):
%(annotation)s

БЕЛЕЖКА ЗА КАРТОГРАФИРАНЕТО:
%(note)s

ИЗТОЧНИЦИ:
%(sources)s

Изисквания:
- Върни САМО LaTeX body, без markdown ограда, без \documentclass, \begin{document},
  \chapter или заглавие на самата глава.
- Напиши самостоятелна, разбираема глава; не преписвай OCR ред по ред. Подреди
  материала според официалната анотация и покрий всяка нейна точка, за която
  източниците действително дават материал.
- Не добавяй факти, теореми или доказателства, които не се поддържат от
  източниците. Не поправяй източника мълчаливо. При съществена очевидна грешка
  използвай \begin{supp}[Бележка] ... \end{supp} и обясни разликата кратко.
- При конфликт предпочети професионално набрания допълнителен PDF, после
  извлечения текст от Word PDF, после OCR на снимки. Ако конфликтът остава,
  отбележи го, вместо да гадаеш.
- Използвай \section и \subsection за ясна йерархия. Използвай defn/keydefn,
  thm/keythm, prop, lem, cor, example, remark, proof и supp, когато са
  семантично подходящи. Не дефинирай нови LaTeX команди и среди.
- Пиши математиката като валиден LaTeX. Използвай $...$ inline и \[...\] за
  отделни формули. Не оставяй символите ⟦, ⟧, � или Unicode mathematical italic.
- За код използвай \begin{verbatim} ... \end{verbatim}; пази идентификаторите и
  операторите буквално. Не слагай код във формула.
- Екранирай %%, #, &, _ извън verbatim и математически режим.
- Завърши с \section{Изпитен фокус}: кратък списък на определенията,
  твърденията, алгоритмите и доказателствените идеи, които трябва да могат да
  бъдат възпроизведени устно.
- Не споменавай OCR, модел, промпт или процеса на създаване.
- Целевият обем е 2500-5000 думи, но вярността и пълното покритие са по-важни.
""" % {"number": number, "title": meta["title"],
       "annotation": annotation or meta["title"], "note": note or "няма",
       "sources": sources}


def clean_latex(raw):
    text = (raw or "").strip()
    text = re.sub(r"^```(?:latex|tex)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    if any(token in text for token in ("\\documentclass", "\\begin{document}",
                                       "\\chapter{")):
        raise ValueError("model returned a full document instead of a body")
    if len(text) < 1000:
        raise ValueError("draft is implausibly short (%d characters)" % len(text))
    return text.rstrip() + "\n"


def is_placeholder(path):
    if not os.path.exists(path):
        return True
    return "%% Placeholder" in open(path, encoding="utf-8").read()


def draft_one(number, meta, annotation, force, reasoning, timeout):
    path = os.path.join(BODIES, "topic_%02d.tex" % number)
    if meta.get("confidence") == "gap":
        return number, "gap retained", None
    if not force and not is_placeholder(path):
        return number, "already drafted", None

    sources = source_bundle(number, meta)
    if len(sources) < 500:
        return number, "FAILED: source bundle is empty", None
    model = "gpt-5.6-terra" if number in TERRA_TOPICS else "gpt-5.6-luna"
    prompt = prompt_for(number, meta, annotation, sources)

    error = None
    for attempt in range(1, 3):
        try:
            raw = _call_codex(prompt, model=model, timeout=timeout,
                              reasoning=reasoning)
            body = clean_latex(raw)
            open(path, "w", encoding="utf-8").write(
                "%% Drafted from the mapped corpus by scripts/draft_topics.py.\n" +
                "%% Model: %s; source characters: %d.\n" % (model, len(sources)) +
                body)
            os.makedirs(RUN_DRAFTS, exist_ok=True)
            json.dump({"topic": number, "model": model,
                       "source_characters": len(sources),
                       "output_characters": len(body)},
                      open(os.path.join(RUN_DRAFTS, "topic_%02d.json" % number), "w"),
                      ensure_ascii=False, indent=1)
            return number, "drafted", model
        except Exception as exc:
            error = str(exc)
            if attempt < 2:
                time.sleep(5)
    return number, "FAILED: " + (error or "unknown error"), model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", action="append", type=int, default=[])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--reasoning", default="low",
                    choices=["none", "low", "medium", "high"])
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    manifest = json.load(open(MANIFEST, encoding="utf-8"))["topics"]
    annotations = json.load(open(ANNOTATIONS, encoding="utf-8"))
    numbers = args.topic or sorted(int(n) for n in manifest)
    jobs = [(n, manifest[str(n)], annotations.get(str(n), ""), args.force,
             args.reasoning, args.timeout) for n in numbers]

    if args.list:
        for n, meta, annotation, *_ in jobs:
            sources = source_bundle(n, meta)
            model = "gap" if meta.get("confidence") == "gap" else (
                "gpt-5.6-terra" if n in TERRA_TOPICS else "gpt-5.6-luna")
            print("%02d  %-15s %7d chars  %s" %
                  (n, model, len(sources), meta["title"]))
        return

    results = []
    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            for result in executor.map(lambda j: draft_one(*j), jobs):
                results.append(result)
                print("topic %02d: %s%s" %
                      (result[0], result[1], " (%s)" % result[2] if result[2] else ""),
                      flush=True)
    else:
        for job in jobs:
            result = draft_one(*job)
            results.append(result)
            print("topic %02d: %s%s" %
                  (result[0], result[1], " (%s)" % result[2] if result[2] else ""),
                  flush=True)

    failed = [n for n, status, _ in results if status.startswith("FAILED")]
    if failed:
        raise SystemExit("failed topics: " + ", ".join(map(str, failed)))


if __name__ == "__main__":
    main()

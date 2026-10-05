#!/usr/bin/env python3
"""Demo redaksi FOI Malaysia.

Pipeline: PDF -> teks -> LLM lokal + fail peraturan JSON -> cadangan redaksi
-> tandalik kekal (PyMuPDF redaction) -> verifikasi imbas semula -> laporan.

Guna:  python3 scripts/redact_demo.py sample/dokumen_fiksyen_mmkn.pdf
Output: output/<nama>_redacted.pdf  +  output/<nama>_laporan.json
"""
import json
import sys
import urllib.request
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "rules" / "my-penang-foi-2010.json"
LLM_URL = "http://aiserverstation:8080/v1/chat/completions"
MODEL = "deepseek-v4-flash"


def load_rules():
    rules = json.loads(RULES_PATH.read_text())
    compact = []
    for r in rules["rules"]:
        compact.append({
            "id": r["id"],
            "reference": r["reference"],
            "type": r["type"],
            "reason": r["reason"],
        })
    return rules, compact


def build_system_prompt(compact_rules):
    rules_json = json.dumps(compact_rules, ensure_ascii=False, indent=1)
    return f"""Anda ialah enjin semakan pendedahan dokumen kerajaan di bawah
Enakmen Kebebasan Maklumat Pulau Pinang 2010 (Enakmen 16).

ATURAN (JSON):
{rules_json}

TUGASAN: Baca dokumen yang diberi. Bagi setiap fragmen teks yang PERLU
ditalik (redacted), keluarkan satu cadangan. Guna HANYA id peraturan di atas.

Prinsip wajib:
- Seksyen 11(1)(a): nombor kad pengenalan, alamat rumah, telefon peribadi,
  e-mel peribadi individu pihak ketiga -> redak.
- Seksyen 11(1)(e): nombor akaun bank, butiran sulit komersial -> redak.
- Seksyen 11(1)(b): HANYA bahagian yang mendedahkan deliberasi/keputusan
  MMKN yang belum diterbitkan -> redak. Bukan seluruh dokumen.
- Seksyen 11(1)(j): maklumat yang sudah ada kepada orang awam -> JANGAN redak.
- Seksyen 12: redak sebahagian sahaja, kekalkan baki dokumen.
- Nama pegawai awam dalam tugas rasmi (contoh: Pegawai Maklumat) -> JANGAN redak.

Balas HANYA JSON sah, format:
{{"redactions": [
  {{"text": "<fragmen tepat seperti dalam dokumen>",
    "rule_id": "<id>",
    "justification": "<sebab dalam Bahasa Melayu, rujuk seksyen>"}}
]}}"""


def ask_llm(system_prompt, doc_text):
    payload = {
        "model": MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "DOKUMEN:\n" + doc_text},
        ],
    }
    req = urllib.request.Request(
        LLM_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        out = json.loads(resp.read())
    return out["choices"][0]["message"]["content"]


def extract_json(content):
    # LLM kadang-kadang balut dengan ```json ... ```
    c = content.strip()
    if c.startswith("```"):
        c = c.split("```")[1]
        if c.startswith("json"):
            c = c[4:]
    start = c.find("{")
    end = c.rfind("}")
    return json.loads(c[start:end + 1])


def main():
    if len(sys.argv) < 2:
        print("guna: redact_demo.py <pdf>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    doc = pymupdf.open(pdf_path)
    doc_text = "\n".join(p.get_text() for p in doc)

    rules, compact = load_rules()
    prompt = build_system_prompt(compact)
    print(f"[1/4] LLM ({MODEL}) menyemak {len(doc_text)} aksara terhadap "
          f"{len(compact)} peraturan...")
    content = ask_llm(prompt, doc_text)
    result = extract_json(content)
    redactions = result.get("redactions", [])
    print(f"[2/4] {len(redactions)} cadangan diterima.")

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    stem = pdf_path.stem
    report = {"source": str(pdf_path), "model": MODEL,
             "rules_file": str(RULES_PATH), "redactions": []}

    print("[3/4] Mengaplikasikan redaksi kekal...")
    applied = 0
    for red in redactions:
        text = red["text"]
        found = False
        for pno, page in enumerate(doc):
            for inst in page.search_for(text):
                page.add_redact_annot(inst)
                found = True
                applied += 1
        report["redactions"].append({
            **red,
            "applied": found,
        })
        if not found:
            print(f"   AMARAN: teks tidak ditemui: {text[:60]}")

    for page in doc:
        page.apply_redactions()

    out_pdf = out_dir / f"{stem}_redacted.pdf"
    doc.save(out_pdf)

    print("[4/4] Verifikasi: imbas semula PDF hasil redaksi...")
    check = pymupdf.open(out_pdf)
    check_text = "\n".join(p.get_text() for p in check)
    survivors = [r["text"] for r in redactions
                 if r["text"] and r["text"] in check_text]
    report["verification"] = {
        "survivors": survivors,
        "passed": len(survivors) == 0,
    }
    report_path = out_dir / f"{stem}_laporan.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    print(f"\nPDF redaksi : {out_pdf}")
    print(f"Laporan     : {report_path}")
    print(f"Diterap     : {applied} instans bagi {len(redactions)} cadangan")
    if survivors:
        print(f"PEMINDAKLEK: {survivors}")
    else:
        print("Verifikasi LULUS — tiada teks sulit tertinggal.")


if __name__ == "__main__":
    main()

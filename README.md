# FOIA Malaysia — Machine-Readable Rules

Repo: https://github.com/mohdhafizi83/foia-my-rules

Fail peraturan (JSON) yang memetakan sebab-sebab pengecualian (exemption) dan
kewajipan pendedahan di bawah undang-undang kebebasan maklumat Malaysia, dalam
format yang boleh dibaca mesin / dimakan LLM sebagai system prompt untuk
automasi redaksi dokumen kerajaan.

Format ikut piawai antarabangsa: datenlabor-bmz/redaction-rules (CC0).

## Apa ini, apa bukan

INI: rujukan struktur "seksyen mana menghalang pendedahan apa, dan bila
pendedahan masih wajib". Boleh plug ke mana-mana tool redaction (easy-redact,
BlackBar, atau pipeline sendiri).

BUKAN: sumber undang-undang rasmi. Setiap rule carry `url` ke sumber asal;
semak warta rasmi sebelum guna untuk keputusan sebenar.

## Status fail

| Fail | Undang-undang | Status |
|---|---|---|
| rules/my-penang-foi-2010.json | Enakmen FOI Pulau Pinang 2010 (Enakmen 16) | Disahkan penuh vs warta rasmi (Jil.56 Tambahan No.1, 2 Feb 2012) |
| rules/my-selangor-foi-2011.json | Enakmen FOI Selangor 2011 | Struktur 22 seksyen disahkan; teks penuh menunggu warta |

## Ciri penting yang dipetakan

- `type: "override"` — gandingan kepentingan awam (Seksyen 11(2) PP: jabatan
  HENDAKLAH dedah jika kepentingan awam melebihi bahaya).
- `type: "rule_of_disclosure"` — pendedahan separa wajib (Seksyen 12 PP):
  kalau bahagian sulit boleh dibuang, dokumen TETAP diberi + pemohon dimaklumkan
  jumlah dipadam. Ini asas teknikal redaction automation.
- `certification` — seksyen yang memerlukan sijil (Speaker DUN / Setiausaha
  MMKN) sebagai bukti muktamad.

## Sumber disahkan

- Warta Kerajaan Pulau Pinang, Enakmen 16 (penang.gov.my/images/pdf/Warta Enakmen.pdf)
- Portal Kerajaan Negeri Selangor m.s. Enakmen Kebebasan Maklumat
- Arkib Dewan Negeri Selangor (enasel, snapshot 2025-04-30) — struktur seksyen
- Jawapan bertulis Dewan Negeri Selangor 2017 — pengesahan Seksyen 14

## Demo automasi redaksi (scripts/)

Pipeline lengkap, semua lokal (tiada data keluar mesin):

```
python3 scripts/make_sample_doc.py          # jana dokumen MMKN fiksyen
python3 scripts/redact_demo.py sample/dokumen_fiksyen_mmkn.pdf
```

Aliran: PDF → teks (PyMuPDF) → LLM lokal + fail peraturan JSON → cadangan
redaksi berjustifikasi → tandalik kekal (redaction, bukan overlay) →
verifikasi imbas semula → laporan JSON.

Keputusan demo pertama (dokumen fiksyen, model deepseek-v4-flash):
6 cadangan, 10 instans diterap, verifikasi LULUS. IC, akaun bank, telefon
peribadi, alamat rumah dan deliberasi MMKN dipadam kekal; nama pegawai
awam dalam tugas rasmi, talian jabatan dan rujukan dokumen KEKAL —
pembezaan yang betul di sisi undang-undang.

Keperluan: Python 3 + PyMuPDF + endpoint LLM OpenAI-compatible lokal
(aiserverstation:8080). Tiada API awam diperlukan — dokumen tidak
pernah meninggalkan mesin.

## Sumbangan

Tambah fail ikut konvensyen `{code-negeri}-{akronim}.json`, kemas kini
rules.json. Label status verifikasi dengan jujur dalam metadata.

## License cadangan

CC0 1.0 untuk fail rules (text undang-undang = maklumat awam; format ikut
piawai CC0 upstream). Kod alat yang dibina atasnya: berasingan.

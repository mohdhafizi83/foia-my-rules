#!/usr/bin/env python3
"""Jana satu dokumen contoh 'kerajaan' untuk demo redaksi.
Fiksyen semata-mata — nama, no. telefon, IC semua palsu."""
import pymupdf

doc = pymupdf.open()
page = doc.new_page()
text = """KERAJAAN NEGERI PULAU PINANG
KERTAS MESYUARAT MAJLIS MESYUARAT KERAJAAN NEGERI (MMKN)
RUJUKAN: PP/TP/2026/118 — TARIKH: 14 SEPTEMBER 2026

PERKARA: KELULUSAN TENDER PEMBAIKAN JAMBATAN JALAN BUKIT KETIL

1. Latar Belakang
Tender MB-2026-441 telah diberikan kepada Syarikat Infrabina Sdn Bhd
(No. Pendaftaran: 887654-X) pada nilai RM4,250,000.00. Pengurus projek
syarikat, Encik Ahmad Zaki bin Ismail, boleh dihubungi di talian
012-345 6789 atau e-mel azaki@infrabina.example.my.

2. Butiran Akaun Pembayaran
Pembayaran fasa pertama akan dikreditkan ke Akaun Bank Islam
01012345678901 atas nama INFRABINA SDN BHD.

3. Maklumat Pemilik Tanah Terjejas
Tanah Lot 4567, Mukim 6, milik Puan SITI AISYAH BINTI OMAR,
No. Kad Pengenalan: 850312-07-5566, alamat: No. 12, Jalan Permai 3,
14000 Bukit Mertajam. Puan Siti Aisyah membantah melalui peguamnya,
Haniff & Co, kerana sempadan tanah terjejas 1.2 meter.

4. Pertimbangan MMKN
MMKN pada mesyuarat 14 September 2026 telah membincangkan risiko
kelewatan projek dan MELULUSKAN bayaran pampasan tambahan sebanyak
RM310,000.00 kepada pemilik tanah. Keputusan ini belum diterbitkan
secara rasmi.

5. Rumusan
Projek dijangka siap Disember 2026. Sebarang pertanyaan:
Puan NORLIZA BINTI YUSOF, Pegawai Maklumat,
Jabatan Kerja Raya Negeri Pulau Pinang, talian 04-555 1234.

--- AKHIR ---"""

rect = pymupdf.Rect(50, 50, 545, 800)
page.insert_textbox(rect, text, fontsize=10, fontname="helv",
                   lineheight=1.45)
doc.save("sample/dokumen_fiksyen_mmkn.pdf")
print("sample/dokumen_fiksyen_mmkn.pdf written")

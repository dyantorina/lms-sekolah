import json
import os
import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="LMS Sekolah - Bu Rina",
                   layout="wide", page_icon="📚")

# --- MASTER DATA ---
DAFTAR_MAPEL = [
    "Matematika",
    "Koding dan Kecerdasan Artifisial"
]

DATA_SISWA_KELAS = {
    "X Mesin 1": [
        "ABDUL SIDIK", "ADITIA SYAHLAN MUBAROK", "AHMAD SOPIAN BAIHAQI", "AHMAD TARYONO",
        "ALANZA ADELIO FAADILAH", "ALFREDO DIZA ARDANI", "ANDRE MUHAMMAD", "ARDITYA DANU RAMADHAN",
        "ARIYA PRATAMA", "AZKA ZHAFIF ELFREDA", "AZRIL HAETAMI", "FATHIR RIZKI RAMADHAN",
        "GHALY ALFATH YUSRA", "HAFIID NAJAMUDIN AGUS", "ILHAM SYAHIN KAILANI",
        "IVANUEL YUWARESTIAN ADHI PRAMANA", "KHAFID SENJA PAMUNGKAS", "KRISNANDA AJI FABIAN",
        "MALKA FIRDAUS GUNAWAN", "MEDISON PUTRA TAUFIK", "MOHAMAD FAUZAN",
        "MUHAMAD MAULANA ALFARIS", "MUHAMAD RIFALDI", "MUHAMMAD ADIB BUSYR", "MUHAMMAD ARKA ARRIZIQ",
        "MUHAMMAD FAHZAN ARSYADI", "MUHAMMAD FERO FERIZKO", "MUHAMMAD LINTANG AQSHAFAIRUS",
        "MUHAMMAD MAHBUB MAULUDY", "MUHAMMAD NUR FADILAH", "MUHAMMAD RAYHAN BAIHAQI",
        "MUHAMMAD RIZIQ", "MURSHALIN MARZHUKHI", "RADIT DEVA FERDIANSYAH", "WILFIANDRE AL-ADHA ARIFIN"
    ],
    "X Mesin 2": [
        "ABDUL ADIT PRAWIRA", "AHMAD ISMAIL KURNIA", "AKHMAD AL ROSYID", "ALFIN RIZKITYA PUTRA",
        "ALVI IGRA DINATA SURAHMAN", "ANDRE RAFAEL PURBA", "ANDRI PUTRA DARMAWAN", "BENUA PANDU PURNAMA",
        "CHARLY REFAEL SINAGA", "FATHI RAIHAAN AZARIA", "HAFISH ELANG ANGGAYUDA", "HANZALAH FADILAH",
        "JUAN RISKI KAISAN", "KAFA MUBAROK", "KHOIRUL FAHMI", "LEANDRA DANADYAKSA",
        "M. EZRA MALEKO RASENDRIYA", "M. ILHAM FIKRI HAIKAL", "MUHAMAD BAGUS KUSUMAHADI",
        "MUHAMAD KHAIRUL AZAM", "MUHAMMAD ABRIL CAHYADI", "MUHAMMAD AFIF AKBAR",
        "MUHAMMAD DAVA ZAKI AL GUFRON", "MUHAMMAD ERLAND FIRDAUS", "RADITYA HIMAWAN",
        "RAIKHAN FIRDAUS", "REFAN SURYA KUSNADI", "REIHAN FADHIL AL KABIR",
        "RICO DWI FAJAR HIDAYATULOH", "RIVINO PUTRA RAMADHAN", "RIZKI BURHANUDIN ANAS",
        "SAHID ARDIAN", "SEFVA PUTRA WIRAWAN", "SURYA SAPUTRA RAMADANI", "TIYAN ZAHRAN ALTHAFI",
        "YOVIE ALFIANSYAH"
    ],
    "X TMI": [
        "ABID AQILA PRANAJA", "ADAM WILDANSYAH", "ADNAN AN NAWAWI", "ADNAN ASKURI",
        "ATQA KHAIRY ALFATURIZKY", "AZRIEL RAFFAEL RIZKY RAMADHAN", "AZRIL ADITYA",
        "BAIHAQI FATIRIANSYAH", "DANISH RAFFA", "DIFORSHEV IHZA LAILI PONTOH",
        "DZIKRY LUKMANUL HAKIM", "EGA ANUGRAH SYARIFUDIN", "FADLAN FAEYZA AFFANDI",
        "FAIRUZ DHIRGHAM SALIM", "FATHIR SYAPUTRA", "GALIH VICKY WIDIANSYAH",
        "GHIFAR ACHMAD FAHREZI", "HANAN PANDU WICAKSONO", "ILHAM PUTRA WIJAYANTO",
        "JENAS BAYU PUTRA", "KAIZHI EL JABAR RAHMAN", "KEEFAN HARTONO",
        "MIFTACHUL ARZAQIE", "MUHAMAD AGUNG ZAKARIA", "MUHAMAD RIO SUMANTRI",
        "MUHAMMAD AL FACHRI RAMADHAN", "MUHAMMAD RAFQI FAHROZAN", "MUHAMMAD RAYYAN RAMADHAN",
        "MUHAMMAD ZIDANE FAHRIZY", "NAFI ALAMSYAH", "ORYZA RAFIF KURNIAWAN", "RESTU ALFADILAH",
        "REZKY ADHA ARDIYANTO", "RIZKY ADRIAN SAPUTRA", "SHAFWAN ALTHAF MUALIF", "SYAHRUL JIDAN"
    ],
    "X DGM": [
        "ADITYA GILANG RAMADHAN ROIS", "AGIL PANDUWINATA SAFUTRA", "AGUNG PRASETYO",
        "AHMAD FACHRI SAPUTRA", "AHMAD NUR BASYARUDIN", "AKMAL RIZQI FIRDAUS",
        "ATHADHIA DWI KHAIRULLAH", "AZRIL APRIANSYAH", "DIMAS ADI SETIAWAN",
        "EDISTA VRISTYO", "EKA SEPTIAN RAMADHAN", "ERENS REYHAN SAPUTRA",
        "FARIID DHIYAA RISKY", "FATHIR SATRIA AR RAZZA", "FAZRIL RIZKY ARYAKA",
        "FIRZA HALIM", "IKROM PERMANA", "KAYLA JAQUALIN RAMADHANI", "KEVIN MUHAMAD RASYA",
        "KHOIRU ALHAFIDZUL AKBAR", "LUTHFI DAFINA KHAIRUNISA", "MOCHAMMAD FARHAN AL-HAQIQI",
        "MUHAMAD REZCY ALVIANSYAH", "MUHAMAD YASER ADHA SAPUTRA", "MUHAMMAD ALPAN",
        "MUHAMMAD ANJI AL-BIANSYAH", "MUHAMMAD RACHEL MALAIKA", "MUHAMMAD ZACKY AL-FACHRY",
        "PRADIPTA AFKAR SAFARAZ", "PRANANDA RADITYA ALDITI", "RAFA ADITYA RAMADANI",
        "REYHAN SYAHPUTRA", "RIFQI AZKA SYABANI", "SAIFUL ARIF", "ULYA QONITA RIDWAN", "ZAQI ADZHAR"
    ]
}

DAFTAR_KELAS = list(DATA_SISWA_KELAS.keys())

# --- KONEKSI GOOGLE SHEETS CLOUD ---
SHEET_TITLE = "DATABASE_LMS_SEKOLAH"

@st.cache_resource
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    if "kunci_json" in st.secrets:
        kunci = st.secrets["kunci_json"]
        if isinstance(kunci, str):
            try:
                key_dict = json.loads(kunci)
            except Exception:
                key_dict = json.loads(kunci, strict=False)
        else:
            key_dict = dict(kunci)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            key_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "kunci.json", scope)

    client = gspread.authorize(creds)
    return client

def get_worksheet(sheet_name):
    client = get_gspread_client()
    sh = client.open(SHEET_TITLE)
    return sh.worksheet(sheet_name)

def read_data(sheet_name):
    try:
        ws = get_worksheet(sheet_name)
        data = ws.get_all_values()
        if len(data) > 1:
            headers = data[0]
            headers = [
                h if h != "" else f"Kolom_{i+1}" for i, h in enumerate(headers)]
            return pd.DataFrame(data[1:], columns=headers)
        elif len(data) == 1:
            headers = [
                h if h != "" else f"Kolom_{i+1}" for i, h in enumerate(data[0])]
            return pd.DataFrame(columns=headers)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal membaca data dari Google Sheets: {e}")
        return pd.DataFrame()

def append_data(sheet_name, row_values):
    try:
        ws = get_worksheet(sheet_name)
        ws.append_row(row_values)
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        return False

# ==============================================================================
# ENGINE CETAK LAPORAN PDF (KOP RESMI SMKN 4 TANGERANG)
# ==============================================================================
class PDFLMS(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 5, "PEMERINTAH PROVINSI BANTEN", ln=True, align="C")
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 5, "DINAS PENDIDIKAN DAN KEBUDAYAAN", ln=True, align="C")
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 6, "SMK NEGERI 4 TANGERANG", ln=True, align="C")
        self.set_font("Helvetica", "", 8)
        self.cell(
            0, 4, "Jl. Veteran No. 1A, Babakan, Kec. Tangerang, Kota Tangerang, Banten 15118", ln=True, align="C")

        self.ln(3)
        self.set_line_width(0.7)
        self.line(10, 32, 200, 32)
        self.set_line_width(0.2)
        self.line(10, 33, 200, 33)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(
            0, 10, f"Sistem LMS SMKN 4 Tangerang | Halaman {self.page_no()}", align="R")

def buat_pdf_harian(nama_guru, kelas, mapel, jam_ke, tanggal, materi, catatan):
    pdf = PDFLMS(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, "JURNAL & AGENDA PEMBELAJARAN HARIAN", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    info = [
        ("Nama Guru", nama_guru),
        ("Mata Pelajaran", mapel),
        ("Kelas / Tingkat", kelas),
        ("Jam Pelajaran Ke-", str(jam_ke)),
        ("Hari / Tanggal", str(tanggal)),
    ]
    for label, val in info:
        pdf.cell(42, 6, label, border=0)
        pdf.cell(5, 6, ":", border=0)
        pdf.set_font("Helvetica", "B" if label in [
                     "Nama Guru", "Kelas / Tingkat"] else "", 10)
        pdf.cell(0, 6, str(val), border=0, ln=True)
        pdf.set_font("Helvetica", "", 10)

    pdf.ln(3)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, " MATERI / CAPAIAN PEMBELAJARAN:", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, materi if materi else "-", border=1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, " CATATAN PERKEMBANGAN / PENUGASAN SISWA:", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, catatan if catatan else "-", border=1)

    pdf.ln(12)
    pdf.cell(115, 5, "", border=0)
    pdf.cell(0, 5, f"Tangerang, {tanggal}", ln=True, align="C")
    pdf.cell(115, 5, "", border=0)
    pdf.cell(0, 5, "Guru Mata Pelajaran,", ln=True, align="C")
    pdf.ln(18)
    pdf.cell(115, 5, "", border=0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, nama_guru, ln=True, align="C")

    return bytes(pdf.output())

def buat_pdf_rekap_bulanan(df_bulan, nama_guru, mapel, kelas, bulan_nama, tahun):
    pdf = PDFLMS(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0, 6, f"REKAPITULASI JURNAL MENGAJAR BULAN {bulan_nama.upper()} {tahun}", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 9)
    pdf.cell(35, 5, "Guru Mata Pelajaran", border=0)
    pdf.cell(5, 5, f": {nama_guru}", border=0)
    pdf.cell(60, 5, "", border=0)
    pdf.cell(25, 5, "Kelas", border=0)
    pdf.cell(0, 5, f": {kelas}", border=0, ln=True)

    pdf.cell(35, 5, "Mata Pelajaran", border=0)
    pdf.cell(5, 5, f": {mapel}", border=0)
    pdf.cell(60, 5, "", border=0)
    pdf.cell(25, 5, "Periode", border=0)
    pdf.cell(0, 5, f": {bulan_nama} {tahun}", border=0, ln=True)
    pdf.ln(3)

    pdf.set_fill_color(225, 235, 245)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(8, 7, "No", border=1, align="C", fill=True)
    pdf.cell(22, 7, "Tanggal", border=1, align="C", fill=True)
    pdf.cell(18, 7, "Jam Ke-", border=1, align="C", fill=True)
    pdf.cell(73, 7, "Materi / Capaian Pembelajaran", border=1, align="C", fill=True)
    pdf.cell(69, 7, "Catatan / Penugasan", border=1, align="C", fill=True)
    pdf.ln(7)

    pdf.set_font("Helvetica", "", 8)
    no = 1
    for _, row in df_bulan.iterrows():
        tgl_str = str(row.iloc[0]) if len(row) > 0 else ""
        jam_str = str(row.iloc[5]) if len(row) > 5 else "-"
        mat_str = str(row.iloc[3])[:75] if len(row) > 3 else "-"
        cat_str = str(row.iloc[4])[:70] if len(row) > 4 else "-"

        pdf.cell(8, 6, str(no), border=1, align="C")
        pdf.cell(22, 6, tgl_str, border=1, align="C")
        pdf.cell(18, 6, jam_str, border=1, align="C")
        pdf.cell(73, 6, f" {mat_str}", border=1)
        pdf.cell(69, 6, f" {cat_str}", border=1)
        pdf.ln(6)
        no += 1

    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9)
    col_w = 95
    pdf.cell(col_w, 5, "Mengetahui,", align="C")
    pdf.cell(col_w, 5, f"Tangerang, 30 {bulan_nama} {tahun}", align="C", ln=True)
    pdf.cell(col_w, 5, "Kepala SMK Negeri 4 Tangerang", align="C")
    pdf.cell(col_w, 5, "Guru Mata Pelajaran,", align="C", ln=True)

    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(col_w, 5, "( ................................................ )", align="C")
    pdf.cell(col_w, 5, f"{nama_guru}", align="C", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(col_w, 4, "NIP. ............................................", align="C")
    pdf.cell(col_w, 4, "NIP. ............................................", align="C", ln=True)

    return bytes(pdf.output())

# --- FUNGSI CETAK PDF PRESENSI HARIAN ---
def buat_pdf_presensi_harian(nama_guru, kelas, mapel, tanggal, data_presensi_dict):
    pdf = PDFLMS(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, "DAFTAR HADIR SISWA (PRESENSI HARIAN)", ln=True, align="C")
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 9)
    col_w = 95
    pdf.cell(28, 5, "Mata Pelajaran", border=0)
    pdf.cell(67, 5, f": {mapel}", border=0)
    pdf.cell(25, 5, "Kelas", border=0)
    pdf.cell(0, 5, f": {kelas}", border=0, ln=True)

    pdf.cell(28, 5, "Guru Pengampu", border=0)
    pdf.cell(67, 5, f": {nama_guru}", border=0)
    pdf.cell(25, 5, "Hari / Tanggal", border=0)
    pdf.cell(0, 5, f": {tanggal}", border=0, ln=True)
    pdf.ln(4)

    # Header Tabel Presensi
    pdf.set_fill_color(225, 235, 245)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(12, 6.5, "No", border=1, align="C", fill=True)
    pdf.cell(133, 6.5, "Nama Lengkap Siswa", border=1, align="C", fill=True)
    pdf.cell(45, 6.5, "Keterangan", border=1, align="C", fill=True)
    pdf.ln(6.5)

    pdf.set_font("Helvetica", "", 8.5)
    hadir = sakit = izin = alpa = 0

    for idx, (nama, stt) in enumerate(data_presensi_dict.items(), 1):
        pdf.cell(12, 5.5, str(idx), border=1, align="C")
        pdf.cell(133, 5.5, f"  {nama}", border=1)
        
        # Penanda visual status
        status_clean = str(stt).strip().capitalize()
        pdf.cell(45, 5.5, status_clean, border=1, align="C")
        pdf.ln(5.5)

        if status_clean == "Hadir":
            hadir += 1
        elif status_clean == "Sakit":
            sakit += 1
        elif status_clean == "Izin":
            izin += 1
        elif status_clean == "Alpa":
            alpa += 1

    # Rekapitulasi Presensi
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(245, 245, 245)
    rekap_teks = f"Rekapitulasi: Hadir = {hadir}  |  Sakit = {sakit}  |  Izin = {izin}  |  Alpa = {alpa}  |  Total = {len(data_presensi_dict)} Siswa"
    pdf.cell(0, 6, rekap_teks, border=1, align="C", fill=True)

    # Tanda Tangan
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(115, 5, "", border=0)
    pdf.cell(0, 5, f"Tangerang, {tanggal}", ln=True, align="C")
    pdf.cell(115, 5, "", border=0)
    pdf.cell(0, 5, "Guru Mata Pelajaran,", ln=True, align="C")
    pdf.ln(18)
    pdf.cell(115, 5, "", border=0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, nama_guru, ln=True, align="C")

    return bytes(pdf.output())

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🏫 LMS SMK (Cloud Drive)")
role = st.sidebar.radio("Masuk Sebagai:", ["Guru", "Siswa"])

# ==============================================================================
# 1. FITUR GURU
# ==============================================================================
if role == "Guru":
    st.sidebar.markdown("---")
    menu_guru = st.sidebar.selectbox("Pilih Modul:", [
        "Jurnal & Agenda Mengajar",
        "Presensi Siswa",
        "Manajemen Materi",
        "Bank Soal & Nilai Ujian"
    ])

    # --- MODUL 1: AGENDA GURU & CETAK PDF ---
    if menu_guru == "Jurnal & Agenda Mengajar":
        st.header("📝 Agenda & Jurnal Guru (Tersimpan di Google Drive)")

        with st.form("form_agenda", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                guru_nama = st.text_input(
                    "Nama Guru", value="Rina Nurmaladewi, S.Pd")
                tgl_agenda = st.date_input("Tanggal", value=date.today())
                mapel_agenda = st.selectbox("Mata Pelajaran", DAFTAR_MAPEL)
                kelas_agenda = st.selectbox("Kelas", DAFTAR_KELAS)
                jam_agenda = st.selectbox(
                    "Jam Pelajaran Ke-", ["1 - 2", "3 - 4", "5 - 6", "7 - 8", "9 - 10"])
            with col2:
                capaian = st.text_area(
                    "Materi / Capaian Pembelajaran", placeholder="Contoh: Logika Pemrograman / Eksponen", height=130)
                catatan = st.text_area(
                    "Catatan Khusus / Tugas Siswa", placeholder="Contoh: Diskusi kelompok, latihan mandiri", height=100)

            simpan_agenda = st.form_submit_button("Simpan Agenda Mengajar")
            if simpan_agenda:
                berhasil = append_data("agenda_guru", [
                    str(tgl_agenda), mapel_agenda, kelas_agenda, capaian, catatan, jam_agenda, guru_nama
                ])
                if berhasil:
                    st.success(
                        "Agenda berhasil dicatat dan tersimpan di Google Drive!")

        st.subheader("Riwayat Jurnal Mengajar (Realtime dari Cloud)")
        df_agenda = read_data("agenda_guru")
        if not df_agenda.empty:
            st.dataframe(df_agenda.iloc[::-1], use_container_width=True)
        else:
            st.info("Belum ada riwayat agenda yang tercatat.")

        # --- FITUR CETAK LAPORAN PDF ---
        st.write("---")
        st.subheader("🖨️ Cetak Dokumen PDF Resmi")
        tab_harian, tab_bulanan = st.tabs(
            ["Cetak Agenda Hari Ini", "Cetak Rekap Bulanan per Kelas"])

        with tab_harian:
            st.caption(
                "Cetak lembar agenda yang sedang aktif di formulir atas lengkap dengan kop sekolah.")
            if st.button("Siapkan PDF Agenda Hari Ini"):
                pdf_bytes_harian = buat_pdf_harian(
                    nama_guru=guru_nama,
                    kelas=kelas_agenda,
                    mapel=mapel_agenda,
                    jam_ke=jam_agenda,
                    tanggal=tgl_agenda,
                    materi=capaian,
                    catatan=catatan
                )
                st.download_button(
                    label="📄 Unduh PDF Agenda Hari Ini",
                    data=pdf_bytes_harian,
                    file_name=f"Agenda_{kelas_agenda}_{tgl_agenda}.pdf",
                    mime="application/pdf"
                )

        with tab_bulanan:
            st.caption(
                "Menarik riwayat mengajar dari Google Sheets dan menyusun rekap bulanan.")
            c_kls, c_bln, c_thn = st.columns(3)
            pilih_kls_rekap = c_kls.selectbox(
                "Pilih Kelas", DAFTAR_KELAS, key="rekap_kls")
            daftar_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            pilih_bln_rekap = c_bln.selectbox(
                "Pilih Bulan", daftar_bulan, index=date.today().month - 1)
            tahun_rekap = c_thn.number_input(
                "Tahun", min_value=2024, max_value=2030, value=date.today().year)

            if st.button("Tarik & Susun Rekap Bulanan"):
                if not df_agenda.empty:
                    bulan_angka = f"{daftar_bulan.index(pilih_bln_rekap) + 1:02d}"
                    kolom_tgl = df_agenda.columns[0]
                    kolom_kls = df_agenda.columns[2]

                    df_filter = df_agenda[
                        (df_agenda[kolom_kls].astype(str) == str(pilih_kls_rekap)) &
                        (df_agenda[kolom_tgl].astype(str).str.contains(
                            f"-{bulan_angka}-", na=False))
                    ]

                    if not df_filter.empty:
                        pdf_bytes_rekap = buat_pdf_rekap_bulanan(
                            df_bulan=df_filter,
                            nama_guru=guru_nama,
                            mapel=mapel_agenda,
                            kelas=pilih_kls_rekap,
                            bulan_nama=pilih_bln_rekap,
                            tahun=tahun_rekap
                        )
                        st.success(
                            f"Ditemukan {len(df_filter)} riwayat pertemuan untuk {pilih_kls_rekap}!")
                        st.download_button(
                            label=f"📊 Unduh Rekap PDF {pilih_bln_rekap} {tahun_rekap}",
                            data=pdf_bytes_rekap,
                            file_name=f"Rekap_{pilih_kls_rekap}_{pilih_bln_rekap}_{tahun_rekap}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.warning(
                            f"Belum ada agenda mengajar yang tersimpan untuk {pilih_kls_rekap} pada periode {pilih_bln_rekap} {tahun_rekap}.")
                else:
                    st.info("Basis data riwayat agenda di cloud masih kosong.")

    # --- MODUL 2: PRESENSI SISWA & CETAK PDF HARIAN ---
    elif menu_guru == "Presensi Siswa":
        st.header("📋 Presensi Kehadiran Siswa (Tersimpan di Google Drive)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            guru_presensi = st.text_input("Guru Pengampu", value="Rina Nurmaladewi, S.Pd")
        with col2:
            tgl_absen = st.date_input(
                "Tanggal Presensi", value=date.today(), key="tgl_absen")
        with col3:
            mapel_absen = st.selectbox(
                "Mata Pelajaran", DAFTAR_MAPEL, key="mapel_absen")
        with col4:
            kelas_absen = st.selectbox(
                "Pilih Kelas", DAFTAR_KELAS, key="kls_absen")

        daftar_nama = DATA_SISWA_KELAS[kelas_absen]
        st.write(
            f"Daftar Siswa **{kelas_absen}** ({len(daftar_nama)} Siswa) — Mapel: **{mapel_absen}**")

        with st.form("form_presensi"):
            absensi_input = {}
            for i, siswa in enumerate(daftar_nama, 1):
                cols = st.columns([1, 4, 3])
                cols[0].write(f"{i}.")
                cols[1].write(siswa)
                absensi_input[siswa] = cols[2].selectbox(
                    "Status", ["Hadir", "Sakit", "Izin", "Alpa"], key=f"status_{kelas_absen}_{siswa}", label_visibility="collapsed"
                )

            submit_absen = st.form_submit_button("Simpan Presensi ke Google Drive")
            if submit_absen:
                ws = get_worksheet("presensi")
                baris_baru = []
                for nama, stt in absensi_input.items():
                    baris_baru.append(
                        [str(tgl_absen), mapel_absen, kelas_absen, nama, stt])
                ws.append_rows(baris_baru)
                st.session_state["terakhir_presensi"] = absensi_input
                st.success(f"Presensi {kelas_absen} berhasil diunggah permanen ke Google Sheets!")

        # --- FITUR CETAK PRESENSI PDF HARIAN ---
        st.write("---")
        st.subheader("🖨️ Cetak Presensi Harian (PDF)")
        c_p1, c_p2 = st.columns(2)

        with c_p1:
            st.caption("Cetak langsung dari formulir presensi yang sedang aktif/diisi di atas:")
            pdf_bytes_aktif = buat_pdf_presensi_harian(
                nama_guru=guru_presensi,
                kelas=kelas_absen,
                mapel=mapel_absen,
                tanggal=str(tgl_absen),
                data_presensi_dict=absensi_input
            )
            st.download_button(
                label=f"📄 Unduh PDF Presensi Hari Ini ({kelas_absen})",
                data=pdf_bytes_aktif,
                file_name=f"Presensi_{kelas_absen}_{tgl_absen}.pdf",
                mime="application/pdf",
                key="btn_unduh_presensi_aktif"
            )

        with c_p2:
            st.caption("Atau cetak dari data riwayat yang tersimpan di Google Sheets:")
            if st.button("Tarik Data Cloud & Cetak PDF"):
                df_absen_cloud = read_data("presensi")
                if not df_absen_cloud.empty:
                    df_filter_cloud = df_absen_cloud[
                        (df_absen_cloud.iloc[:, 0].astype(str) == str(tgl_absen)) &
                        (df_absen_cloud.iloc[:, 2].astype(str) == str(kelas_absen))
                    ]
                    if not df_filter_cloud.empty:
                        data_cloud_dict = {}
                        for _, row in df_filter_cloud.iterrows():
                            data_cloud_dict[row.iloc[3]] = row.iloc[4]
                        
                        pdf_bytes_cloud = buat_pdf_presensi_harian(
                            nama_guru=guru_presensi,
                            kelas=kelas_absen,
                            mapel=mapel_absen,
                            tanggal=str(tgl_absen),
                            data_presensi_dict=data_cloud_dict
                        )
                        st.download_button(
                            label=f"📄 Unduh PDF Presensi Terarsip ({tgl_absen})",
                            data=pdf_bytes_cloud,
                            file_name=f"Presensi_Arsip_{kelas_absen}_{tgl_absen}.pdf",
                            mime="application/pdf",
                            key="btn_unduh_presensi_cloud"
                        )
                    else:
                        st.warning(f"Tidak ada riwayat presensi tersimpan untuk {kelas_absen} pada tanggal {tgl_absen}.")
                else:
                    st.info("Basis data presensi di cloud masih kosong.")

        st.subheader(f"Riwayat Presensi Tersimpan - {kelas_absen}")
        df_absen = read_data("presensi")
        if not df_absen.empty and len(df_absen.columns) >= 3:
            kolom_kls = df_absen.columns[2]
            df_filter = df_absen[df_absen[kolom_kls] == kelas_absen]
            st.dataframe(df_filter.iloc[::-1], use_container_width=True)

    # --- MODUL 3: MANAJEMEN MATERI ---
    elif menu_guru == "Manajemen Materi":
        st.header("📁 Bagikan Materi Pembelajaran")
        with st.form("form_materi", clear_on_submit=True):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                judul_materi = st.text_input(
                    "Judul Materi", placeholder="Dasar Percabangan Python / Eksponen")
                mapel_materi = st.selectbox("Mata Pelajaran", DAFTAR_MAPEL)
            with col_m2:
                kelas_materi = st.selectbox("Target Kelas", DAFTAR_KELAS)
                link_materi = st.text_input(
                    "Tautan Materi (Google Drive / YouTube)", placeholder="https://drive.google.com/...")
            catatan_materi = st.text_area("Ringkasan / Petunjuk Belajar")

            simpan_materi = st.form_submit_button("Terbitkan Materi ke Cloud")
            if simpan_materi:
                berhasil = append_data("materi", [
                    judul_materi, mapel_materi, kelas_materi, link_materi, catatan_materi
                ])
                if berhasil:
                    st.success(
                        "Materi berhasil disimpan dan dapat diakses siswa!")

        st.subheader("Daftar Materi Aktif di Google Drive")
        df_materi = read_data("materi")
        if not df_materi.empty:
            st.dataframe(df_materi.iloc[::-1], use_container_width=True)

    # --- MODUL 4: BANK SOAL & REKAP NILAI ---
    elif menu_guru == "Bank Soal & Nilai Ujian":
        st.header("⚙️ Bank Soal & Hasil Evaluasi Siswa")
        tab1, tab2 = st.tabs(["Tambah Butir Soal", "Rekap Nilai Siswa"])

        with tab1:
            with st.form("form_soal", clear_on_submit=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    mapel_soal = st.selectbox("Mata Pelajaran", DAFTAR_MAPEL)
                with col_s2:
                    topik = st.text_input(
                        "Nama Ujian / Topik", placeholder="Contoh: Kuis 1 Logika Percabangan")

                pertanyaan = st.text_area(
                    "Pertanyaan (Bisa menggunakan LaTeX rumus, contoh: $2^3 \\times 2^4$)", height=100)
                c1, c2 = st.columns(2)
                op_a = c1.text_input("Pilihan A")
                op_b = c2.text_input("Pilihan B")
                op_c = c1.text_input("Pilihan C")
                op_d = c2.text_input("Pilihan D")
                kunci = st.selectbox("Kunci Jawaban Benar", [
                    "A", "B", "C", "D"])

                simpan_soal = st.form_submit_button(
                    "Simpan Soal ke Google Sheets")
                if simpan_soal:
                    berhasil = append_data("bank_soal", [
                        mapel_soal, topik, pertanyaan, op_a, op_b, op_c, op_d, kunci
                    ])
                    if berhasil:
                        st.success(
                            "Soal baru berhasil tersimpan ke Bank Soal Cloud!")

        with tab2:
            st.subheader("Rekap Nilai Siswa (Langsung dari Cloud)")
            df_nilai = read_data("nilai_ujian")
            if not df_nilai.empty:
                st.dataframe(df_nilai.iloc[::-1], use_container_width=True)
            else:
                st.info("Belum ada data nilai ujian masuk.")

# ==============================================================================
# 2. FITUR SISWA
# ==============================================================================
else:
    st.sidebar.markdown("---")
    menu_siswa = st.sidebar.selectbox(
        "Pilihan Siswa:", ["Materi Belajar", "Ujian Online (CBT)"])

    if menu_siswa == "Materi Belajar":
        st.header("📖 Materi Pelajaran")
        c1, c2 = st.columns(2)
        with c1:
            kls_pilih = st.selectbox("Pilih Kelas Kamu:", DAFTAR_KELAS)
        with c2:
            mapel_pilih = st.selectbox("Pilih Mata Pelajaran:", DAFTAR_MAPEL)

        df_materi = read_data("materi")
        if not df_materi.empty and 'kelas' in df_materi.columns and 'mapel' in df_materi.columns:
            materi_filter = df_materi[(df_materi['kelas'] == kls_pilih) & (
                df_materi['mapel'] == mapel_pilih)]
            if materi_filter.empty:
                st.info("Belum ada materi untuk kelas dan mata pelajaran ini.")
            else:
                for _, r in materi_filter.iterrows():
                    with st.expander(f"📌 {r.get('judul', 'Materi')}"):
                        st.write(
                            f"**Ringkasan / Petunjuk:** {r.get('catatan', '-')}")
                        link = r.get('url_link', '')
                        if str(link).startswith("http"):
                            st.markdown(f"🔗 [Buka Tautan Materi]({link})")
        else:
            st.info("Belum ada materi yang tersedia.")

    elif menu_siswa == "Ujian Online (CBT)":
        st.header("✍️️ Ujian Online")

        col_s1, col_s2, col_s3 = st.columns(3)
        kelas_siswa = col_s1.selectbox("Kelas:", DAFTAR_KELAS)
        nama_siswa = col_s2.selectbox(
            "Pilih Nama Kamu:", DATA_SISWA_KELAS[kelas_siswa])
        mapel_siswa = col_s3.selectbox("Mata Pelajaran:", DAFTAR_MAPEL)

        df_soal = read_data("bank_soal")
        if not df_soal.empty and 'mapel' in df_soal.columns and 'topik' in df_soal.columns:
            soal_mapel = df_soal[df_soal['mapel'] == mapel_siswa]
            topik_list = soal_mapel['topik'].dropna().unique().tolist()

            if not topik_list:
                st.warning(f"Belum ada ujian aktif untuk {mapel_siswa}.")
            else:
                topik_pilihan = st.selectbox("Pilih Topik Ujian:", topik_list)
                soal_aktif = soal_mapel[soal_mapel['topik'] == topik_pilihan]
                st.write(f"Jumlah Soal: **{len(soal_aktif)}** butir.")

                with st.form("form_cbt"):
                    jawaban_user = {}
                    for idx, (_, row) in enumerate(soal_aktif.iterrows()):
                        st.markdown(f"**Soal {idx + 1}:** {row['pertanyaan']}")
                        pilihan = [
                            f"A. {row['opsi_a']}",
                            f"B. {row['opsi_b']}",
                            f"C. {row['opsi_c']}",
                            f"D. {row['opsi_d']}"
                        ]
                        jawab = st.radio(
                            f"Jawaban No. {idx+1}:", pilihan, key=f"q_{idx}")
                        jawaban_user[idx] = (jawab[0], str(
                            row['kunci']).strip().upper())

                    submit_ujian = st.form_submit_button("Kirim Jawaban Ujian")
                    if submit_ujian:
                        benar = 0
                        for _, (pilih_huruf, kunci_asli) in jawaban_user.items():
                            if pilih_huruf.strip().upper() == kunci_asli:
                                benar += 1

                        skor_akhir = round((benar / len(soal_aktif)) * 100, 2)

                        append_data("nilai_ujian", [
                            nama_siswa, kelas_siswa, mapel_siswa, topik_pilihan, skor_akhir, str(
                                date.today())
                        ])

                        st.balloons()
                        st.success(
                            f"Ujian selesai! Nilai {nama_siswa}: **{skor_akhir}** (Benar: {benar} dari {len(soal_aktif)} soal)")
        else:
            st.warning("Belum ada soal ujian di bank soal cloud.")
import json
import os
import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
        "MALKA FIRDAUS GUNAWAN", "MATAHARI TERBIT", "MEDISON PUTRA TAUFIK", "MOHAMAD FAUZAN",
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
            # Jika di secrets disimpan sebagai dictionary/tabel toml
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
        records = ws.get_all_records()
        return pd.DataFrame(records)
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

    # --- MODUL 1: AGENDA GURU ---
    if menu_guru == "Jurnal & Agenda Mengajar":
        st.header("📝 Agenda & Jurnal Guru (Tersimpan di Google Drive)")

        with st.form("form_agenda", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tgl_agenda = st.date_input("Tanggal", value=date.today())
                mapel_agenda = st.selectbox("Mata Pelajaran", DAFTAR_MAPEL)
                kelas_agenda = st.selectbox("Kelas", DAFTAR_KELAS)
            with col2:
                capaian = st.text_area(
                    "Materi / Capaian Pembelajaran", placeholder="Contoh: Logika Pemrograman / Eksponen")
                catatan = st.text_input(
                    "Catatan Khusus / Tugas Siswa", placeholder="Contoh: Diskusi kelompok, latihan mandiri")

            simpan_agenda = st.form_submit_button("Simpan Agenda Mengajar")
            if simpan_agenda:
                berhasil = append_data("agenda_guru", [
                    str(tgl_agenda), mapel_agenda, kelas_agenda, capaian, catatan
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

    # --- MODUL 2: PRESENSI SISWA ---
    elif menu_guru == "Presensi Siswa":
        st.header("📋 Presensi Kehadiran Siswa (Tersimpan di Google Drive)")
        col1, col2, col3 = st.columns(3)
        with col1:
            tgl_absen = st.date_input(
                "Tanggal Presensi", value=date.today(), key="tgl_absen")
        with col2:
            mapel_absen = st.selectbox(
                "Mata Pelajaran", DAFTAR_MAPEL, key="mapel_absen")
        with col3:
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

            submit_absen = st.form_submit_button(
                "Simpan Presensi ke Google Drive")
            if submit_absen:
                ws = get_worksheet("presensi")
                baris_baru = []
                for nama, stt in absensi_input.items():
                    baris_baru.append(
                        [str(tgl_absen), mapel_absen, kelas_absen, nama, stt])
                ws.append_rows(baris_baru)
                st.success(
                    f"Presensi {kelas_absen} berhasil diunggah permanen ke Google Sheets!")

        st.subheader(f"Rekap Presensi {kelas_absen}")
        df_absen = read_data("presensi")
        if not df_absen.empty and 'kelas' in df_absen.columns:
            df_filter = df_absen[df_absen['kelas'] == kelas_absen]
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
        st.header("✍️ Ujian Online")

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

                        # Simpan hasil ujian ke cloud Google Sheets
                        append_data("nilai_ujian", [
                            nama_siswa, kelas_siswa, mapel_siswa, topik_pilihan, skor_akhir, str(
                                date.today())
                        ])

                        st.balloons()
                        st.success(
                            f"Ujian selesai! Nilai {nama_siswa}: **{skor_akhir}** (Benar: {benar} dari {len(soal_aktif)} soal)")
        else:
            st.warning("Belum ada soal ujian di bank soal cloud.")

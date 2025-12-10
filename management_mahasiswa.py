import streamlit as st
import pandas as pd
import re
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import hashlib
import os

# ============================================
# KELAS DASAR DAN INHERITANCE
# ============================================

class Person:
    """Kelas dasar untuk merepresentasikan seseorang"""
    def __init__(self, nama: str):
        self._nama = nama
    
    @property
    def nama(self) -> str:
        return self._nama
    
    @nama.setter
    def nama(self, value: str):
        if not value.strip():
            raise ValueError("Nama tidak boleh kosong")
        self._nama = value
    
    def get_info(self) -> str:
        """Polimorfisme: Method yang akan di-override oleh subclass"""
        return f"Nama: {self._nama}"

class Mahasiswa(Person):
    """Kelas Mahasiswa yang mewarisi dari Person"""
    _total_mahasiswa = 0  # Class variable
    
    def __init__(self, nama: str, nim: str):
        super().__init__(nama)
        self._nim = nim
        self._id = Mahasiswa._total_mahasiswa + 1
        Mahasiswa._total_mahasiswa += 1
    
    @property
    def nim(self) -> str:
        return self._nim
    
    @nim.setter
    def nim(self, value: str):
        if not re.match(r'^\d+$', value):
            raise ValueError("NIM harus berupa angka")
        self._nim = value
    
    @property
    def id(self) -> int:
        return self._id
    
    def get_info(self) -> str:
        """Override method get_info dari parent class"""
        return f"ID: {self._id}, NIM: {self._nim}, Nama: {self._nama}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Mengubah objek menjadi dictionary untuk serialisasi"""
        return {
            'id': self._id,
            'nama': self._nama,
            'nim': self._nim
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mahasiswa':
        """Membuat objek Mahasiswa dari dictionary"""
        mhs = cls(data['nama'], data['nim'])
        mhs._id = data['id']
        return mhs
    
    @staticmethod
    def validate_nim(nim: str) -> bool:
        """Validasi format NIM menggunakan regex"""
        pattern = r'^\d{9,12}$'
        return bool(re.match(pattern, nim))
    
    @classmethod
    def get_total_mahasiswa(cls) -> int:
        return cls._total_mahasiswa

# ============================================
# KELAS MANAJER DATA (MENGIMPLEMENTASIKAN ARRAY & POINTER)
# ============================================

class DataManager:
    """Kelas untuk mengelola data mahasiswa menggunakan array/pointer"""
    
    def __init__(self):
        self._data: List[Mahasiswa] = []  # Array untuk menyimpan data
        self._current_index = 0  # Pointer untuk iterasi
        self._file_path = "data_mahasiswa.json"
    
    def _get_pointer(self) -> int:
        """Mendapatkan pointer saat ini"""
        return self._current_index
    
    def _set_pointer(self, index: int):
        """Mengatur pointer"""
        if 0 <= index < len(self._data):
            self._current_index = index
    
    def tambah(self, mahasiswa: Mahasiswa):
        """Menambahkan mahasiswa ke array"""
        self._data.append(mahasiswa)
        # Auto-save setelah tambah
        self.simpan_ke_file()
    
    def get_by_index(self, index: int) -> Optional[Mahasiswa]:
        """Mengakses data menggunakan pointer/indeks"""
        try:
            return self._data[index] if 0 <= index < len(self._data) else None
        except IndexError:
            return None
    
    def get_all(self) -> List[Mahasiswa]:
        """Mengembalikan semua data"""
        return self._data.copy()
    
    def get_count(self) -> int:
        """Mendapatkan jumlah data"""
        return len(self._data)
    
    def edit(self, index: int, nama: str, nim: str):
        """Mengedit data mahasiswa"""
        if 0 <= index < len(self._data):
            self._data[index].nama = nama
            self._data[index].nim = nim
            # Auto-save setelah edit
            self.simpan_ke_file()
    
    def hapus(self, index: int):
        """Menghapus data mahasiswa"""
        if 0 <= index < len(self._data):
            del self._data[index]
            # Auto-save setelah hapus
            self.simpan_ke_file()
    
    def simpan_ke_file(self):
        """Menyimpan data ke file JSON"""
        try:
            data_to_save = [mhs.to_dict() for mhs in self._data]
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Gagal menyimpan ke file: {str(e)}")
    
    def baca_dari_file(self):
        """Membaca data dari file JSON"""
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._data = [Mahasiswa.from_dict(item) for item in data]
                Mahasiswa._total_mahasiswa = max([mhs.id for mhs in self._data], default=0)
            return True
        except Exception as e:
            raise Exception(f"Gagal membaca file: {str(e)}")

# ============================================
# ALGORITMA PENCARIAN
# ============================================

class SearchAlgorithms:
    """Kelas yang mengimplementasikan berbagai algoritma pencarian"""
    
    @staticmethod
    def linear_search(data: List[Mahasiswa], keyword: str, by: str = 'nama') -> List[Mahasiswa]:
        """
        Linear Search: O(n)
        Mencari data secara berurutan
        """
        results = []
        keyword_lower = keyword.lower()
        
        for mhs in data:
            value = mhs.nama.lower() if by == 'nama' else mhs.nim
            if keyword_lower in value.lower():
                results.append(mhs)
        
        return results
    
    @staticmethod
    def binary_search(data: List[Mahasiswa], nim: str) -> Optional[Mahasiswa]:
        """
        Binary Search: O(log n)
        Hanya bekerja pada data yang sudah terurut berdasarkan NIM
        """
        # Pastikan data terurut
        sorted_data = sorted(data, key=lambda x: x.nim)
        
        low = 0
        high = len(sorted_data) - 1
        
        while low <= high:
            mid = (low + high) // 2
            mid_nim = sorted_data[mid].nim
            
            if mid_nim == nim:
                return sorted_data[mid]
            elif mid_nim < nim:
                low = mid + 1
            else:
                high = mid - 1
        
        return None
    
    @staticmethod
    def sequential_search(data: List[Mahasiswa], keyword: str) -> List[Mahasiswa]:
        """
        Sequential Search: O(n)
        Sama seperti linear search, mencari semua kemunculan
        """
        return SearchAlgorithms.linear_search(data, keyword, 'nama')

# ============================================
# ALGORITMA PENGURUTAN
# ============================================

class SortAlgorithms:
    """Kelas yang mengimplementasikan berbagai algoritma pengurutan"""
    
    @staticmethod
    def bubble_sort(data: List[Mahasiswa], by: str = 'nama') -> List[Mahasiswa]:
        """
        Bubble Sort: O(n²)
        Pengurutan dengan metode pertukaran
        """
        sorted_data = data.copy()
        n = len(sorted_data)
        
        for i in range(n):
            for j in range(0, n - i - 1):
                a = sorted_data[j].nama.lower() if by == 'nama' else sorted_data[j].nim
                b = sorted_data[j + 1].nama.lower() if by == 'nama' else sorted_data[j + 1].nim
                
                if a > b:
                    sorted_data[j], sorted_data[j + 1] = sorted_data[j + 1], sorted_data[j]
        
        return sorted_data
    
    @staticmethod
    def selection_sort(data: List[Mahasiswa], by: str = 'nama') -> List[Mahasiswa]:
        """
        Selection Sort: O(n²)
        Pengurutan dengan memilih elemen terkecil
        """
        sorted_data = data.copy()
        n = len(sorted_data)
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                a = sorted_data[min_idx].nama.lower() if by == 'nama' else sorted_data[min_idx].nim
                b = sorted_data[j].nama.lower() if by == 'nama' else sorted_data[j].nim
                
                if a > b:
                    min_idx = j
            
            sorted_data[i], sorted_data[min_idx] = sorted_data[min_idx], sorted_data[i]
        
        return sorted_data
    
    @staticmethod
    def insertion_sort(data: List[Mahasiswa], by: str = 'nama') -> List[Mahasiswa]:
        """
        Insertion Sort: O(n²)
        Pengurutan seperti mengurutkan kartu
        """
        sorted_data = data.copy()
        
        for i in range(1, len(sorted_data)):
            key = sorted_data[i]
            j = i - 1
            
            while j >= 0:
                a = sorted_data[j].nama.lower() if by == 'nama' else sorted_data[j].nim
                b = key.nama.lower() if by == 'nama' else key.nim
                
                if a > b:
                    sorted_data[j + 1] = sorted_data[j]
                    j -= 1
                else:
                    break
            
            sorted_data[j + 1] = key
        
        return sorted_data
    
    @staticmethod
    def merge_sort(data: List[Mahasiswa], by: str = 'nama') -> List[Mahasiswa]:
        """
        Merge Sort: O(n log n)
        Pengurutan dengan metode divide and conquer
        """
        if len(data) <= 1:
            return data
        
        mid = len(data) // 2
        left = SortAlgorithms.merge_sort(data[:mid], by)
        right = SortAlgorithms.merge_sort(data[mid:], by)
        
        return SortAlgorithms._merge(left, right, by)
    
    @staticmethod
    def _merge(left: List[Mahasiswa], right: List[Mahasiswa], by: str) -> List[Mahasiswa]:
        """Helper function untuk merge sort"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            a = left[i].nama.lower() if by == 'nama' else left[i].nim
            b = right[j].nama.lower() if by == 'nama' else right[j].nim
            
            if a <= b:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def shell_sort(data: List[Mahasiswa], by: str = 'nama') -> List[Mahasiswa]:
        """
        Shell Sort: O(n log n) sampai O(n²)
        Pengurutan dengan gap sequence
        """
        sorted_data = data.copy()
        n = len(sorted_data)
        gap = n // 2
        
        while gap > 0:
            for i in range(gap, n):
                temp = sorted_data[i]
                j = i
                
                while j >= gap:
                    a = sorted_data[j - gap].nama.lower() if by == 'nama' else sorted_data[j - gap].nim
                    b = temp.nama.lower() if by == 'nama' else temp.nim
                    
                    if a > b:
                        sorted_data[j] = sorted_data[j - gap]
                        j -= gap
                    else:
                        break
                
                sorted_data[j] = temp
            gap //= 2
        
        return sorted_data

# ============================================
# VALIDASI INPUT
# ============================================

class Validator:
    """Kelas untuk validasi input menggunakan regex"""
    
    @staticmethod
    def validate_nama(nama: str) -> tuple[bool, str]:
        """Validasi nama menggunakan regex"""
        pattern = r'^[A-Za-z\s\.]{3,50}$'
        if re.match(pattern, nama):
            return True, ""
        return False, "Nama harus 3-50 karakter, hanya boleh huruf dan spasi"
    
    @staticmethod
    def validate_nim(nim: str) -> tuple[bool, str]:
        """Validasi NIM menggunakan regex"""
        pattern = r'^\d{9,12}$'
        if re.match(pattern, nim):
            return True, ""
        return False, "NIM harus 9-12 digit angka"
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validasi username untuk login"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validasi password untuk login"""
        if len(password) < 6:
            return False
        return True

# ============================================
# SISTEM AUTHENTIKASI (PERBAIKAN PASSWORD)
# ============================================

class AuthSystem:
    """Kelas untuk mengelola login/logout"""
    
    def __init__(self):
        # Perbaikan: Sesuaikan dengan credential di deskripsi
        self._users = {
            'admin': self._hash_password('admin123'),
            'operator': self._hash_password('opt23')  # Diubah dari 'op123' ke 'opt23'
        }
        self.logged_in_user = None
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password menggunakan SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> bool:
        """Proses login"""
        try:
            if not Validator.validate_username(username):
                return False
            
            hashed_password = self._hash_password(password)
            
            if username in self._users and self._users[username] == hashed_password:
                self.logged_in_user = username
                return True
            return False
        except Exception as e:
            st.error(f"Error saat login: {str(e)}")
            return False
    
    def logout(self):
        """Proses logout"""
        self.logged_in_user = None
    
    def is_logged_in(self) -> bool:
        """Cek status login"""
        return self.logged_in_user is not None

# ============================================
# APLIKASI UTAMA
# ============================================

class AplikasiManajemenMahasiswa:
    """Kelas utama aplikasi"""
    
    def __init__(self):
        self.auth = AuthSystem()
        self.data_manager = DataManager()
        self.sort_algorithms = SortAlgorithms()
        self.search_algorithms = SearchAlgorithms()
        
        # Inisialisasi session state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.edit_index = None
            st.session_state.search_results = []
            st.session_state.sort_method = 'bubble'
            st.session_state.sort_by = 'nama'
        
        # Load data dari file
        try:
            self.data_manager.baca_dari_file()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def run(self):
        """Menjalankan aplikasi"""
        st.set_page_config(
            page_title="Manajemen Data Mahasiswa",
            page_icon="🎓",
            layout="wide"
        )
        
        # Sidebar untuk navigasi
        with st.sidebar:
            st.title("🎓 Sistem Login")
            
            if not self.auth.is_logged_in():
                self._show_login_form()
            else:
                self._show_logout_section()
                self._show_navigation()
        
        # Main content
        if self.auth.is_logged_in():
            self._show_main_content()
        else:
            self._show_welcome()
    
    def _show_login_form(self):
        """Menampilkan form login"""
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if self.auth.login(username, password):
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah")
    
    def _show_logout_section(self):
        """Menampilkan section logout"""
        st.success(f"👤 Login sebagai: **{self.auth.logged_in_user}**")
        if st.button("Logout", type="secondary"):
            self.auth.logout()
            st.rerun()
    
    def _show_navigation(self):
        """Menampilkan navigasi di sidebar"""
        st.title("📊 Menu")
        menu = st.radio(
            "Pilih Menu:",
            ["🏠 Dashboard", "➕ Input Data", "✏️ Edit Data", "🔍 Pencarian", 
             "📊 Pengurutan", "🗑️ Hapus Data", "📁 Ekspor/Impor", "ℹ️ Time Complexity"]
        )
        st.session_state.current_menu = menu
    
    def _show_welcome(self):
        """Menampilkan halaman welcome"""
        st.title("🎓 Selamat Datang di Aplikasi Manajemen Data Mahasiswa")
        st.markdown("""
        ### Silakan login terlebih dahulu
        **Credential Login:**
        - Username: `admin` | Password: `admin123`
        - Username: `operator` | Password: `opt23`
        
        ### Fitur Aplikasi:
        1. **Login/Logout System** - Keamanan akses
        2. **CRUD Data Mahasiswa** - Create, Read, Update, Delete
        3. **Penyimpanan File** - Auto save ke JSON
        4. **Pencarian Data** - Multiple search algorithms
        5. **Pengurutan Data** - 5 jenis sorting algorithms
        6. **Validasi Input** - Menggunakan Regex
        7. **Error Handling** - Try-catch exception
        8. **OOP Implementation** - Class, Inheritance, Polymorphism
        
        ### Data Sample:
        Aplikasi sudah berisi data 31 mahasiswa contoh
        """)
    
    def _show_main_content(self):
        """Menampilkan konten utama berdasarkan menu yang dipilih"""
        try:
            menu = st.session_state.get('current_menu', '🏠 Dashboard')
            
            if menu == "🏠 Dashboard":
                self._show_dashboard()
            elif menu == "➕ Input Data":
                self._show_input_form()
            elif menu == "✏️ Edit Data":
                self._show_edit_form()
            elif menu == "🔍 Pencarian":
                self._show_search()
            elif menu == "📊 Pengurutan":
                self._show_sorting()
            elif menu == "🗑️ Hapus Data":
                self._show_delete()
            elif menu == "📁 Ekspor/Impor":
                self._show_export_import()
            elif menu == "ℹ️ Time Complexity":
                self._show_time_complexity()
        except Exception as e:
            st.error(f"Terjadi error: {str(e)}")
            st.info("Silakan refresh halaman atau coba lagi")
    
    def _show_dashboard(self):
        """Menampilkan dashboard"""
        st.title("📊 Dashboard Manajemen Data Mahasiswa")
        
        # Statistik
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Mahasiswa", self.data_manager.get_count())
        
        with col2:
            st.metric("User Aktif", self.auth.logged_in_user)
        
        with col3:
            st.metric("Data Terakhir Diupdate", 
                     datetime.now().strftime("%d/%m/%Y"))
        
        # Tampilkan data
        st.subheader("📋 Daftar Mahasiswa")
        
        if self.data_manager.get_count() > 0:
            self._display_data_table()
        else:
            st.info("Belum ada data mahasiswa. Silakan tambah data terlebih dahulu.")
        
        # Tombol aksi cepat
        st.subheader("⚡ Aksi Cepat")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📥 Load Sample Data", use_container_width=True):
                self._load_sample_data()
        
        with col3:
            if st.button("💾 Simpan ke File", use_container_width=True):
                try:
                    self.data_manager.simpan_ke_file()
                    st.success("Data berhasil disimpan ke file!")
                except Exception as e:
                    st.error(f"Gagal menyimpan: {str(e)}")
    
    def _show_input_form(self):
        """Menampilkan form input data"""
        st.title("➕ Input Data Mahasiswa")
        
        with st.form("input_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nama = st.text_input("Nama Lengkap")
            
            with col2:
                nim = st.text_input("NIM")
            
            submitted = st.form_submit_button("Simpan Data", type="primary")
            
            if submitted:
                try:
                    # Validasi input
                    valid_nama, msg_nama = Validator.validate_nama(nama)
                    valid_nim, msg_nim = Validator.validate_nim(nim)
                    
                    if not valid_nama:
                        st.error(msg_nama)
                    elif not valid_nim:
                        st.error(msg_nim)
                    else:
                        # Cek duplikasi NIM
                        existing_nim = any(mhs.nim == nim for mhs in self.data_manager.get_all())
                        if existing_nim:
                            st.error("NIM sudah terdaftar!")
                        else:
                            # Buat objek mahasiswa dan tambahkan
                            mhs = Mahasiswa(nama, nim)
                            self.data_manager.tambah(mhs)
                            
                            # Simpan ke file
                            self.data_manager.simpan_ke_file()
                            
                            st.success(f"Data {nama} berhasil ditambahkan!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Terjadi error: {str(e)}")
        
        # Tampilkan data terbaru
        st.subheader("📋 Data Terbaru")
        if self.data_manager.get_count() > 0:
            self._display_data_table()
    
    def _show_edit_form(self):
        """Menampilkan form edit data"""
        st.title("✏️ Edit Data Mahasiswa")
        
        data = self.data_manager.get_all()
        
        if not data:
            st.info("Belum ada data untuk diedit")
            return
        
        # Pilih data yang akan diedit
        options = [f"{i+1}. {mhs.nim} - {mhs.nama}" for i, mhs in enumerate(data)]
        selected = st.selectbox("Pilih data yang akan diedit:", options)
        
        if selected:
            index = options.index(selected)
            mhs = data[index]
            
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_nama = st.text_input("Nama", value=mhs.nama)
                
                with col2:
                    new_nim = st.text_input("NIM", value=mhs.nim)
                
                submitted = st.form_submit_button("Update Data", type="primary")
                
                if submitted:
                    try:
                        # Validasi
                        valid_nama, msg_nama = Validator.validate_nama(new_nama)
                        valid_nim, msg_nim = Validator.validate_nim(new_nim)
                        
                        if not valid_nama:
                            st.error(msg_nama)
                        elif not valid_nim:
                            st.error(msg_nim)
                        else:
                            # Cek duplikasi NIM (kecuali untuk data yang sedang diedit)
                            existing_nim = any(
                                i != index and m.nim == new_nim 
                                for i, m in enumerate(data)
                            )
                            if existing_nim:
                                st.error("NIM sudah digunakan oleh mahasiswa lain!")
                            else:
                                self.data_manager.edit(index, new_nama, new_nim)
                                self.data_manager.simpan_ke_file()
                                st.success("Data berhasil diupdate!")
                                st.rerun()
                    
                    except Exception as e:
                        st.error(f"Terjadi error: {str(e)}")
    
    def _show_search(self):
        """Menampilkan fitur pencarian"""
        st.title("🔍 Pencarian Data Mahasiswa")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            keyword = st.text_input("Masukkan kata kunci pencarian:")
        
        with col2:
            search_by = st.selectbox("Cari berdasarkan:", ["Nama", "NIM"])
        
        col3, col4 = st.columns(2)
        
        with col3:
            algorithm = st.selectbox(
                "Pilih algoritma pencarian:",
                ["Linear Search", "Binary Search", "Sequential Search"]
            )
        
        with col4:
            if st.button("🔍 Cari", type="primary", use_container_width=True):
                if keyword:
                    start_time = time.time()
                    
                    try:
                        data = self.data_manager.get_all()
                        
                        if algorithm == "Linear Search":
                            results = self.search_algorithms.linear_search(
                                data, keyword, 'nama' if search_by == "Nama" else 'nim'
                            )
                        elif algorithm == "Binary Search":
                            if search_by == "NIM":
                                result = self.search_algorithms.binary_search(data, keyword)
                                results = [result] if result else []
                            else:
                                results = []
                                st.warning("Binary Search hanya untuk pencarian NIM pada data terurut")
                        else:  # Sequential Search
                            results = self.search_algorithms.sequential_search(data, keyword)
                        
                        elapsed_time = (time.time() - start_time) * 1000
                        
                        st.session_state.search_results = results
                        st.session_state.search_time = elapsed_time
                        st.session_state.search_algorithm = algorithm
                    
                    except Exception as e:
                        st.error(f"Error saat pencarian: {str(e)}")
        
        # Tampilkan hasil
        if hasattr(st.session_state, 'search_results'):
            results = st.session_state.search_results
            
            st.subheader(f"📊 Hasil Pencarian ({len(results)} data ditemukan)")
            
            if results:
                st.info(f"Algoritma: {st.session_state.search_algorithm} | "
                       f"Waktu: {st.session_state.search_time:.2f} ms")
                
                df = pd.DataFrame([
                    {"No": i+1, "NIM": m.nim, "Nama": m.nama}
                    for i, m in enumerate(results)
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Tidak ditemukan data yang sesuai")
    
    def _show_sorting(self):
        """Menampilkan fitur pengurutan"""
        st.title("📊 Pengurutan Data Mahasiswa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            algorithm = st.selectbox(
                "Pilih algoritma pengurutan:",
                ["Bubble Sort", "Selection Sort", "Insertion Sort", 
                 "Merge Sort", "Shell Sort"]
            )
        
        with col2:
            sort_by = st.selectbox("Urutkan berdasarkan:", ["Nama", "NIM"])
        
        if st.button("🔄 Urutkan Data", type="primary"):
            try:
                data = self.data_manager.get_all()
                start_time = time.time()
                
                if algorithm == "Bubble Sort":
                    sorted_data = self.sort_algorithms.bubble_sort(data, sort_by.lower())
                elif algorithm == "Selection Sort":
                    sorted_data = self.sort_algorithms.selection_sort(data, sort_by.lower())
                elif algorithm == "Insertion Sort":
                    sorted_data = self.sort_algorithms.insertion_sort(data, sort_by.lower())
                elif algorithm == "Merge Sort":
                    sorted_data = self.sort_algorithms.merge_sort(data, sort_by.lower())
                else:  # Shell Sort
                    sorted_data = self.sort_algorithms.shell_sort(data, sort_by.lower())
                
                elapsed_time = (time.time() - start_time) * 1000
                
                st.session_state.sorted_data = sorted_data
                st.session_state.sort_time = elapsed_time
                st.session_state.sort_algorithm = algorithm
            
            except Exception as e:
                st.error(f"Error saat pengurutan: {str(e)}")
        
        # Tampilkan hasil
        if hasattr(st.session_state, 'sorted_data'):
            st.subheader(f"📋 Data Terurut ({st.session_state.sort_algorithm})")
            st.info(f"Waktu eksekusi: {st.session_state.sort_time:.2f} ms")
            
            df = pd.DataFrame([
                {"No": i+1, "NIM": m.nim, "Nama": m.nama}
                for i, m in enumerate(st.session_state.sorted_data)
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    def _show_delete(self):
        """Menampilkan fitur penghapusan data"""
        st.title("🗑️ Hapus Data Mahasiswa")
        
        data = self.data_manager.get_all()
        
        if not data:
            st.info("Belum ada data untuk dihapus")
            return
        
        # Tampilkan data dengan checkbox
        st.subheader("Pilih data yang akan dihapus:")
        
        df = pd.DataFrame([
            {"Pilih": False, "No": i+1, "NIM": m.nim, "Nama": m.nama}
            for i, m in enumerate(data)
        ])
        
        edited_df = st.data_editor(
            df,
            column_config={
                "Pilih": st.column_config.CheckboxColumn(
                    "Pilih",
                    help="Pilih data untuk dihapus",
                    default=False
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("🗑️ Hapus Data Terpilih", type="primary"):
            try:
                # Dapatkan indeks yang dipilih
                selected_indices = edited_df[edited_df['Pilih']].index.tolist()
                
                if selected_indices:
                    # Hapus dari belakang untuk menjaga indeks
                    for idx in sorted(selected_indices, reverse=True):
                        self.data_manager.hapus(idx)
                    
                    self.data_manager.simpan_ke_file()
                    st.success(f"Berhasil menghapus {len(selected_indices)} data!")
                    st.rerun()
                else:
                    st.warning("Pilih minimal satu data untuk dihapus")
            
            except Exception as e:
                st.error(f"Error saat menghapus: {str(e)}")
    
    def _show_export_import(self):
        """Menampilkan fitur ekspor/impor"""
        st.title("📁 Ekspor/Impor Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💾 Ekspor Data")
            
            if st.button("📥 Download sebagai JSON", use_container_width=True):
                try:
                    self.data_manager.simpan_ke_file()
                    
                    with open("data_mahasiswa.json", "r") as f:
                        data = f.read()
                    
                    st.download_button(
                        label="Klik untuk download",
                        data=data,
                        file_name="data_mahasiswa.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            if st.button("📊 Download sebagai CSV", use_container_width=True):
                try:
                    data = self.data_manager.get_all()
                    df = pd.DataFrame([m.to_dict() for m in data])
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="Klik untuk download",
                        data=csv,
                        file_name="data_mahasiswa.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            st.subheader("📤 Impor Data")
            
            uploaded_file = st.file_uploader("Upload file JSON", type=['json'])
            
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    
                    # Validasi format
                    if isinstance(data, list):
                        imported_data = [Mahasiswa.from_dict(item) for item in data]
                        
                        if st.button("Import Data", type="primary"):
                            # Tambahkan data baru (skip duplikat NIM)
                            existing_nims = {m.nim for m in self.data_manager.get_all()}
                            added_count = 0
                            
                            for mhs in imported_data:
                                if mhs.nim not in existing_nims:
                                    self.data_manager.tambah(mhs)
                                    existing_nims.add(mhs.nim)
                                    added_count += 1
                            
                            self.data_manager.simpan_ke_file()
                            st.success(f"Berhasil mengimpor {added_count} data baru!")
                            st.rerun()
                    else:
                        st.error("Format file tidak valid!")
                
                except Exception as e:
                    st.error(f"Error membaca file: {str(e)}")
    
    def _show_time_complexity(self):
        """Menampilkan informasi time complexity"""
        st.title("ℹ️ Analisis Time Complexity")
        
        st.markdown("""
        ## Kompleksitas Waktu Algoritma
        
        ### Pencarian:
        - **Linear Search**: O(n) - Mencari satu per satu
        - **Binary Search**: O(log n) - Hanya pada data terurut
        - **Sequential Search**: O(n) - Sama seperti linear
        
        ### Pengurutan:
        - **Bubble Sort**: O(n²) - Worst case, O(n) best case
        - **Selection Sort**: O(n²) - Selalu O(n²)
        - **Insertion Sort**: O(n²) - O(n) untuk data hampir terurut
        - **Merge Sort**: O(n log n) - Stabil dan konsisten
        - **Shell Sort**: O(n log n) sampai O(n²) - Bergantung gap
        
        ### Operasi Lain:
        - **Tambah Data**: O(1) - Tambah di akhir
        - **Hapus Data**: O(n) - Perlu shifting
        - **Edit Data**: O(1) - Akses langsung
        - **Akses Data**: O(1) - Menggunakan indeks
        """)
        
        # Benchmark
        st.subheader("📈 Benchmark Performa")
        
        if st.button("Jalankan Benchmark"):
            data = self.data_manager.get_all()
            
            if data:
                results = []
                
                # Test sorting algorithms
                algorithms = [
                    ("Bubble Sort", SortAlgorithms.bubble_sort),
                    ("Selection Sort", SortAlgorithms.selection_sort),
                    ("Insertion Sort", SortAlgorithms.insertion_sort),
                    ("Merge Sort", SortAlgorithms.merge_sort),
                    ("Shell Sort", SortAlgorithms.shell_sort)
                ]
                
                for name, func in algorithms:
                    start_time = time.time()
                    func(data, 'nama')
                    elapsed = (time.time() - start_time) * 1000
                    results.append((name, elapsed))
                
                # Display results
                df = pd.DataFrame(results, columns=["Algorithm", "Time (ms)"])
                st.dataframe(df, use_container_width=True)
                
                # Chart
                st.bar_chart(df.set_index("Algorithm"))
    
    def _display_data_table(self):
        """Menampilkan data dalam tabel"""
        data = self.data_manager.get_all()
        
        df = pd.DataFrame([
            {"No": i+1, "NIM": m.nim, "Nama": m.nama}
            for i, m in enumerate(data)
        ])
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "No": st.column_config.NumberColumn(width="small"),
                "NIM": st.column_config.TextColumn(width="medium"),
                "Nama": st.column_config.TextColumn(width="large")
            }
        )
    
    def _load_sample_data(self):
        """Memuat data sample"""
        sample_data = [
            ("Azka Insan Robbani", "24101140099"),
            ("Bagus ardiansyah", "241011401958"),
            ("Fathur Rachman", "241011401713"),
            ("Tumpal Sinaga", "241011400087"),
            ("Vina Aulia", "241011401650"),
            ("Satria Apriza Fajar", "241011400103"),
            ("Davrielle saddad", "241011400085"),
            ("JANDRI HARTAT GEA", "241012402295"),
            ("Walman pangaribuan", "241011400094"),
            ("Rafli", "24011400075"),
            ("Jason Cornelius Chandra", "241011401866"),
            ("Ahmad Rasyid", "241011402663"),
            ("Ferda Ayi Sukaesih Sutanto", "241011400068"),
            ("M. Ikram Maulana", "241011402896"),
            ("Nazril Supriyadi", "241011400091"),
            ("Ade jahwa aulia", "241011402829"),
            ("Maulana ikhsan fadhillah", "241011400092"),
            ("Dea Amellya", "241011400089"),
            ("Risqi Eko Trianto", "241011402427"),
            ("Rizki Ramadani", "241011400098"),
            ("muhammad alif fajriansyah", "241011402197"),
            ("dzaki ramadhan", "241011400097"),
            ("Servatius Hasta Kristanto", "241011400076"),
            ("Ahmad Firdaus", "241011401761"),
            ("Ade sofyan", "241011402338"),
            ("Dimas Ahmad", "241011402835"),
            ("Adam Darmansyah", "241011401470"),
            ("Muhammad Noer Alam P", "241011400079"),
            ("Azmi Al Fahriza", "241011403269"),
            ("Ahmad Irfan", "241011402053"),
            ("Gregorius Gilbert Ieli Sarjana", "241011402382")
        ]
        
        try:
            # Clear existing data
            for _ in range(self.data_manager.get_count()):
                self.data_manager.hapus(0)
            
            # Add sample data
            for nama, nim in sample_data:
                mhs = Mahasiswa(nama, nim)
                self.data_manager.tambah(mhs)
            
            self.data_manager.simpan_ke_file()
            st.success("Data sample berhasil dimuat!")
            st.rerun()
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============================================
# MENJALANKAN APLIKASI
# ============================================

def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    try:
        app = AplikasiManajemenMahasiswa()
        app.run()
    
    except Exception as e:
        st.error(f"Aplikasi error: {str(e)}")
        st.info("Silakan refresh halaman atau hubungi administrator")

if __name__ == "__main__":
    main()

import mimetypes
from app.config.config import Settings, Dbconfig
from app.utils.encoder import Encoder
from app.utils.pdf_extractor import Pdfextractor
import json
import psycopg2
from psycopg2 import sql
import uuid

class Agent:
    def __init__(self):
        self.model = Settings.get_model()
        self.tbl_name = Dbconfig.TABLE_NAME
        self.db_config = {
            "user": Dbconfig.DB_USER,
            "password": Dbconfig.DB_PASS,
            "host": Dbconfig.DB_HOST,
            "port": Dbconfig.DB_PORT,
            "database": Dbconfig.DB_NAME
        }
    
    def build_prompt(self) -> str:
        return (
            """
            Anda adalah spesialis gemologi dan penilai perhiasan.
            Tugas Anda adalah menganalisis gambar dengan cermat dan memberikan deskripsi yang sangat detail, objektif, dan terperinci mengenai barang emas yang terlihat. 
            Deskripsi harus mencakup semua aspek fisik, material, dan estetika.

            Lakukan dengan instruksi seperti berikut:
            - Jika ada objek, sebutkan jumlah dan nama objek
            - Berikan balasan yang seragam untuk jenis objek seperti 'Cincin emas dengan pertama biru' menjadi 'Cincin Emas'.
            - Hitung perkiraan dimensi utama dari objek seperti panjang dan lebar atau diameter (Contoh: Diameter 18 mm, atau Panjang 35 mm, Lebar 12 mm).
            - Hanya analisa objek yang berupa emas seperti perhiasan atau batangan emas
            - Jika objek tidak teridentifikasi, berikan nama objek sebagai 'Emas Lainnya'
            - Jangan beri kalimat tambahan, jangan beri kata pengantar
            - Hanya kembalikan daftar objek yang ditemukan

            Kategori Analisis dan Detail Wajib Disediakan
            - Identitas Dasar : Jenis Barang & Jumlah(Contoh: 1 Gelang Emas Bangle, 2 Anting Emas Stud)
            - Material & Warna : Warna Emas & Perkiraan Karat(Emas Kuning Cemerlang / Rose Gold Pucat / Emas Putih 14K, dll.)
            - Dimensi Kunci : Perkiraan Ukuran(Contoh: Panjang Liontin 3 cm, Lebar Band Cincin 4 mm, Diameter 20 mm)
            - Desain Utama : Bentuk Geometris Utama(Oval, Bulat, Persegi, Tetes Air)."
            - Tekstur Permukaan : Kondisi Finishing(Dipoles mengilap/High-Polish, Matte/Dof, Bertekstur/Hammered, Satin Finish)
            - Fitur Detail : Detail Dekoratif(Uliran/Mille-Grains, Pola Spiral, Ukiran Bunga/Floral Engraving, Filigree)
            - Pengikatan Batu (Jika Ada) : Mata Cincin & Setting(Bentuk Batu: Bulat/Marquise; Jenis Setting: Prong/Bezel/Pavé)

            Output harus berupa JSON. Jadikan JSON sebagai List/Array. JSON memiliki key berikut :
            1. nama_barang -> Tipe data STRING
            2. jenis_barang -> Tipe data STRING
            3. jumlah_barang -> Tipe data INTEGER
            4. dimensi -> Tipe data STRING
            5. deskripsi -> Tipe data TEXT

            Contoh:
            [
            {
                "nama_barang": "Cincin Emas Putih Tiga Batu (Trilogy Ring)",
                "jenis_barang": "Cincin Emas",
                "jumlah_barang": 1,
                "dimensi": "Diameter 17.3 mm (Ukuran US 7)",
                "deskripsi": "Cincin terbuat dari Emas Putih (perkiraan 18K) dengan hasil akhir High-Polish yang cemerlang di seluruh band. Band cincin memiliki taper (penyempitan) di dekat kepala cincin, dengan lebar minimal 2.5 mm. Desain Trilogy menampilkan tiga batu mulia: satu berlian utama berbentuk Round Brilliant Cut berukuran sekitar 5.0 mm (sekitar 0.5 ct), diapit oleh dua berlian Round Brilliant Cut yang lebih kecil, masing-masing berukuran 3.0 mm. Semua batu diikat menggunakan Setting Prong 4-cakar. Tidak ada uliran atau ukiran tambahan pada permukaan band."
            }
            ]

            Contoh lainnya:
            [
            {
                "nama_barang": "Sepasang Anting Stud Berlian",
                "jenis_barang": "Anting Berlian",
                "jumlah_barang": 2,
                "dimensi": "Panjang 30 mm dan Lebar 15 mm",
                "deskripsi": "Sepasang Anting Stud (kancing) yang terbuat dari Emas Putih (perkiraan 14K) dengan finishing High-Polish. Setiap anting memiliki satu batu mulia utama berbentuk Round Brilliant Cut berdiameter sekitar 4.0 mm (sekitar 0.25 ct per anting). Batu-batu tersebut diikat menggunakan Setting Prong 4-cakar yang ramping, dan ditopang oleh kerangka emas kecil. Tiang (post) anting terlihat lurus tanpa uliran."
            },
            {
                "nama_barang": "Liontin Medali Emas Kuning Berukir",
                "jenis_barang": "Liontin Emas",
                "jumlah_barang": 1,
                "dimensi": "Panjang 40 mm dan Lebar 25 mm",
                "deskripsi": "Satu Liontin berbentuk Medali Bundar Emas Kuning (perkiraan 22K) dengan diameter 30 mm. Permukaan medali memiliki dua tekstur: bingkai luar memiliki tekstur Matte, sementara bagian tengahnya menampilkan ukiran relief mendalam dari figur mitologis dengan rambut yang sangat detail. Ukiran ini memiliki permukaan yang dipoles mengilap, menciptakan kontras visual. Medali digantung pada Bail berbentuk oval sederhana."
            }
            ]
            """
            
            #"Analisis file ini dan kembalikan hasil dalam format yang sangat ringkas:\n"
            # "- Jika ada objek, sebutkan jumlah dan nama objek, pisahkan dengan koma jika lebih dari satu.\n"
            #"- Berikan balasan yang seragam, seperti '1 Cincin emas dengan pertama biru' menjadi '1 Cincin Emas'.\n"
            #"- Jika ada dokumen, sebutkan jenis dokumen (contoh: '1 surat kepemilikan tanah', '1 KTP').\n"
            #"- '1 Surat Kepemilikan Tanah di Kota Jakarta' menjadi '1 Surat Kepemilikan Tanah'"
            # "- Hanya analisa objek yang berupa emas seperti perhiasan atau batangan emas"
            # "- Berikan balasan dengan menyebutkan nama barang dan deskripsi dari barang tersebut seperti bentuk"
            # "- Jangan beri kalimat tambahan, jangan beri kata pengantar.\n"
            # "- Hanya kembalikan daftar objek/dokumen yang ditemukan."
        )

    def analyze_file(self, file_path: str, mime_type:str = None) -> list:
        print(f"DEBUG: File {file_path} | MIME dari UI: {mime_type}")
        parts = []
        # mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type or mime_type == "application/octet-stream":
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            print(f"DEBUG: MIME fallback dari mimetypes: {mime_type}")

        # 🔧 Fallback manual kalau tetap None
        if not mime_type:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".png":
                mime_type = "image/png"
            elif ext == ".pdf":
                mime_type = "application/pdf"

        if not mime_type:
            raise ValueError(f"❌ Tidak bisa mengenali tipe file: {file_path}")
        
        # PDF handling
        if mime_type == "application/pdf":
            text = Pdfextractor.exctract_doc(file_path)
            if text:
                parts.append({"text": text})
            else:
                base64_data = Encoder.file_to_base64(file_path)
                parts.append({"inline_data": {"mime_type": "application/pdf", "data": base64_data}})
        elif mime_type.startswith("image/"):
            base64_data = Encoder.file_to_base64(file_path)
            parts.append({"inline_data": {"mime_type": mime_type, "data": base64_data}})
        else:
            raise ValueError(f"Mime type '{mime_type}' tidak didukung")
        
        prompt = self.build_prompt()
        response = self.model.generate_content([{"text": prompt}, *parts])
        raw_text = response.text

        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.strip("```json").strip()
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text.strip("```").strip()

        try:
            json_data = json.loads(cleaned_text)
            id_transaksi_dokumen = str(uuid.uuid4())
            saved_ids = []

            if not isinstance(json_data, list):
                print("❌ Output JSON tidak berupa List. Menganggapnya sebagai satu item.")
                json_data = [json_data]

            for item_data in json_data:
                if not isinstance(item_data, dict):
                    print("Peringatan: Melewati item non-dictionary dalam list.")
                    continue

                item_uuid = self.save_result(id_transaksi_dokumen, item_data)

                if item_uuid:
                    saved_ids.append(item_uuid)

            if saved_ids:
                print(f"✅ Transaksi ID {id_transaksi_dokumen}: Total {len(saved_ids)} item berhasil disimpan.")
            else:
                print("❌ Gagal menyimpan data, tidak ada item yang berhasil disimpan.")
            # hasil_input = self.save_result(json_data)
            # if hasil_input:
            #     print(f"✅ Data berhasil disimpan dengan ID {hasil_input}.")
            # else:
            #     print("❌ Gagal menyimpan data ke DB, hanya mengembalikan hasil mentah.")
            #     return json_data
            return json_data
        except json.JSONDecodeError:
            print(f"Error parsing JSON: {e}")
            print(f"Original text: {raw_text}")
            return {"error": "JSON_PARSE_FAILURE", "raw_output": raw_text}
        
    def save_result(self, document_id: str, result_json: dict):
        """
        Simpan hasil analisis AI ke database
        """

        conn = None
        try:
            new_uuid = uuid.uuid4()

            conn = psycopg2.connect(**self.db_config)
            curr = conn.cursor()

            insert_data = {
                "id": str(new_uuid),
                "document_id": document_id,
                "nama_barang": result_json.get("nama_barang"),
                "jenis_barang": result_json.get("jenis_barang"),
                "jumlah_barang": int(result_json.get("jumlah_barang")),
                "dimensi": result_json.get("dimensi"),
                "deskripsi": result_json.get("deskripsi")
            }

            kolom = insert_data.keys()
            value = insert_data.values()

            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(self.tbl_name),
                sql.SQL(', ').join(map(sql.Identifier, kolom)),
                sql.SQL(', ').join(sql.Placeholder() * len(kolom))
            )

            curr.execute(insert_query, list(value))
            conn.commit()
            print(f"✅ Berhasil menyimpan hasil dengan ID: {new_uuid}")
            return new_uuid
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Terjadi kesalahan saat menyimpan data: {error}")
            if conn:
                conn.rollback()
                return f"Gagal menyimpan data"
        finally:
            if conn:
                curr.close()
                conn.close()
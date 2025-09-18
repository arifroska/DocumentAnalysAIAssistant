import streamlit as st
import tempfile
import os
from service.agent import Agent

def run():
    st.set_page_config(page_title="AI Dokumen & Gambar Analyzer", layout="centered")
    st.title("📑 AI Analyzer")
    st.write("Upload satu atau lebih file (gambar/dokumen PDF) lalu biarkan AI menjelaskan isinya.")

    uploaded_files = st.file_uploader(
        "Drag & Drop file di sini", 
        type=["png", "jpg", "jpeg", "pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"{len(uploaded_files)} file diupload.")
        if st.button("Analisis Semua File"):
            agent = Agent()
            results = []

            progress = st.progress(0)
            total_files = len(uploaded_files)

            with st.spinner("⏳ Menganalisis semua file..."):
                for idx, file in enumerate(uploaded_files, start=1):
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(file.read())
                        temp_file_path = tmp.name

                    hasil = agent.analyze_file(temp_file_path, mime_type=file.type)
                    # results.append((file.name, hasil))
                    results.append(hasil)

                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)

                    # Update progress bar
                    progress.progress(idx / total_files)

            st.success("✅ Analisis semua file selesai!")
            gabungan = ", ".join([r.strip() for r in results if r.strip() != ""])
            st.subheader("Hasil Analisis:")
            st.text_area("", gabungan, height=150)

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time, timedelta

def run():
        
    if st.button("🔙 Kembali ke Beranda"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown(
        """
        <h1 style='text-align: center; color: white; background-color: #F9E79F; padding: 15px; border-radius: 10px;'>
            ✏️ Update Data Preventive
        </h1>
        """,
        unsafe_allow_html=True
    )

    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx6y1WeK9o4LItHUOxvw_HJnO92lCprypFEqfruWwjMwW1ViLoZVBByaSZGtMVqiK4/exec"

    def get_all_data():
        try:
            response = requests.get(APPS_SCRIPT_URL, params={"action": "get_ALL"}, timeout=20)
            response.raise_for_status()
            return response.json().get("data", [])
        except:
            return []

    def get_database_sp():
        try:
            response = requests.get(APPS_SCRIPT_URL, params={"action": "get_DatabaseSP"}, timeout=20)
            response.raise_for_status()
            return response.json().get("data", [])
        except:
            return []

    def update_data_to_all(form_data):
        try:
            response = requests.post(APPS_SCRIPT_URL, json=form_data, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}

    all_data = get_all_data()
    database_sp = get_database_sp()

    if all_data:
        df = pd.DataFrame(all_data)
        id_list = df["ID"].astype(str).unique().tolist()
        selected_id = st.selectbox("Pilih ID yang ingin diupdate", id_list)

        selected_row = df[df["ID"].astype(str) == selected_id].iloc[0]
        approve_status = str(selected_row.get("Approve", "")).strip().lower()
        kondisi_status = str(selected_row.get("Kondisi", "")).strip().lower()

        if approve_status == "approved" or kondisi_status in ["close", "done"]:
            if approve_status == "approved" and kondisi_status in ["close", "done"]:
                st.warning("🔒 Data ini tidak dapat diedit karena sudah disetujui oleh SM dan SPV")
            elif approve_status == "approved":
                st.warning("🔒 Data ini tidak dapat diedit karena status sudah 'Approved' oleh SM.")
            elif kondisi_status in ["close", "done"]:
                st.warning("🔒 Data ini tidak dapat diedit karena status sudah 'Close' / 'Done' oleh SPV.")
            return

        spk_info = pd.DataFrame([{
            "ID_SPK": selected_id,
            "BU": selected_row["BU"],
            "Line": selected_row["Line"],
            "Produk": selected_row["Produk"],
            "Mesin": selected_row["Mesin"],
            "Nomor Mesin": selected_row["Nomor Mesin"],
            "Tanggal": pd.to_datetime(selected_row['Tanggal Pengerjaan'], errors='coerce').date(),
            "Masalah": selected_row['Masalah'],
            "PIC": selected_row['PIC']
        }])
        st.markdown("#### Data dari SPK")
        st.dataframe(spk_info, use_container_width=True)

        st.markdown("### 🔧 Form Update Data")

        tanggal_raw = pd.to_datetime(selected_row.get("Tanggal Pengerjaan", ""), errors='coerce')
        tanggal_display = tanggal_raw.strftime("%d-%b-%Y") if pd.notnull(tanggal_raw) else "-"
        st.markdown(f"📅 **Tanggal SPK:** `{tanggal_display}`")

        mulai_str = selected_row.get("Mulai", "00:00")
        try:
            mulai_time = datetime.strptime(mulai_str, "%H:%M").time()
        except ValueError:
            mulai_time = time(0, 0)
        mulai = st.time_input("Jam Mulai", value=mulai_time)

        selesai_str = selected_row.get("Selesai", "00:00")
        try:
            selesai_time = datetime.strptime(selesai_str, "%H:%M").time()
        except ValueError:
            selesai_time = time(0, 0)
        selesai = st.time_input("Jam Selesai", value=selesai_time)

        start_dt = datetime.combine(datetime.today(), mulai)
        end_dt = datetime.combine(datetime.today(), selesai)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        durasi_timedelta = end_dt - start_dt
        durasi_str = (datetime(1900, 1, 1) + durasi_timedelta).time().strftime("%H:%M")
        st.info(f"⏱ Total Durasi: {durasi_str} jam")

        tindakan = st.text_area("Tindakan Perbaikan", value=str(selected_row.get("Tindakan Perbaikan", "")))

        bu_filter = selected_row['BU']
        df_sp_db = pd.DataFrame(database_sp)
        filtered_db = df_sp_db[df_sp_db['BU'] == bu_filter]
        unique_descriptions = filtered_db['Deskripsi'].dropna().unique().tolist()

        selected_items = st.multiselect("Pilih Deskripsi Sparepart", unique_descriptions)

        uom_values = []
        edited_df = pd.DataFrame(columns=["Item", "UOM", "Quantity"])

        if selected_items:
            uom_values = [
                filtered_db.loc[filtered_db['Deskripsi'] == item, 'UOM'].values[0]
                if not filtered_db.loc[filtered_db['Deskripsi'] == item, 'UOM'].empty
                else "UNKNOWN"
                for item in selected_items
            ]
            data = {'Item': selected_items, 'UOM': uom_values, 'Quantity': [0] * len(selected_items)}
            df_sp_input = pd.DataFrame(data)
            edited_df = st.data_editor(df_sp_input, key="data_editor", disabled=["Item", "UOM"])
        else:
            st.info("ℹ️ Tidak memilih sparepart. Anda tetap bisa melanjutkan update.")

        if st.button("Update Data"):
            if durasi_timedelta.total_seconds() == 0:
                    st.error("⚠ Durasi tidak boleh 0. Periksa kembali jam mulai dan selesai.")
            else:
                deskripsi = edited_df["Item"].tolist() if not edited_df.empty else []
                quantity = edited_df["Quantity"].tolist() if not edited_df.empty else []
                delimiter = "||"
                
                data_to_send = {
                    "action": "update_data",
                    "ID_SPK": selected_id,
                    "BU": str(selected_row['BU']),
                    "Line": str(selected_row['Line']),
                    "Produk": str(selected_row['Produk']),
                    "Mesin": str(selected_row['Mesin']),
                    "Nomor": str(selected_row['Nomor Mesin']),
                    "Tanggal": str(selected_row['Tanggal Pengerjaan']),
                    "Mulai": mulai.strftime("%H:%M"),
                    "Selesai": selesai.strftime("%H:%M"),
                    "Masalah": str(selected_row['Masalah']),
                    "Tindakan": tindakan,
                    "Deskripsi": delimiter.join(deskripsi),
                    "Quantity": delimiter.join(map(str, quantity)),
                    "PIC": str(selected_row['PIC']),
                    "Durasi": durasi_str,
                }


                res = update_data_to_all(data_to_send)
                if res.get("status") == "success":
                    st.success("✅ Berhasil memperbarui data!")
                else:
                    st.error("❌ Gagal memperbarui data: Tidak ada ID SPK yang dipilih")

    # else:
    #     st.warning("Tidak ada data yang tersedia untuk diupdate.")

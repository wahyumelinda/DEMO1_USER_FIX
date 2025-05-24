import streamlit as st

st.set_page_config(page_title="Landing Page Preventive", page_icon="🛠️", layout="wide")

# Inisialisasi session_state untuk navigasi
if "page" not in st.session_state:
    st.session_state.page = "home"

# Fungsi navigasi
def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()  # rerun agar bisa navigasi ke file lain


# Landing Page
if st.session_state.page == "home":
    st.markdown("""
        <h1 style='text-align: center; background-color: #82E0AA; padding: 20px; border-radius: 10px; color: black;'>
            🛠️ Sistem Manajemen Data Preventive
        </h1>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("")
        if st.button("➕ Tambah Data Preventive", use_container_width=True):
            go_to("add")

        if st.button("✏️ Update Data Preventive", use_container_width=True):
            go_to("update")

# Halaman Tambah Data
elif st.session_state.page == "add":
    import add_user
    add_user.run()

# Halaman Update Data
elif st.session_state.page == "update":
    import update_user_fix
    update_user_fix.run()

st.markdown("---")
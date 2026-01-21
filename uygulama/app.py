import streamlit as st
import joblib
import pandas as pd

# 1. Sayfa Ayarları
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# 2. Tasarım Kodları (MAVİ TEMA)
st.markdown("""
<style>
    /* GENEL ARKAPLAN */
    .stApp { background-color: #F2F2F7 !important; }
    h1, h2, h3, h4, h5, p, span, div, label { color: #1C1C1E !important; }

    /* KARTLAR (BEYAZ KUTULAR) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* BUTONLAR */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }

    /* --- MENÜ (MAVİ YAPILANDIRMA) --- */
    
    /* 1. Seçim Kutusunun Kendisi */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #007AFF !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    /* Kutunun içindeki yazı rengi */
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
    }
    
    /* Sağdaki ok simgesi */
    .stSelectbox svg {
        fill: white !important;
    }

    /* 2. Açılan Liste (POPOVER) */
    div[data-baseweb="popover"] {
        background-color: #007AFF !important;
        border: 1px solid white !important;
    }

    /* 3. Listenin İçindeki Seçenekler */
    ul[data-baseweb="menu"] {
        background-color: #007AFF !important;
    }
    ul[data-baseweb="menu"] li {
        background-color: #007AFF !important;
        color: white !important;
    }
    
    /* Seçeneğin üzerine gelince koyulaşsın */
    ul[data-baseweb="menu"] li:hover {
        background-color: #0056b3 !important;
    }

    /* --- SAYI GİRİŞ KUTUSU --- */
    .stNumberInput div[data-baseweb="input"] {
        background-color: #E5F1FF !important;
        border: 1px solid #007AFF !important;

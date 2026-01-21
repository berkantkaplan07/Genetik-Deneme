import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS: FULL MAVİ TASARIM (MAVİ LİSTE DAHİL) ---
css_kodu = """
<style>
    /* 1. Ana Arkaplan */
    .stApp { background-color: #F2F2F7 !important; }
    h1, h2, h3, h4, h5, p, span, div, label, .stMarkdown { color: #1C1C1E !important; }
    
    /* 2. Beyaz Kartlar */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 3. Butonlar */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    
    /* --- MENÜ DÜZELTME (İŞTE BURASI!) --- */
    
    /* 1. Seçim Kutusunun Kendisi (Kapalıyken) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #007AFF !important; /* Mavi */
        color: white !important;              /* Beyaz Yazı */
        border: none !important;
        border-radius: 10px !important;
    }
    /* Kutunun içindeki seçili yazı */
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
    }
    /* Sağdaki ok simgesi */
    .stSelectbox svg {
        fill: white !important;
    }
    
    /* 2. AÇILAN LİSTE KUTUSU (POPOVER) - O SİYAH YER */
    div[data-baseweb="popover"] {
        background-color: #007AFF !important; /* Arkaplanı Maviye Zorla */
        border: 1px solid white !important;
    }
    
    /* 3. LİSTENİN İÇİNDEKİ SEÇENEKLER */
    ul[data-baseweb="menu"] {
        background-color: #0

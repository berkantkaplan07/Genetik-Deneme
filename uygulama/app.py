import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS: RENK VE TASARIM AYARLARI ---
st.markdown("""
    <style>
    /* 1. Tüm Sayfa Arkaplanı */
    .stApp {
        background-color: #F2F2F7 !important;
    }
    
    /* 2. Tüm Ana Metinler */
    h1, h2, h3, h4, h5, p, span, div, label {
        color: #1C1C1E !important;
    }
    
    /* 3. Kartlar (Beyaz Kutular) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 4. Butonlar */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* --- DROPDOWN (AÇILIR MENÜ) DÜZELTME --- */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important

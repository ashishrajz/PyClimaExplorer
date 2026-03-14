import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PyClimaExplorer", page_icon="🌍", layout="wide")

st.markdown("""
<style>
* { margin: 0; padding: 0; }
.stApp { background: #020b18; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.block-container { padding: 0 !important; }
.stApp > div > div > div > div { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

with open("landing.html", "r", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=1000, scrolling=True)

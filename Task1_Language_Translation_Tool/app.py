"""CodeAlpha - Task 1 : Language Translation Tool
Interface Streamlit + Google Translate (via deep-translator) + synthèse vocale (gTTS).
Lancer : streamlit run app.py
"""
import textwrap
from io import BytesIO
from urllib.parse import quote

import requests
import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from gtts import gTTS

AUTO = "Détection automatique"
MAX_CHARS = 5000

st.set_page_config(page_title="Traducteur CodeAlpha", page_icon="🌍", layout="wide")


@st.cache_data(show_spinner=False)
def get_languages() -> dict:
    """Retourne {Nom: code}, ex. {'French': 'fr'}."""
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    return {name.title(): code for name, code in sorted(langs.items())}


def _is_rate_limit(err) -> bool:
    msg = str(err).lower()
    return "too many requests" in msg or "429" in msg


def _engine_google(text, src_name, tgt_name):
    src = "auto" if src_name == AUTO else LANGS[src_name]
    return GoogleTranslator(source=src, target=LANGS[tgt_name]).translate(text)


def _engine_mymemory(text, src_name, tgt_name):
    """Limité à ~500 caractères par requête ; ne détecte pas la langue seul."""
    if src_name == AUTO:
        from langdetect import detect

        code_to_name = {c: n for n, c in LANGS.items()}
        src_name = code_to_name.get(detect(text).split("-")[0], "English")
    tr = MyMemoryTranslator(source=src_name.lower(), target=tgt_name.lower())
    chunks = textwrap.wrap(text, 450, replace_whitespace=False)
    return " ".join(tr.translate(c) for c in chunks)


LINGVA_INSTANCES = ["https://lingva.ml", "https://lingva.lunar.icu", "https://translate.plausibility.cloud"]


def _engine_lingva(text, src_name, tgt_name):
    """Passe par un serveur public (Lingva) : contourne le blocage de votre IP."""
    src = "auto" if src_name == AUTO else LANGS[src_name]
    tgt = LANGS[tgt_name]
    last = None
    for base in LINGVA_INSTANCES:
        try:
            parts = []
            for chunk in textwrap.wrap(text, 800, replace_whitespace=False):
                r = requests.get(f"{base}/api/v1/{src}/{tgt}/{quote(chunk, safe='')}", timeout=10)
                r.raise_for_status()
                parts.append(r.json()["translation"])
            return " ".join(parts)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


ENGINES = [
    ("Google Translate", _engine_google),
    ("MyMemory (plan B)", _engine_mymemory),
    ("Lingva (plan C)", _engine_lingva),
]


@st.cache_data(show_spinner=False)
def translate(text: str, src_name: str, tgt_name: str) -> tuple[str, str]:
    """Essaie chaque moteur dans l'ordre. Retourne (traduction, moteur)."""
    errors = []
    for name, fn in ENGINES:
        try:
            return fn(text, src_name, tgt_name), name
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name} : {e}")
    raise RuntimeError("\n\n".join(errors))


def speak(text: str, lang_code: str) -> bytes | None:
    try:
        buf = BytesIO()
        gTTS(text=text, lang=lang_code).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None  # langue non supportée par gTTS ou pas de connexion


LANGS = get_languages()
NAMES = list(LANGS.keys())

# --- état par défaut + bouton d'inversion ---
st.session_state.setdefault("src", AUTO)
st.session_state.setdefault("tgt", "French" if "French" in NAMES else NAMES[0])
st.session_state.setdefault("history", [])


def swap_languages():
    if st.session_state.src != AUTO:
        st.session_state.src, st.session_state.tgt = (
            st.session_state.tgt,
            st.session_state.src,
        )


# --- interface ---
st.title("🌍 Language Translation Tool")
st.caption("CodeAlpha AI Internship – Task 1")

c1, c2, c3 = st.columns([5, 1, 5])
c1.selectbox("Langue source", [AUTO] + NAMES, key="src")
c2.button("⇄", on_click=swap_languages, help="Inverser les langues", use_container_width=True)
c3.selectbox("Langue cible", NAMES, key="tgt")

left, right = st.columns(2)
with left:
    text = st.text_area("Texte à traduire", height=250, max_chars=MAX_CHARS,
                        placeholder="Écrivez ou collez votre texte ici...")
    go = st.button("Traduire", type="primary", use_container_width=True)

with right:
    st.markdown("**Traduction**")
    if go:
        if not text.strip():
            st.warning("Veuillez saisir un texte.")
        else:
            try:
                with st.spinner("Traduction en cours..."):
                    result, engine = translate(text, st.session_state.src, st.session_state.tgt)
                tgt_code = LANGS[st.session_state.tgt]
                # st.code affiche un bouton "copier" intégré
                st.code(result, language=None, wrap_lines=True)
                st.caption(f"Moteur : {engine}")
                audio = speak(result, tgt_code)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.caption("🔇 Synthèse vocale indisponible pour cette langue.")
                st.session_state.history.insert(
                    0, (text[:60], result[:60], st.session_state.src, st.session_state.tgt)
                )
            except Exception as e:
                st.error(" Aucun moteur de traduction n'a répondu (Google bloque probablement votre connexion). "
                         "Essayez avec le partage de connexion de votre téléphone ou réessayez plus tard.")
                with st.expander("Détails techniques"):
                    st.code(str(e), language=None, wrap_lines=True)

if st.session_state.history:
    with st.expander(" Historique"):
        for original, translated, s, t in st.session_state.history[:10]:
            st.write(f"**{s} → {t}** : {original} ➜ {translated}")
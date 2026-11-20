"""CodeAlpha - Task 2 : Chatbot FAQ (interface de chat Streamlit).
Lancer : streamlit run app.py
"""
import streamlit as st

from chatbot import FAQChatbot

st.set_page_config(page_title="Chatbot FAQ CodeAlpha", page_icon="🤖")


@st.cache_resource(show_spinner="Chargement du chatbot...")
def get_bot() -> FAQChatbot:
    return FAQChatbot()


bot = get_bot()

# ---------- Barre latérale ----------
with st.sidebar:
    st.header("⚙️ Options")
    bot.threshold = st.slider("Seuil de confiance", 0.05, 0.80, 0.25, 0.05,
                              help="En dessous de ce score, le bot dit qu'il ne sait pas.")
    show_debug = st.checkbox("Afficher le score de similarité", value=True)
    st.divider()
    st.subheader("💡 Questions d'exemple")
    for item in bot.faq[:6]:
        if st.button(item["question"], use_container_width=True):
            st.session_state.pending = item["question"]
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []

# ---------- Conversation ----------
st.title("🤖 Chatbot FAQ – Stage IA CodeAlpha")
st.caption("CodeAlpha AI Internship – Task 2 · NLTK + TF-IDF + similarité cosinus")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Bonjour ! 👋 Posez-moi vos questions sur le stage IA de CodeAlpha "
                    "(tâches, certificat, soumission, contact...)."}
    ]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("debug") and show_debug:
            st.caption(m["debug"])

prompt = st.chat_input("Écrivez votre question...") or st.session_state.pop("pending", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    result = bot.ask(prompt)
    debug = None
    if not result.intent:
        debug = f"Score : {result.score:.2f}"
        if result.matched_question:
            debug += f" · FAQ associée : « {result.matched_question} »"

    with st.chat_message("assistant"):
        st.markdown(result.text)
        if debug and show_debug:
            st.caption(debug)
        if result.suggestions:
            st.caption("Questions proches : " + " | ".join(q for q, _ in result.suggestions))
    st.session_state.messages.append({"role": "assistant", "content": result.text, "debug": debug})

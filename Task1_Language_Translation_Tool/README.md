# 🌍 CodeAlpha_LanguageTranslationTool

> **CodeAlpha AI Internship – Task 1: Language Translation Tool**

A web application that translates text between more than 100 languages. The user types a text, picks a source and a target language, and gets the translation instantly, with a copy button and text-to-speech.

## ✨ Features

- Clean web interface built with **Streamlit**
- Source language selection (or **automatic detection**) and target language selection
- Translation through the **Google Translate API** (via the `deep-translator` library)
- **Automatic fallback engines** (MyMemory, then Lingva) if Google rate-limits the connection
- 📋 **Copy button** on the translated text
- 🔊 **Text-to-speech** of the translation (gTTS)
- ⇄ One-click **language swap** and a **translation history**
- Friendly error messages and a technical-details panel

## 🛠️ Tech Stack

| Purpose | Tool |
|---|---|
| Interface | Streamlit |
| Translation | deep-translator (Google Translate), MyMemory, Lingva |
| Text-to-speech | gTTS |
| Language | Python 3.9+ |

## 📁 Project Structure

```
CodeAlpha_LanguageTranslationTool/
├── app.py            # Streamlit application (UI + translation engines)
├── test_moteurs.py   # Diagnostic script: tests each translation engine
├── requirements.txt  # Dependencies
└── README.md
```

## 🚀 Installation & Usage

```bash
git clone https://github.com/<aminaelbayyadi>/CodeAlpha_LanguageTranslationTool.git
cd CodeAlpha_LanguageTranslationTool
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## ⚙️ How It Works

1. The user enters a text (up to 5,000 characters) and chooses the languages.
2. The text is sent to the first available engine: **Google Translate → MyMemory → Lingva**.
3. The translation is displayed with a copy button, the engine used, and an audio player.

## 🩺 Troubleshooting

| Problem | Solution |
|---|---|
| `Too many requests` error | Google temporarily blocked your IP. Wait a few minutes, disable your VPN, or use a mobile hotspot. The fallback engines take over automatically. |
| Check which engine works on your network | Run `python test_moteurs.py` |
| No audio for a language | Text-to-speech is not available for every language; the translation still works. |

## 👩‍💻 Author

**Amina ELBAYYADI** – Master’s Degree in Big Data & AI
LinkedIn: `<https://www.linkedin.com/in/amina-elbayyadi/>`

---
*Developed as part of the CodeAlpha Artificial Intelligence Internship.*
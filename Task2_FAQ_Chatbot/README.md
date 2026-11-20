# 🤖 CodeAlpha_FAQChatbot

> **CodeAlpha AI Internship – Task 2: Chatbot for FAQs**

A chatbot that answers frequently asked questions about the CodeAlpha AI internship program (tasks, certificate, submission, contact). It uses classic NLP: text preprocessing with **NLTK**, **TF-IDF** vectors, and **cosine similarity** to find the FAQ entry closest to the user's question.

## ✨ Features

- 19 FAQ entries (questions + answers) stored in a simple `faq.json` file
- NLP preprocessing: lowercasing, tokenization, French stop-word removal, stemming, unigrams + bigrams
- Best-match retrieval using **TF-IDF + cosine similarity**
- Confidence threshold with a "Did you mean…?" suggestion zone and fallback message
- Simple **intent matching** for greetings, thanks and goodbyes
- Chat interface with Streamlit (example questions, adjustable threshold, similarity score display)
- Console mode and automated tests

## 🛠️ Tech Stack

| Purpose | Tool |
|---|---|
| NLP preprocessing | NLTK (tokenizer, stop words, Snowball stemmer) |
| Vectorization & similarity | scikit-learn (TfidfVectorizer, cosine_similarity) |
| Chat UI | Streamlit |
| Language | Python 3.9+ |

## 📁 Project Structure

```
CodeAlpha_FAQChatbot/
├── app.py             # Streamlit chat interface
├── chatbot.py         # NLP pipeline + matching engine
├── faq.json           # FAQ knowledge base
├── test_chatbot.py    # Automated matching tests
├── requirements.txt
└── README.md
```

## 🚀 Installation & Usage

```bash
git clone https://github.com/<aminaelbayyadi>/CodeAlpha_FAQChatbot.git
cd CodeAlpha_FAQChatbot
pip install -r requirements.txt

streamlit run app.py        # chat interface
python chatbot.py           # console mode
python test_chatbot.py      # run the tests
```

## ⚙️ How It Works

```
User question
   → lowercase → tokenize → remove stop words → stem → unigrams + bigrams
   → TF-IDF vector
   → cosine similarity with every FAQ entry
   → best score ≥ threshold ?  yes → return the answer
                               no  → suggest the closest questions
```

1. **Collect**: each FAQ entry has a `question`, `keywords` (synonyms) and an `answer`.
2. **Preprocess**: the same pipeline is applied to the FAQ and to every user message.
3. **Match**: the similarity score (0 to 1) is computed against all entries; the best one wins.
4. **Respond**: if the score is below the threshold, the bot asks the user to rephrase and proposes close questions.

## ➕ Adding Your Own FAQ

Add an object to `faq.json`:

```json
{
  "category": "Topic",
  "question": "Your question?",
  "keywords": "synonyms and related words",
  "answer": "Your answer."
}
```

## 👩‍💻 Author

**Amina ELBAYYADI** – Master’s Degree in Big Data & AI
LinkedIn: `<https://www.linkedin.com/in/amina-elbayyadi/>`

---
*Developed as part of the CodeAlpha Artificial Intelligence Internship.*
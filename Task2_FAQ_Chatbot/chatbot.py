"""Moteur du chatbot FAQ : NLTK (prétraitement) + TF-IDF + similarité cosinus."""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import nltk
from nltk.stem.snowball import FrenchStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_PATH = Path(__file__).parent / "faq.json"

# Liste de secours si le téléchargement des stopwords NLTK échoue (pas d'internet)
FALLBACK_STOPWORDS = (
    "au aux avec ce ces dans de des du elle en et eux il je la le les leur lui ma mais me meme mes moi mon ne nos "
    "notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous c d j l "
    "a m n s t y est sont suis es sommes etes etre ete fait faire peut puis dois doit faut ai as avons avez ont "
    "quel quelle quels quelles quoi comment ou est-ce"
).split()

INTENTS = [
    (r"^(salut|bonjour|bonsoir|hello|hey|coucou)\b",
     "Bonjour ! 👋 Je réponds à vos questions sur le stage IA de CodeAlpha. Que voulez-vous savoir ?"),
    (r"\b(merci|thanks|thx)\b",
     "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. 😊"),
    (r"\b(au revoir|bye|a bientot|a plus)\b",
     "Au revoir et bonne chance pour votre stage ! 🍀"),
]


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def _load_stopwords() -> set[str]:
    try:
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords

        words = set(stopwords.words("french"))
    except Exception:  # noqa: BLE001
        words = set(FALLBACK_STOPWORDS)
    return {strip_accents(w) for w in words}


@dataclass
class Answer:
    text: str
    matched_question: str | None = None
    score: float = 0.0
    is_fallback: bool = False
    intent: bool = False
    suggestions: list[tuple[str, float]] = field(default_factory=list)


class FAQChatbot:
    def __init__(self, faq_path: str | Path = FAQ_PATH, threshold: float = 0.25):
        self.threshold = threshold
        self.faq = json.loads(Path(faq_path).read_text(encoding="utf-8"))
        self._tokenizer = RegexpTokenizer(r"\w+")
        self._stemmer = FrenchStemmer()
        self._stop = _load_stopwords()

        # On indexe question + mots-clés (les mots-clés couvrent les synonymes)
        corpus = [f"{item['question']} {item.get('keywords', '')}" for item in self.faq]
        self.vectorizer = TfidfVectorizer(analyzer=self.analyze, sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(corpus)

    # ---- Prétraitement NLP -------------------------------------------------
    def analyze(self, text: str) -> list[str]:
        """minuscules -> tokens -> stopwords retirés -> racinisation -> unigrammes + bigrammes."""
        tokens = self._tokenizer.tokenize(text.lower())
        stems = [
            strip_accents(self._stemmer.stem(t))
            for t in tokens
            if strip_accents(t) not in self._stop
        ]
        bigrams = [f"{a}_{b}" for a, b in zip(stems, stems[1:])]
        return stems + bigrams

    # ---- Réponse -------------------------------------------------------------
    def _intent(self, text: str) -> str | None:
        clean = strip_accents(text.lower()).strip()
        if len(clean.split()) > 4:
            return None
        for pattern, reply in INTENTS:
            if re.search(pattern, clean):
                return reply
        return None

    def ask(self, user_text: str, top_k: int = 3) -> Answer:
        user_text = user_text.strip()
        if not user_text:
            return Answer("Posez-moi une question 🙂", is_fallback=True)

        reply = self._intent(user_text)
        if reply:
            return Answer(reply, intent=True, score=1.0)

        vec = self.vectorizer.transform([user_text])
        scores = cosine_similarity(vec, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        best = int(ranked[0])
        best_score = float(scores[best])
        suggestions = [(self.faq[i]["question"], float(scores[i])) for i in ranked if scores[i] > 0]

        if best_score < self.threshold:
            if best_score >= 0.15:  # zone d'hésitation : on propose la question la plus proche
                msg = f"Je ne suis pas sûr de comprendre. Vouliez-vous dire : « {self.faq[best]['question']} » ?"
            else:
                msg = ("Je n'ai pas trouvé de réponse précise. 🤔 Essayez de reformuler, "
                       "ou choisissez une des questions suggérées.")
            return Answer(
                msg,
                score=best_score,
                is_fallback=True,
                suggestions=suggestions,
            )
        return Answer(
            self.faq[best]["answer"],
            matched_question=self.faq[best]["question"],
            score=best_score,
            suggestions=suggestions[1:],
        )


if __name__ == "__main__":  # mode console : python chatbot.py
    bot = FAQChatbot()
    print("🤖 Chatbot FAQ CodeAlpha (tapez 'q' pour quitter)")
    while True:
        q = input("Vous : ")
        if q.lower() in {"q", "quit", "exit"}:
            break
        r = bot.ask(q)
        print(f"Bot : {r.text}  [score={r.score:.2f}]\n")

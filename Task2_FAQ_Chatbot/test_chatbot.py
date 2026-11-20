"""Tests rapides : python test_chatbot.py"""
from chatbot import FAQChatbot

bot = FAQChatbot()

CASES = [
    ("Combien de tâches pour avoir le certificat ?", "Combien de tâches faut-il réaliser pour obtenir le certificat ?"),
    ("où mettre mon code ?", "Où dois-je publier mon code source ?"),
    ("comment vous joindre par email", "Comment contacter CodeAlpha ?"),
    ("c'est quoi la task 2", "En quoi consiste la Task 2 : chatbot FAQ ?"),
    ("traduction de langues, comment la réaliser ?", "En quoi consiste la Task 1 : outil de traduction ?"),
    ("est-ce qu'on est payé ?", "Le stage est-il rémunéré ?"),
    ("comment envoyer mon travail", "Comment soumettre ma tâche terminée ?"),
    ("détection d'objets avec YOLO", "En quoi consiste la Task 4 : détection et suivi d'objets ?"),
    ("quelle est la capitale de la France ?", None),  # hors sujet -> repli
]

ok = 0
for question, expected in CASES:
    r = bot.ask(question)
    got = None if r.is_fallback else r.matched_question
    good = got == expected
    ok += good
    print(f"{'✅' if good else '❌'} {question!r:55} -> {got!r} ({r.score:.2f})")
print(f"\n{ok}/{len(CASES)} tests réussis")
assert bot.ask("Bonjour").intent

"""Lancer : python test_moteurs.py
"""
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator

def google():
    return GoogleTranslator(source="fr", target="ar").translate("salut")

def mymemory():
    return MyMemoryTranslator(source="french", target="arabic").translate("salut")

def lingva():
    last = None
    for base in ["https://lingva.ml", "https://lingva.lunar.icu", "https://translate.plausibility.cloud"]:
        try:
            r = requests.get(f"{base}/api/v1/fr/ar/salut", timeout=10)
            r.raise_for_status()
            return f"{r.json()['translation']}  (via {base})"
        except Exception as e:
            last = e
    raise last

for name, fn in [("Google", google), ("MyMemory", mymemory), ("Lingva", lingva)]:
    try:
        print(f" {name:9} -> {fn()}")
    except Exception as e:
        print(f" {name:9} -> {str(e)[:150]}")
from deep_translator import GoogleTranslator


def translate_text(text: str, target: str = "ar") -> str:
    return GoogleTranslator(source="auto", target=target).translate(text[:4900]) or ""

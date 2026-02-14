from lingua import Language, LanguageDetectorBuilder
detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
# detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

def is_english(phrase):
    lang = detector.detect_language_of(phrase)
    # print(lang)
    return lang == Language.ENGLISH

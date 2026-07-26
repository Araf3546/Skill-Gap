import re

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import wordnet
except Exception:  # pragma: no cover - optional dependency fallback
    nltk = None
    stopwords = None
    WordNetLemmatizer = None
    word_tokenize = None
    wordnet = None

DEFAULT_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will',
    'with', 'this', 'these', 'those', 'or', 'if', 'into', 'than', 'then', 'their',
    'they', 'them', 'you', 'your', 'we', 'our', 'i'
}

class TextPreprocessor:
    
    def __init__(self, remove_stopwords=True, lemmatize=True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        if stopwords is not None:
            try:
                self.stop_words = set(stopwords.words('english'))
            except Exception:
                self.stop_words = set(DEFAULT_STOP_WORDS)
        else:
            self.stop_words = set(DEFAULT_STOP_WORDS)

        self.lemmatizer = WordNetLemmatizer() if WordNetLemmatizer is not None else None

    def clean_text(self, text):

        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text):
        if word_tokenize is not None:
            try:
                return word_tokenize(text)
            except Exception:
                pass

        return re.findall(r"[A-Za-z0-9\+\#\.]+", text)

    def remove_stop_words(self, tokens):

        keep_words = {'no', 'not', 'more', 'most', 'only'}
        custom_stops = self.stop_words - keep_words
        return [word for word in tokens if word not in custom_stops]
    
    def lemmatize_tokens(self, tokens):
        if self.lemmatizer is None:
            return tokens

        try:
            return [self.lemmatizer.lemmatize(word, pos='v') for word in tokens]
        except Exception:
            return tokens
    
    def preprocess(self, text):

        cleaned = self.clean_text(text)


        tokens = self.tokenize(cleaned)

        if self.remove_stopwords:
            tokens = self.remove_stop_words(tokens)


        if self.lemmatize:
            tokens = self.lemmatize_tokens(tokens)

        return tokens

if __name__ == "__main__":
    preprocessor = TextPreprocessor()

    sample_text = """
    I am a Senior Python Developer with 5+ years of experience
    in Machine Learning and Data Science. Proficient in TensorFlow,
    PyTorch, and scikit-learn.
    """

    tokens = preprocessor.preprocess(sample_text)
    print("Original text:", sample_text)
    print("\nProcessed tokens:", tokens)
    print("\nCleaned text:", ' '.join(tokens))



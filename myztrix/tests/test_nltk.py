import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print("Punkt tokenizer found.")
except LookupError:
    print("Downloading punkt...")
    nltk.download('punkt')

print("Stopwords:", nltk.corpus.stopwords.words('english')[:5])

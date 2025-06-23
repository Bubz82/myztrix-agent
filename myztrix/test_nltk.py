import nltk

print("NLTK data paths:", nltk.data.path)

try:
    nltk.data.find('tokenizers/punkt')
    print("✔ Punkt tokenizer found.")
except LookupError:
    print("❌ Punkt tokenizer missing. Downloading...")
    nltk.download('punkt')

try:
    from nltk.corpus import stopwords
    print("✔ Stopwords sample:", stopwords.words('english')[:5])
except LookupError:
    print("❌ Stopwords missing. Downloading...")
    nltk.download('stopwords')

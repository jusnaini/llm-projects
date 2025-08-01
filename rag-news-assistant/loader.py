def load_news(file_path="data/news_sample.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        docs = [line.strip() for line in f if line.strip()]
    return docs
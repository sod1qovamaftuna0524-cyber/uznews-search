import re
import collections
import math
import pickle
import os

class UzbekNewsSearchEngine:
    def __init__(self):
        self.articles = []
        self.inverted_index = collections.defaultdict(list)
        self.word_counts = collections.defaultdict(lambda: collections.defaultdict(int))
        self.doc_lengths = []
        self.avg_doc_len = 0
        
        # Agar avvaldan indeks bo'lsa, uni yuklab olamiz
        self.load_index()

    def normalize_uz(self, text):
        """O'zbekcha matnni standart ko'rinishga keltirish"""
        if not text:
            return ""
        text = text.lower()
        # o' va g' harflarini standartlashtirish
        text = re.sub(r"o[‘'’`´]", "o'", text)
        text = re.sub(r"g[‘'’`´]", "g'", text)
        # Faqat lotin harflari, sonlar va bo'shliq
        text = re.sub(r"[^a-z0-9' ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def load_and_index(self, file_path):
        """Matnli faylni o'qish va indekslash"""
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        raw_articles = re.findall(r'\[BEGIN\](.*?)\[END\]', content, re.DOTALL)
        
        total_len = 0
        self.articles = []
        self.inverted_index.clear()
        self.word_counts.clear()
        self.doc_lengths = []

        for idx, text in enumerate(raw_articles):
            clean_text = text.strip()
            self.articles.append(clean_text)
            
            tokens = self.normalize_uz(clean_text).split()
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len
            
            for token in tokens:
                self.word_counts[idx][token] += 1
            
            for token in set(tokens):
                self.inverted_index[token].append(idx)
        
        if len(self.articles) > 0:
            self.avg_doc_len = total_len / len(self.articles)
        
        self.save_index()
        return True

    def save_index(self, index_file='index.pickle'):
        """Indeksni faylga saqlash"""
        data = {
            'articles': self.articles,
            'inverted_index': self.inverted_index,
            'word_counts': {k: dict(v) for k, v in self.word_counts.items()},
            'doc_lengths': self.doc_lengths,
            'avg_doc_len': self.avg_doc_len
        }
        with open(index_file, 'wb') as f:
            pickle.dump(data, f)

    def load_index(self, index_file='index.pickle'):
        """Saqlangan indeksni yuklash"""
        if os.path.exists(index_file):
            with open(index_file, 'rb') as f:
                data = pickle.load(f)
                self.articles = data['articles']
                self.inverted_index = data['inverted_index']
                self.word_counts = collections.defaultdict(lambda: collections.defaultdict(int))
                for k, v in data['word_counts'].items():
                    self.word_counts[k].update(v)
                self.doc_lengths = data['doc_lengths']
                self.avg_doc_len = data['avg_doc_len']
            return True
        return False

    def search(self, query, algorithm='bm25'):
        """Views.py uchun asosiy qidiruv interfeysi"""
        if algorithm == 'tfidf':
            raw_results = self.search_tfidf(query)
        else:
            raw_results = self.search_bm25(query)
        
        query_tokens = self.normalize_uz(query).split()
        
        formatted_results = []
        for doc_id, score in raw_results:
            # Har bir natija uchun so'zlar chastotasini hisoblash
            freq = sum(self.word_counts[doc_id][token] for token in query_tokens)
            
            formatted_results.append({
                'id': doc_id,
                'content': self.articles[doc_id],
                'score': round(score, 2),
                'frequency': freq
            })
        return formatted_results

    def search_bm25(self, query, k1=1.5, b=0.75):
        query_tokens = self.normalize_uz(query).split()
        scores = collections.defaultdict(float)
        N = len(self.articles)
        if N == 0 or not query_tokens: return []

        for token in query_tokens:
            if token in self.inverted_index:
                df = len(self.inverted_index[token])
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                for doc_id in self.inverted_index[token]:
                    tf = self.word_counts[doc_id][token]
                    doc_len = self.doc_lengths[doc_id]
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (doc_len / self.avg_doc_len))
                    scores[doc_id] += idf * (numerator / denominator)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:50]

    def search_tfidf(self, query):
        query_tokens = self.normalize_uz(query).split()
        scores = collections.defaultdict(float)
        N = len(self.articles)
        if N == 0 or not query_tokens: return []

        for token in query_tokens:
            if token in self.inverted_index:
                df = len(self.inverted_index[token])
                idf = math.log10(N / df) if df > 0 else 0
                for doc_id in self.inverted_index[token]:
                    tf = self.word_counts[doc_id][token]
                    scores[doc_id] += tf * idf
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:50]

    def get_suggestions(self, term):
        """Avto-to'ldirish uchun so'zlar ro'yxati"""
        term = self.normalize_uz(term)
        return [word for word in self.inverted_index.keys() if word.startswith(term)][:10]

    def get_total_docs_count(self):
        return len(self.articles)
    def search(self, query, algorithm='bm25'):
        query_tokens = self.normalize_uz(query).split()
        
        # --- YANGI QISM: Umumiy bazadagi chastotani hisoblash ---
        total_word_frequency = 0
        for token in query_tokens:
            if token in self.inverted_index:
                # Har bir hujjatdagi ushbu so'z sonini yig'amiz
                for doc_id in self.inverted_index[token]:
                    total_word_frequency += self.word_counts[doc_id][token]
        # -------------------------------------------------------

        if algorithm == 'tfidf':
            raw_results = self.search_tfidf(query)
        else:
            raw_results = self.search_bm25(query)
        
        formatted_results = []
        for doc_id, score in raw_results:
            freq = sum(self.word_counts[doc_id][token] for token in query_tokens)
            formatted_results.append({
                'id': doc_id,
                'content': self.articles[doc_id],
                'score': round(score, 2),
                'frequency': freq
            })
            
        # Natijalar bilan birga umumiy chastotani ham qaytaramiz
        return formatted_results, total_word_frequency

engine = UzbekNewsSearchEngine()
if len(engine.articles) == 0:
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    txt_path = os.path.join(base_dir, 'yangiliklar_kichik.txt')
    if os.path.exists(txt_path):
        engine.load_and_index(txt_path)

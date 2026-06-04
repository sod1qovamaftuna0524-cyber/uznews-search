import re
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'articles.db')

class UzbekNewsSearchEngine:
    def __init__(self):
        self.db_path = DB_PATH

    def normalize_uz(self, text):
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"o['''`´]", "o'", text)
        text = re.sub(r"g['''`´]", "g'", text)
        text = re.sub(r"[^a-z0-9' ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def load_and_index(self, file_path=None):
        """Eski kod bilan moslik uchun"""
        pass

    def search(self, query, algorithm='bm25'):
        tokens = self.normalize_uz(query).split()
        if not tokens:
            return [], 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        conditions = " AND ".join([f"content LIKE ?" for _ in tokens])
        params = [f"%{token}%" for token in tokens]

        cursor.execute(f"""
            SELECT id, content FROM articles
            WHERE {conditions}
            LIMIT 50
        """, params)

        rows = cursor.fetchall()
        conn.close()

        results = []
        total_freq = 0
        for doc_id, content in rows:
            freq = sum(content.lower().count(token) for token in tokens)
            total_freq += freq
            results.append({
                'id': doc_id,
                'content': content,
                'score': freq,
                'frequency': freq
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results, total_freq

    def get_suggestions(self, term):
        term = self.normalize_uz(term)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT content FROM articles WHERE content LIKE ? LIMIT 10",
            (f"%{term}%",)
        )
        rows = cursor.fetchall()
        conn.close()
        words = []
        for (content,) in rows:
            for word in content.split():
                if word.startswith(term) and word not in words:
                    words.append(word)
        return words[:10]

    def get_total_docs_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_query_tokens_info(self, query):
        tokens = self.normalize_uz(query).split()
        result = {}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for token in tokens:
            cursor.execute(
                "SELECT COUNT(*) FROM articles WHERE content LIKE ?",
                (f"%{token}%",)
            )
            result[token] = cursor.fetchone()[

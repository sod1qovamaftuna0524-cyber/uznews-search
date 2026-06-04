import re
import collections
import math

class UzbekNewsSearchEngine:
    def __init__(self):
        # Maqolalarni saqlash uchun ro'yxat
        self.articles = []
        # Teskari indeks: {so'z: [doc_id1, doc_id2, ...]}
        self.inverted_index = collections.defaultdict(list)
        # Har bir hujjatda so'zlar necha marta uchrashini saqlash (TF uchun)
        # {doc_id: {so'z: soni}}
        self.word_counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def normalize_uz(self, text):
        """O'zbek tilidagi maxsus belgilarni standartlashtirish"""
        text = text.lower()
        # O' va G' harflari uchun barcha variantlarni bitta standart ' belgisiga o'tkazish
        text = re.sub(r"[o‘o’o`]", "o'", text)
        text = re.sub(r"[g‘g’g`]", "g'", text)
        # Faqat lotin harflari, raqamlar va bo'shliqlarni qoldirish
        text = re.sub(r"[^a-z0-9' ]", " ", text)
        return text

    def preprocess(self, text):
        """Matnni tozalash va so'zlarga ajratish"""
        clean_text = self.normalize_uz(text)
        return clean_text.split()

    def load_and_index(self, file_path):
        """Datasetni o'qish, indekslash va TF-IDF uchun ma'lumot yig'ish"""
        print(f"'{file_path}' fayli o'qilmoqda...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print("Xato: Fayl topilmadi!")
            return

        # [BEGIN] va [END] orasidagi matnlarni ajratish
        raw_articles = re.findall(r'\[BEGIN\](.*?)\[END\]', content, re.DOTALL)
        
        total = len(raw_articles)
        print(f"Jami {total} ta maqola topildi. Indekslash boshlandi...")

        for idx, text in enumerate(raw_articles):
            text = text.strip()
            self.articles.append(text)
            
            tokens = self.preprocess(text)
            
            # Har bir so'zning ushbu hujjatdagi sonini hisoblash (TF uchun)
            for token in tokens:
                self.word_counts[idx][token] += 1
            
            # Teskari indeks yaratish (Har bir so'z qaysi hujjatlarda bor)
            for token in set(tokens):
                self.inverted_index[token].append(idx)
            
            # Progress paneli (har 10,000 tada)
            if (idx + 1) % 10000 == 0:
                print(f"Progress: {idx + 1}/{total} maqola indekslandi...")

        print("Indekslash muvaffaqiyatli yakunlandi!\n")

    def search_tfidf(self, query, top_n=10):
        """TF-IDF algoritmi bo'yicha qidiruv va saralash"""
        query_tokens = self.preprocess(query)
        if not query_tokens:
            return []

        # Maqolalar uchun ballarni saqlash {doc_id: score}
        scores = collections.defaultdict(float)
        N = len(self.articles)

        for token in query_tokens:
            if token in self.inverted_index:
                # 1. IDF hisoblash (Inverse Document Frequency)
                df = len(self.inverted_index[token])
                idf = math.log10(N / df)

                # 2. TF hisoblash va umumiy ballni yig'ish
                for doc_id in self.inverted_index[token]:
                    tf = self.word_counts[doc_id][token]
                    # Score = TF * IDF
                    scores[doc_id] += tf * idf

        # Ballar bo'yicha kamayish tartibida saralash
        sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        return sorted_results[:top_n]

# --- ASOSIY QISM ---
if __name__ == "__main__":
    engine = UzbekNewsSearchEngine()

    # 1. Ma'lumotlarni yuklash
    # Fayl nomini o'zingiznikiga moslang (masalan: 'yangiliklar.txt')
    engine.load_and_index('yangiliklar.txt')

    while True:
        query = input("\nQidiruv so'rovini kiriting (to'xtatish uchun 'exit'): ")
        if query.lower() == 'exit':
            break
        
        print(f"'{query}' bo'yicha qidirilmoqda...")
        results = engine.search_tfidf(query)

        if not results:
            print("Hech narsa topilmadi.")
        else:
            print(f"\nTopilgan natijalar (Top {len(results)}):")
            print("-" * 50)
            for i, (doc_id, score) in enumerate(results):
                content = engine.articles[doc_id].replace('\n', ' ')
                print(f"{i+1}. [Ball: {score:.4f}] {content[:150]}...")
            print("-" * 50)
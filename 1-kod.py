import re
import collections

class NewsSearchEngine:
    def __init__(self):
        self.inverted_index = collections.defaultdict(list)
        self.articles = []

    def normalize_uz(self, text):
        """O'zbek tilidagi maxsus belgilarni standartlashtirish"""
        text = text.lower()
        # Turli xil apostroflarni bitta standart ' belgisiga o'tkazish
        text = re.sub(r"[o‘o’o`]", "o'", text)
        text = re.sub(r"[g‘g’g`]", "g'", text)
        # Faqat lotin harflari, raqamlar va ' belgisini qoldirish
        text = re.sub(r"[^a-z0-9' ]", " ", text)
        return text

    def preprocess(self, text):
        """Matnni tozalash va so'zlarga ajratish"""
        clean_text = self.normalize_uz(text)
        return clean_text.split()

    def load_and_index(self, file_path):
        """100k lik faylni o'qish va indekslash"""
        print("Fayl o'qilmoqda, iltimos kutib turing...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # [BEGIN] va [END] orasidagi matnlarni qidirish
        # re.DOTALL - yangi qatorlarni ham hisobga olish uchun
        raw_articles = re.findall(r'\[BEGIN\](.*?)\[END\]', content, re.DOTALL)
        
        for idx, text in enumerate(raw_articles):
            text = text.strip()
            self.articles.append(text) # Maqolani saqlash
            
            # Tokenizatsiya va Indekslash
            tokens = self.preprocess(text)
            for token in set(tokens): # Har bir so'zni bir marta hisobga olamiz
                self.inverted_index[token].append(idx)
            
            # Har 10,000 tada jarayonni ko'rsatish
            if idx % 10000 == 0:
                print(f"{idx} ta maqola indekslandi...")

        print(f"Tayyor! Jami {len(self.articles)} ta maqola yuklandi.")

    def search(self, query):
        """Oddiy qidiruv funksiyasi"""
        query_tokens = self.preprocess(query)
        if not query_tokens:
            return []

        # So'rovdagi barcha so'zlar qatnashgan maqolalar ID larini topish
        result_sets = []
        for token in query_tokens:
            if token in self.inverted_index:
                result_sets.append(set(self.inverted_index[token]))
        
        if not result_sets:
            return []

        # Umumiy ID larni topish (kesishma - INTERSECTION)
        common_ids = set.intersection(*result_sets)
        return [self.articles[i] for i in list(common_ids)[:10]] # Dastlabki 10 tasini qaytarish

# --- ISHLATISH QISMI ---
engine = NewsSearchEngine()

# Faylingiz nomini to'g'ri yozing:
engine.load_and_index('yangiliklar.txt')

# Sinab ko'rish:
natija = engine.search("O'zbekiston ta'lim yangiliklari")
for i, res in enumerate(natija):
     print(f"{i+1}-Natija: {res[:100]}...")
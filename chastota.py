from search_app.search_engine import UzbekNewsSearchEngine
import collections
import os
import re # RegEx qo'shamiz

def calculate_word_frequency():
    engine = UzbekNewsSearchEngine()
    
    input_file = 'yangiliklar.txt'
    output_file = 'sozlar_chastotasi.txt'
    
    if not os.path.exists(input_file):
        print(f"Xato: {input_file} topilmadi!")
        return

    print("Fayl o'qilmoqda, kuting...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Matn normalizatsiya qilinmoqda...")
    
    # 1. Avval barcha turdagi apostroflarni bitta standart ' belgisiga keltiramiz
    # Bu orqali "ma'no", "ma’no" va "ma`no" bitta so'z deb hisoblanadi
    content = content.replace("’", "'").replace("`", "'").replace("‘", "'")

    # 2. engine.normalize_uz funksiyasini chaqiramiz
    clean_text = engine.normalize_uz(content)

    # 3. Agar normalize_uz tutuq belgilarini o'chirib tashlayotgan bo'lsa:
    # Biz faqat harflar va ' belgisini qoldiradigan qo'shimcha filtr qo'llaymiz
    # [^a-zA-Zа-яА-ЯёЁ' ] - harflar, tutuq belgisi va bo'shliqdan boshqa hamma narsani o'chiradi
    clean_text = re.sub(r"[^a-zA-Zа-яА-ЯёЁ'\s]", " ", clean_text)
    
    words = clean_text.lower().split() # lower() kichik harflarga o'tkazish uchun

    print(f"Jami so'zlar soni: {len(words)}")
    
    print("Chastota hisoblanmoqda...")
    word_counts = collections.Counter(words)
    sorted_counts = word_counts.most_common()

    print(f"Natija '{output_file}' fayliga yozilmoqda...")
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("So'z".ljust(20) + " | " + "Chastota (marta)".ljust(10) + "\n")
        out.write("-" * 35 + "\n")
        
        for word, count in sorted_counts:
            # So'z juda qisqa bo'lsa yoki faqat ' belgisidan iborat bo'lsa o'tkazib yuboramiz
            if len(word) < 2 and word != "u" and word != "i": 
                continue
                
            line = f"{word:<20} | {count:<10}\n"
            out.write(line)

    print(f"Tayyor! Unikal so'zlar soni: {len(sorted_counts)}")

if __name__ == "__main__":
    calculate_word_frequency()
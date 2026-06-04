from search_app.search_engine import UzbekNewsSearchEngine
import os

def generate_tokens_file():
    # Engine-ni yuklaymiz (normalize_uz funksiyasidan foydalanish uchun)
    engine = UzbekNewsSearchEngine()
    
    input_file = 'yangiliklar.txt'
    output_file = 'token_yangiliklar.txt'
    
    if not os.path.exists(input_file):
        print(f"Xato: {input_file} fayli topilmadi!")
        return

    print("Fayl o'qilmoqda...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Maqolalarni ajratib olamiz
    import re
    raw_articles = re.findall(r'\[BEGIN\](.*?)\[END\]', content, re.DOTALL)
    
    print(f"Jami {len(raw_articles)} ta maqola topildi. Tokenizatsiya boshlanmoqda...")

    all_tokens = []

    with open(output_file, 'w', encoding='utf-8') as out:
        for idx, text in enumerate(raw_articles):
            # Matnni tozalash va so'zlarga bo'lish
            tokens = engine.normalize_uz(text).split()
            
            # Faylga yozish formati
            out.write(f"--- MAQOLA #{idx} ---\n")
            out.write(" ".join(tokens) + "\n\n")
            
            all_tokens.extend(tokens)

        # Oxirida umumiy statistika
        unique_tokens = set(all_tokens)
        out.write("="*30 + "\n")
        out.write(f"UMUMIY STATISTIKA:\n")
        out.write(f"Jami so'zlar soni: {len(all_tokens)}\n")
        out.write(f"Unikal so'zlar soni: {len(unique_tokens)}\n")
    
    print(f"Muvaffaqiyatli yakunlandi! Natija '{output_file}' fayliga saqlandi.")

if __name__ == "__main__":
    generate_tokens_file()
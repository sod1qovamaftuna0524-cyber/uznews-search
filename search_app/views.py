from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
import time
import os

# Search engine obyektini import qilish
try:
    from .search_engine import engine
except ImportError:
    from .search_engine import SearchEngine
    engine = SearchEngine()

def index(request):
    query = request.GET.get('q', '').strip()
    algo = request.GET.get('algo', 'bm25')
    sort_by = request.GET.get('sort', 'score')
    page_number = request.GET.get('page', 1)

    results = []
    duration = 0
    count = 0
    total_freq = 0
    tokens_data = {}

    # Qidiruv mantiqi
    if query:
        start_time = time.time()
        search_output = engine.search(query, algorithm=algo)
        
        if isinstance(search_output, tuple) and len(search_output) == 2:
            results, total_freq = search_output
        else:
            results = search_output
            total_freq = sum(item.get('frequency', 0) for item in results) if results else 0

        # Token ma'lumotlarini olish
        if hasattr(engine, 'get_query_tokens_info'):
            tokens_data = engine.get_query_tokens_info(query)
        else:
            tokens_data = {query: total_freq}

        # Saralash
        if sort_by == 'id':
            results = sorted(results, key=lambda x: x.get('id', 0))
        else:
            results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)

        duration = round(time.time() - start_time, 4)
        count = len(results)

    # Fayllarni o'qish qismi
    def read_system_file(file_name):
        path = os.path.join(settings.BASE_DIR, file_name)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read(10000) # Brauzer qotmasligi uchun dastlabki 10kb
        return "Fayl topilmadi yoki bo'sh."

    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'algo': algo,
        'sort_by': sort_by,
        'page_obj': page_obj,
        'count': count,
        'duration': duration,
        'total_freq': total_freq,
        'tokens_info': tokens_data,
        'total_articles': engine.get_total_docs_count() if hasattr(engine, 'get_total_docs_count') else 0,
        # Fayllar mazmuni
        'chastota_txt': read_system_file('sozlar_chastotasi.txt'),
        'token_txt': read_system_file('token_yangiliklar.txt'),
    }
    
    return render(request, 'index.html', context)

def suggest(request):
    term = request.GET.get('term', '').lower()
    suggestions = []
    if term and hasattr(engine, 'get_suggestions'):
        suggestions = engine.get_suggestions(term)
    return JsonResponse(suggestions, safe=False)
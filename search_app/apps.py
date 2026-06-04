from django.apps import AppConfig


class SearchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search_app'

from django.apps import AppConfig
import os

class SearchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search_app'
    engine = None 

    def ready(self):
        from .search_engine import UzbekNewsSearchEngine
        SearchAppConfig.engine = UzbekNewsSearchEngine()
        # Fayl yo'li manage.py bilan bir joyda bo'lishi kerak
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, 'yangiliklar.txt')
        SearchAppConfig.engine.load_and_index(file_path)
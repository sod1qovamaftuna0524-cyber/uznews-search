from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight(text, query):
    if not query:
        return text
    
    # Qidiruv so'zini matn ichidan topib, <mark> tegiga o'raymiz
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted = pattern.sub(lambda m: f'<mark style="background-color: #ffeb3b; padding: 0;">{m.group(0)}</mark>', text)
    return mark_safe(highlighted)
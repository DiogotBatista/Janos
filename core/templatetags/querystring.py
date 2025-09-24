from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Uso:
      <a href="{% url 'minha_view' %}{% querystring page=page_obj.next_page_number %}">Próxima</a>
    Mantém os parâmetros atuais e atualiza/insere os informados.
    Para remover um parâmetro, passe None: {% querystring busca=None %}
    """
    request = context.get('request')
    if not request:
        # Garante que funciona mesmo sem request no contexto (retorna só os novos params)
        from django.http import QueryDict
        q = QueryDict(mutable=True)
    else:
        q = request.GET.copy()

    for k, v in kwargs.items():
        if v is None:
            q.pop(k, None)
        else:
            q[k] = v
    encoded = q.urlencode()
    return f"?{encoded}" if encoded else ""

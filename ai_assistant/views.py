from django.shortcuts import render

from accounts.decorators import section_required

from .models import AssistantQuery
from .services import generate_supply_chain_response, is_llm_configured


@section_required('ai_assistant')
def assistant_chat(request):
    response = None
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            response_text, context_used = generate_supply_chain_response(question)
            AssistantQuery.objects.create(
                user=request.user,
                question=question,
                context_used=context_used,
                response=response_text,
            )
            response = response_text

    history = AssistantQuery.objects.filter(user=request.user)[:15]
    return render(request, 'ai_assistant/chat.html', {
        'response': response,
        'history': history,
        'llm_configured': is_llm_configured(),
    })

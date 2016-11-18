from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_GET


# Create your views here.
from qa.forms import AskForm, AnswerForm
from qa.models import Question


def paginate(request, qs):
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10
    if limit > 100:
        limit = 10
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(qs, limit)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return paginator, page


@require_GET
def test(request, *args, **kwargs):
    return HttpResponse('OK')


@require_GET
def home(request):
    questions = Question.objects.new()
    paginator, page = paginate(request, questions)
    paginator.baseurl = '/?page='
    return render(request, 'home.html', {
        'questions': page.object_list,
        'paginator': paginator,
        'page': page,
    })


@require_GET
def popular(request):
    questions = Question.objects.popular()
    paginator, page = paginate(request, questions)
    paginator.baseurl = '/popular/?page='
    return render(request, 'home.html', {
        'questions': page.object_list,
        'paginator': paginator,
        'page': page,
    })


@require_GET
def question_detail(request, id):
    question = get_object_or_404(Question, pk=id)
    answers = question.answer_set.all()
    form = AnswerForm(initial={'question': str(id)})
    return render(request, 'question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
    })


def ask(request):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save()
            url = question.get_url()
            return HttpResponseRedirect(url)
    else:
        form = AskForm()
    return render(request, 'ask.html', {
        'form': form
    })


def answer(request):
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save()
            q_id = answer.question_id
            question = get_object_or_404(Question, pk=q_id)
            return HttpResponseRedirect(question.get_url())
    return HttpResponseRedirect('/')

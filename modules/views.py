from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm

@login_required
def submit_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.writer = request.user  # Set the writer to the currently logged-in user
            article.save()
            return redirect('submit_article_success')  # Redirect to a success page or another relevant page
    else:
        form = ArticleForm()
    
    return render(request, 'modules/article_form.html', {'form': form})

def submit_article_success(request):
    return render(request, 'modules/submit_article_success.html')

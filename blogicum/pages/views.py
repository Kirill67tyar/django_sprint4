from django.shortcuts import render


def about(request):
    context = {}
    return render(
        request=request,
        template_name='pages/about.html',
        context=context
    )


def rules(request):
    context = {}
    return render(
        request=request,
        template_name='pages/rules.html',
        context=context
    )

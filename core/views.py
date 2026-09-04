from django.shortcuts import render


def inicio(request):
    return render(request, 'core/inicio.html')


def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)
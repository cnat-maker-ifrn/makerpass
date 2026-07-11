from django.urls import path
from .views import PaginaRegistroPontoView, PaginaSucessoPontoView

urlpatterns = [
    path("", PaginaRegistroPontoView.as_view(), name="pagina_registro_ponto"),
    path("sucesso/", PaginaSucessoPontoView.as_view(), name="pagina_sucesso_ponto"),
]

#Django imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from datetime import timedelta
# App imports
from autenticacao.models import Servidor
from .models import Ponto
from .utils import calcular_total_horas
from .services import (
	registrar_novo_ponto, 
	calcular_horas_se_saida, 
	RegraDePontoException, 
	calcula_intervalo_de_tempo, 
	deletar_ponto_pendente,
	get_data 
)

class PaginaRegistroPontoView(View):
    template_name = "makerpass/registrar_ponto.html"
    def get(self, request, **kwargs):
        return render(request, self.template_name)
    def post(self, request, **kwargs):
        servidor, ultimo_ponto = get_data(request)
        calcula_intervalo_de_tempo(ultimo_ponto, request)
        ponto_criado = registrar_novo_ponto(servidor, ultimo_ponto)
        request.session.pop("horas_trabalhadas_dia", None)
        horas_trabalhadas = calcular_horas_se_saida(ponto_criado, servidor)
        if horas_trabalhadas:
            request.session["horas_trabalhadas_dia"] = horas_trabalhadas
        return redirect("pagina_sucesso_ponto")

class PaginaSucessoPontoView(TemplateView):
    template_name = "makerpass/sucesso_ponto.html"
    def get_context_data(self, **kwargs):
        ultimo_ponto = Ponto.objects.all().last()
        context = super().get_context_data(**kwargs)
        context["ultimo_ponto"] = ultimo_ponto
        context["horas_trabalhadas_dia"] = self.request.session.pop(
            "horas_trabalhadas_dia", None
        )
        return context

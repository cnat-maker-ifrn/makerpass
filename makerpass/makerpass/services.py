from datetime import timedelta, time, datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from typing import Iterable, Tuple
from autenticacao.models import Servidor
from .models import Ponto


class RegraDePontoException(Exception):
    pass

def get_data(request):
    matricula = request.POST.get("matricula")
    print(f"Matricula: {matricula}")
    print(f"Request: {request}")
    if not matricula:
        raise RegraDePontoException("Matricula não informada.")
    try:
        servidor = Servidor.objects.get(matricula=matricula)
    except Servidor.DoesNotExist:
        raise RegraDePontoException("Bolsista não encontrado.")
    servidor = Servidor.objects.get(matricula=matricula)
    ultimo_ponto = Ponto.objects.filter(bolsista=servidor).last()
    print(f"Servidor: {servidor} --- Ultimo ponto: {ultimo_ponto}")
    return servidor, ultimo_ponto

def registrar_novo_ponto(servidor, ultimo_ponto):
    _entrada = not ultimo_ponto.eh_entrada if ultimo_ponto else True
    ponto_criado = Ponto.objects.create(bolsista=servidor, eh_entrada=_entrada)
    return ponto_criado

def calcula_intervalo_de_tempo(ultimo_ponto, request):
    agora = timezone.now()
    if ultimo_ponto:
        tempo_desde_ultimo_ponto = agora - ultimo_ponto.data_hora_do_ponto
    if tempo_desde_ultimo_ponto < timedelta(minutes=1):
        segundos_restantes = int(60 - tempo_desde_ultimo_ponto.total_seconds())
        messages.error(request, f"Aguarde {segundos_restantes} segundos para registrar um novo ponto.")
        return redirect('pagina_registro_ponto')
    return None

def deletar_ponto_pendente(ultimo_ponto):
    agora = timezone.now()
    if not eh_entrada:
        if ultimo_ponto.data_hora_do_ponto.date() < agora.date():
            ultimo_ponto.delete()
            eh_entrada = True

def calcular_total_horas(pontos: Iterable) -> Tuple[int, int]:
    total_duration = timedelta()
    entrada_time = None

    for ponto in pontos:
        if getattr(ponto, "eh_entrada", False):
            entrada_time = getattr(ponto, "data_hora_do_ponto", None)
        elif entrada_time is not None:
            saida_time = getattr(ponto, "data_hora_do_ponto", None)
            if saida_time is not None and entrada_time is not None:
                duration = saida_time - entrada_time
                total_duration += duration
                entrada_time = None

    total_seconds = int(total_duration.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    return horas, minutos

def calcular_horas_se_saida(ponto_criado, servidor):
    if ponto_criado.eh_entrada:
        return None
    hoje = timezone.localtime(ponto_criado.data_hora_do_ponto).date()
    inicio_do_dia = timezone.make_aware(datetime.combine(hoje, time.min))
    fim_do_dia = timezone.make_aware(datetime.combine(hoje, time.max))
    pontos_do_dia = Ponto.objects.filter(
        bolsista=servidor,
        data_hora_do_ponto__gte=inicio_do_dia,
        data_hora_do_ponto__lte=fim_do_dia,
    ).order_by("data_hora_do_ponto")
    horas, minutos = calcular_total_horas(pontos_do_dia)
    return f"{horas}h {minutos}min"

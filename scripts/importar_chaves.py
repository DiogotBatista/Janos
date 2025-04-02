import os
import sys
import pandas as pd
from datetime import datetime
import django
from django.contrib import messages



# Configuração do caminho relativo do projeto Django
django_project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(django_project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'janus.settings')

django.setup()

from chaves.models import Chave

def cadastrar_chaves_from_planilha(request, planilha, use_messages=True):
    try:

        # Leitura da planilha sem cabeçalho
        df = pd.read_excel(planilha, header=None)

        registros_criados = 0
        for index, row in df.iterrows():
            # Assumindo que as colunas são: 0 - chave, 1 - data_chamado, 2 - chamado
            chave_numero = row.iloc[0]
            data_chamado_str = str(row.iloc[1])  # Converte para string
            chamado = row.iloc[2]
            # print(f"Processando linha {index}: {row}")

            # Converte a string para um objeto datetime
            try:
                data_chamado = datetime.strptime(data_chamado_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                if use_messages:
                    messages.error(request, f"Formato de data inválido na linha {index}")
                continue

            # Verificar se a chave já existe no banco de dados
            chave_existente = Chave.objects.filter(chave=chave_numero).first()
            if not chave_existente:
                # A chave não existe, criar uma nova instância
                Chave.objects.create(
                    chave=chave_numero,
                    chamado=chamado,
                    data_chamado=data_chamado
                )
                registros_criados += 1
            else:
                # A chave já existe, você pode querer fazer alguma ação aqui
                messages.warning(request, f"A chave {chave_numero} já existe no banco de dados.")

        # print(f"Registros processados: {registros_criados}")
        if use_messages:
            messages.success(request, f"{registros_criados} registros foram criados.")
    except Exception as e:
        # print(f"Erro durante o processamento: {e}")
        if use_messages:
            messages.error(request, f"Erro: {e}")


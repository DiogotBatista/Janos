from django.test import TestCase, RequestFactory
from chaves.models import Chave
from scripts.importar_chaves import cadastrar_chaves_from_planilha
from io import BytesIO
import pandas as pd


class CadastrarChavesFromPlanilhaTestCase(TestCase):
    def setUp(self):
        # Configuração inicial para o teste
        self.factory = RequestFactory()
        self.request = self.factory.get('/fake-url')

    def criar_planilha_teste(self, dados):
        # Cria um DataFrame e converte para um arquivo Excel na memória
        df = pd.DataFrame(dados)
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, header=False)
        excel_file.seek(0)
        return excel_file

    def test_cadastrar_chaves_from_planilha(self):
        # Dados de teste
        dados_teste = {
            0: ['chave1', 'chave2', 'chave3'],
            1: ['2024-01-05 00:00:00', 'adasda', '2024-01-05 00:00:00'],
            2: ['Chamado A', 'Chamado B', 'Chamado C']
        }
        planilha = self.criar_planilha_teste(dados_teste)

        # Executa a função de importação
        cadastrar_chaves_from_planilha(self.request, planilha, use_messages=False)

        # Testa se os registros corretos foram criados
        self.assertEqual(Chave.objects.count(), 2)
        self.assertTrue(Chave.objects.filter(chave='chave1').exists())
        self.assertFalse(Chave.objects.filter(chave='chave2').exists())  # Devido a data inválida
        self.assertTrue(Chave.objects.filter(chave='chave3').exists())

    def tearDown(self):
        # Limpeza após o teste
        Chave.objects.all().delete()

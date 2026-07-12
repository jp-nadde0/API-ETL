from openpyxl import Workbook

from services.sales_service import ServicoVendas


def test_servico_vendas_persiste_e_consulta_registros(tmp_path):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Dados de Vendas'
    worksheet.append([
        'ID Venda',
        'Data da Venda',
        'Produto',
        'Categoria',
        'Preço Unitário',
        'Quantidade Vendida',
        'Estoque Atual',
    ])
    worksheet.append([1, '2023-01-01', 'Produto A', 'Categoria 1', 10.0, 5, 100])
    worksheet.append([2, '2023-01-02', 'Produto B', 'Categoria 2', 20.0, 3, 50])

    database_url = f"sqlite:///{tmp_path / 'sales_service.db'}"
    servico = ServicoVendas()

    resultado = servico.persistir_dados(workbook, 'Dados de Vendas', database_url=database_url)

    assert resultado['persistidos'] == 2
    assert len(servico.consultar_vendas(database_url=database_url)) == 2


def test_servico_vendas_usa_extrator_injetado():
    class StubExtrator:
        def extrair(self, workbook_or_path, sheet_name=None):
            return [(1, '2023-01-01', 'Produto A', 'Categoria 1', 10.0, 2.0, 20.0, 50)]

        def resumir(self, workbook_or_path, sheet_name=None, data_inicial=None, data_final=None):
            return {'mais_vendidos': []}

    class StubRepositorio:
        def persistir(self, dados, database_url=None):
            return {'persistidos': len(dados), 'database_url': database_url or 'stub'}

        def consultar(self, database_url=None, limit=100):
            return []

    servico = ServicoVendas(repositorio_vendas=StubRepositorio(), extrator_vendas=StubExtrator())

    resultado = servico.persistir_dados('arquivo.xlsx', sheet_name='Dados de Vendas', database_url='sqlite:///stub.db')

    assert resultado['persistidos'] == 1

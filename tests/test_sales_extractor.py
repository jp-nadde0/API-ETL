from extractors.sales_extractor import extract_produtos, resumir_vendas, persistir_dados, consultar_vendas
from openpyxl import Workbook
import pytest

@pytest.fixture
def sales_workbook():
    wb = Workbook()
    worksheet = wb.active
    worksheet.title = 'Dados de Vendas'
    headers = [
        'ID Venda',
        'Data da Venda',
        'Produto',
        'Categoria',
        'Preço Unitário',
        'Quantidade Vendida',
        'Estoque Atual',
    ]
    dados = [
        (1, '2023-01-01', 'Produto A', 'Categoria 1', 10.0, 5, 100),
        (2, '2023-01-02', 'Produto B', 'Categoria 2', 20.0, 3, 50),
        (3, '2023-01-03', 'Produto C', 'Categoria 3', 15.0, 2, 30),
    ]

    worksheet.append(headers)
    for row in dados:
        worksheet.append(row)

    return wb


def test_extract_produtos_returns_expected_rows(sales_workbook):
    result = extract_produtos(sales_workbook, 'Dados de Vendas')

    assert result == [
        (1, '2023-01-01', 'Produto A', 'Categoria 1', 10.0, 5.0, 50.0, 100),
        (2, '2023-01-02', 'Produto B', 'Categoria 2', 20.0, 3.0, 60.0, 50),
        (3, '2023-01-03', 'Produto C', 'Categoria 3', 15.0, 2.0, 30.0, 30),
    ]


def test_resumir_vendas_returns_top_and_bottom_products_and_category(sales_workbook):
    result = resumir_vendas(sales_workbook, 'Dados de Vendas')

    assert result['mais_vendidos'][0]['produto'] == 'Produto A'
    assert result['menos_vendidos'][0]['produto'] == 'Produto C'
    assert result['categoria_mais_vendida']['categoria'] == 'Categoria 1'


def test_persistir_e_consultar_vendas_em_sqlite(tmp_path, sales_workbook):
    database_url = f"sqlite:///{tmp_path / 'sales.db'}"

    resultado = persistir_dados(sales_workbook, 'Dados de Vendas', database_url=database_url)
    assert resultado['persistidos'] == 3

    registros = consultar_vendas(database_url=database_url)
    assert len(registros) == 3
    assert registros[0]['produto'] == 'Produto A'
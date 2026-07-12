from extractors.employee_costs_extractor import ParseNumeros, ExtratorEmpresa, ExtratorEventos, ExtratorBlocos, ExtratorFuncionario, ExtrairBasesImpostos, ExtrairTotais, ExtratorPDF
import pytest

@pytest.fixture
def parse_numeros():
    return ParseNumeros()

def test_parse_float_with_valid_number(parse_numeros):
    salario_br = "1.234,56"
    resultado = parse_numeros.parse_float(salario_br)
    
    assert resultado == 1234.56

@pytest.fixture
def extrator_empresa():
    return ExtratorEmpresa()

def test_extract_company_info(extrator_empresa):
    texto_pdf = """
    NEXUS TECH & RETAIL LTDA\nRECIBO DE PAGAMENTO\n
    AVENIDA PAULISTA, 1000 - BELA VISTA - SÃO PAULO - SP\n
    Mês/Ano: 06/2026\nCNPJ: 45.987.123/0001-89 INSC. ESTADUAL: 110.223.445.111
    """
    empresa = extrator_empresa.extrair_empresa(texto_pdf)
    
    assert empresa.nome == "NEXUS TECH & RETAIL LTDA"
    assert empresa.cnpj == "45.987.123/0001-89"
    assert empresa.inscricao_estadual == "110.223.445.111"
    assert empresa.data_periodo == "06/2026"

@pytest.fixture
def extrator_eventos():
    return ExtratorEventos()

def test_extract_events(extrator_eventos):
    texto_pdf = """
    'NEXUS TECH & RETAIL LTDA\nRECIBO DE PAGAMENTO\nAVENIDA PAULISTA, 1000 - BELA VISTA - SÃO PAULO - SP\nMês/Ano: 06/2026
    \nCNPJ: 45.987.123/0001-89 INSC. ESTADUAL: 110.223.445.111\nCód: 0001 Funcionário: CARLOS HENRIQUE SILVA CBO: 3171-10 Função: DEV
    \nBACKEND JR\nCód. Descrição do Evento Referência Proventos Descontos\n001 SALÁRIO BASE 30,00D 4,200.00
    """
    eventos = extrator_eventos.extrair_eventos(texto_pdf)

    assert len(eventos) == 1
    assert eventos[0].codigo == "001"
    assert eventos[0].descricao == "SALÁRIO BASE"
    assert eventos[0].referencia == "30,00D"
    assert eventos[0].provento == 4200.00
    assert eventos[0].desconto == 0.0

@pytest.fixture
def extrator_blocos():
    return ExtratorBlocos()

def test_extract_blocks(extrator_blocos):
    texto_pdf = """
    NEXUS TECH & RETAIL LTDA\nRECIBO DE PAGAMENTO\nAVENIDA PAULISTA, 1000 - BELA VISTA - SÃO PAULO - SP\nMês/Ano: 06/2026
    \nCNPJ: 45.987.123/0001-89 INSC. ESTADUAL: 110.223.445.111\nCód: 0001 Funcionário: CARLOS HENRIQUE SILVA CBO: 3171-10 Função: DEV
    \nBACKEND JR\nCód. Descrição do Evento Referência Proventos Descontos\n001 SALÁRIO BASE 30,00D 4,200.00
    \nNEXUS TECH & RETAIL LTDA\nRECIBO DE PAGAMENTO\nAVENIDA PAULISTA, 1000 - BELA VISTA - SÃO PAULO - SP\nMês/Ano: 07/2026
    \nCNPJ: 45.987.123/0001-89 INSC. ESTADUAL: 110.223.445.111\nCód: 0002 Funcionário: MARIA EDUARDA COSTA CBO: 3171-10 Função: DEV
    \nFRONTEND JR\nCód. Descrição do Evento Referência Proventos Descontos\n002 SALÁRIO BASE 30,00D 4,200.00
    """
    blocos = extrator_blocos.extrair_blocos(texto_pdf)

    assert len(blocos) == 2
    assert "CARLOS HENRIQUE SILVA" in blocos[0]
    assert "MARIA EDUARDA COSTA" in blocos[1]

@pytest.fixture
def extrator_funcionario():
    return ExtratorFuncionario()

def test_extract_employee_info(extrator_funcionario):
    texto_pdf = """
    Cód: 0001 Funcionário: CARLOS HENRIQUE SILVA CBO: 3171-10 Função: DEV BACKEND JR
    """
    funcionario = extrator_funcionario.extrair_funcionario(texto_pdf)

    assert funcionario.codigo == "0001"
    assert funcionario.nome == "CARLOS HENRIQUE SILVA"
    assert funcionario.cbo == "3171-10"
    assert funcionario.funcao == "DEV BACKEND JR"

@pytest.fixture
def extrair_bases_impostos():
    return ExtrairBasesImpostos()

def test_extract_tax_bases(extrair_bases_impostos):
    texto_pdf = """
    Salário Base Base Cálc. INSS Base Cálc. IRRF FGTS do Mês Base Cálc. FGTS
    4,200.00 4,200.00 3,764.66 336,00 4,200.00
    """
    bases_impostos = extrair_bases_impostos.extrair_bases_impostos(texto_pdf)

    assert bases_impostos.base_inss == 4200.00
    assert bases_impostos.base_irrf == 3764.66
    assert bases_impostos.base_fgts == 4200.00
    assert bases_impostos.fgts_mes == 336.00

def test_extract_totals(extrair_bases_impostos):
    texto_pdf = """
    TOTAL DE PROVENTOS TOTAL DE DESCONTOS VALOR LÍQUIDO A RECEBER\nR$ 4,200.00 R$ 880.46 R$ 3,319.54
    \nSalário Base Base Cálc. INSS Base Cálc. IRRF FGTS do Mês Base Cálc. FGTS\n4,200.00 4,200.00 3,764.66 336.00 4,200.00
    """
    totais = ExtrairTotais.extrair_totais(texto_pdf)

    assert totais.total_proventos == 4200.00
    assert totais.total_descontos == 880.46
    assert totais.total_liquido == 3319.54

@pytest.fixture
def extrator_pdf():
    return ExtratorPDF()

def test_extrator_pdf_associa_eventos_por_funcionario(monkeypatch):
    texto_pdf = """
    NEXUS TECH & RETAIL LTDA
    RECIBO DE PAGAMENTO
    Cód: 0001 Funcionário: CARLOS HENRIQUE SILVA CBO: 3171-10 Função: DEV
    Cód. Descrição do Evento Referência Proventos Descontos
    001 SALÁRIO BASE 30,00D 4,200.00
    002 OUTRO EVENTO 1,00 100.00
    """

    monkeypatch.setattr(ExtratorPDF, "extrair_texto_pdf", staticmethod(lambda caminho_pdf: texto_pdf))

    extrator = ExtratorPDF()
    resultado = extrator.extrair_dados("ignored.pdf")

    assert resultado["empresa"]["nome"] == "NEXUS TECH & RETAIL LTDA"
    assert len(resultado["funcionarios"]) == 1

    funcionario = resultado["funcionarios"][0]
    assert funcionario["nome"] == "CARLOS HENRIQUE SILVA"
    assert isinstance(funcionario["eventos"], list)
    assert len(funcionario["eventos"]) == 2
    assert funcionario["eventos"][0]["codigo"] == "001"
    assert funcionario["eventos"][1]["codigo"] == "002"
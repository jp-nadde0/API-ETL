from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import re
import pdfplumber

@dataclass
class Empresa:
    nome: str
    cnpj: str
    inscricao_estadual: str
    data_periodo: str

    def to_dict(self) -> Dict:
        return {
            "nome": self.nome,
            "cnpj": self.cnpj,
            "inscricao_estadual": self.inscricao_estadual,
            "data_periodo": self.data_periodo
        }

@dataclass
class Eventos:
    codigo: str
    descricao: str
    referencia: str
    provento: Optional[float] = None
    desconto: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "codigo": self.codigo,
            "descricao": self.descricao,
            "referencia": self.referencia,
            "provento": self.provento,
            "desconto": self.desconto
        }

@dataclass
class Funcionario:
    codigo: str
    nome: str
    cbo: str
    funcao: str

    def to_dict(self) -> Dict:
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "cbo": self.cbo,
            "funcao": self.funcao
        }

@dataclass
class BasesImpostos:
    base_inss: float
    base_irrf: float
    base_fgts: float
    fgts_mes: float

    def to_dict(self) -> Dict:
        return {
            "base_inss": self.base_inss,
            "base_irrf": self.base_irrf,
            "base_fgts": self.base_fgts,
            "fgts_mes": self.fgts_mes
        }

@dataclass
class Totais:
    total_proventos: float
    total_descontos: float
    total_liquido: float

    def to_dict(self) -> Dict:
        return {
            "total_proventos": self.total_proventos,
            "total_descontos": self.total_descontos,
            "total_liquido": self.total_liquido
        }

class ParseNumeros:
    """Classe responsável por filtrar e converter números de strings para float."""

    @staticmethod
    def parse_float(valor: str) -> float:
        """Converte uma string para float, tratando vírgulas, pontos e símbolos."""
        if not valor:
            return 0.0

        valor = re.sub(r'[^\d,.-]', '', str(valor))

        if valor.count(',') and valor.count('.'):
            if valor.rfind(',') > valor.rfind('.'):
                valor = valor.replace('.', '').replace(',', '.')
            else:
                valor = valor.replace(',', '')
        elif valor.count('.') == 1 and len(valor.split('.')[-1]) == 2:
            valor = valor.replace(',', '')
        else:
            valor = valor.replace('.', '').replace(',', '.')

        try:
            return float(valor)
        except ValueError:
            return 0.0

class ExtratorEmpresa:
    """Classe responsável por extrair informações da empresa a partir do texto do PDF."""

    @staticmethod
    def extrair_empresa(texto: str) -> Empresa:
        """Extrai informações da empresa do texto do PDF."""
        
        nome = re.search(r'(?:Página \d+ de \d+)?\s*([A-Z\s&]+LTDA)', texto)
        cnpj = re.search(r'CNPJ:\s*([\d./-]+)', texto)
        inscricao_estadual = re.search(r'INSC\.\s*ESTADUAL:\s*([\d.]+)', texto)
        data_periodo = re.search(r'Mês/Ano:\s*(\d{2}/\d{4})', texto)

        return Empresa(
            nome=nome.group(1).strip() if nome else "",
            cnpj=cnpj.group(1).strip() if cnpj else "",
            inscricao_estadual=inscricao_estadual.group(1).strip() if inscricao_estadual else "",
            data_periodo=data_periodo.group(1).strip() if data_periodo else ""
        )

class ExtratorFuncionario:
    """Classe responsável por extrair informações do funcionário a partir do texto do PDF."""

    @staticmethod
    def extrair_funcionario(texto: str) -> Funcionario:
        """Extrai informações do funcionário do texto do PDF."""
        codigo = re.search(r'Cód:\s*(\d+)', texto)
        nome = re.search(r'Funcionário:\s*([^\n]+?)\s+CBO:', texto)
        cbo = re.search(r'CBO:\s*([\d-]+)', texto)
        funcao = re.search(r'Função:\s*(.+)', texto)

        return Funcionario(
            codigo=codigo.group(1).strip() if codigo else "",
            nome=nome.group(1).strip() if nome else "",
            cbo=cbo.group(1).strip() if cbo else "",
            funcao=funcao.group(1).strip() if funcao else ""
        )

class ExtratorEventos:
    """Classe responsável por extrair eventos do texto do PDF."""

    @staticmethod
    def extrair_eventos(texto: str) -> List[Eventos]:
        """Extrai eventos do texto do PDF."""
        eventos = []
        padrao_evento = re.compile(
            r'^\s*(\d{3})\s+(?!-\s)(.+?)\s+([\d.,D%]+)\s+([\d.,]+)(?:\s+([\d.,]+))?$',
            re.MULTILINE
        )
        for match in padrao_evento.finditer(texto):
            codigo, descricao, referencia, provento, desconto = match.groups()
            eventos.append(Eventos(
                codigo=codigo.strip(),
                descricao=descricao.strip(),
                referencia=referencia.strip(),
                provento=ParseNumeros.parse_float(provento),
                desconto=ParseNumeros.parse_float(desconto)
            ))
        return eventos

class ExtratorBlocos:
    """Classe responsável por extrair blocos de recibos do texto do PDF."""

    @staticmethod
    def extrair_blocos(texto: str) -> List[str]:
        """Extrai blocos de recibos de pagamento do texto completo."""
        if not texto:
            return []

        partes = re.split(
            r'(?=NEXUS TECH & RETAIL LTDA\s+RECIBO DE PAGAMENTO)',
            texto, 
            flags=re.MULTILINE
        )

        blocos = [parte.strip() for parte in partes if parte.strip()]
        return blocos
    
class ExtrairBasesImpostos:
    """Classe responsável por extrair bases de impostos do texto do PDF."""

    @staticmethod
    def extrair_bases_impostos(texto: str) -> BasesImpostos:
        """Extrai bases de impostos do texto do PDF."""
        match = re.search(
            r'Sal[aá]rio Base.*?Base C[aá]lc\. FGTS\s*[\r\n]+([^\n]+)',
            texto,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            linha_valores = match.group(1)
            valores = re.findall(r'[\d.,]+', linha_valores)
            if len(valores) >= 5:
                base_inss, base_irrf, fgts_mes, base_fgts = valores[1:5]
            else:
                base_inss = base_irrf = base_fgts = fgts_mes = "0"
        else:
            base_inss = base_irrf = base_fgts = fgts_mes = "0"

        return BasesImpostos(
            base_inss=ParseNumeros.parse_float(base_inss),
            base_irrf=ParseNumeros.parse_float(base_irrf),
            base_fgts=ParseNumeros.parse_float(base_fgts),
            fgts_mes=ParseNumeros.parse_float(fgts_mes)
        )
    
class ExtrairTotais:
    """Classe responsável por extrair totais do texto do PDF."""

    @staticmethod
    def extrair_totais(texto: str) -> Totais:
        """Extrai totais do texto do PDF."""
        match = re.search(
            r'TOTAL DE PROVENTOS\s+TOTAL DE DESCONTOS\s+VALOR L[ÍI]QUIDO A RECEBER\s*R\$?\s*([\d.,]+)\s+R\$?\s*([\d.,]+)\s+R\$?\s*([\d.,]+)',
            texto,
            re.IGNORECASE
        )

        if match:
            total_proventos, total_descontos, total_liquido = match.groups()
        else:
            total_proventos = total_descontos = total_liquido = "0"

        return Totais(
            total_proventos=ParseNumeros.parse_float(total_proventos),
            total_descontos=ParseNumeros.parse_float(total_descontos),
            total_liquido=ParseNumeros.parse_float(total_liquido)
        )

class ExtratorPDF:
    """Responsável por extrair informações do PDF."""

    def __init__(self):
        self.extrator_empresa = ExtratorEmpresa()
        self.extrator_blocos = ExtratorBlocos()
        self.extrator_funcionario = ExtratorFuncionario()
        self.extrator_eventos = ExtratorEventos()
        self.extrator_bases = ExtrairBasesImpostos()
        self.extrator_totais = ExtrairTotais()

    @staticmethod
    def extrair_texto_pdf(caminho_pdf: str) -> str:
        """Extrai o texto de um arquivo PDF usando pdfplumber."""
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += (pagina.extract_text() or "") + "\n"
            return texto_completo.strip()

    def extrair_dados(self, caminho_pdf: str) -> Dict:
        """Orquestra a extração completa dos dados."""
        texto = self.extrair_texto_pdf(caminho_pdf)
        empresa = self.extrator_empresa.extrair_empresa(texto)
        blocos_comp = self.extrator_blocos.extrair_blocos(texto)
        bases = self.extrator_bases.extrair_bases_impostos(texto)
        totais = self.extrator_totais.extrair_totais(texto)

        funcionarios = []
        for bloco in blocos_comp:
            funcionario = self.extrator_funcionario.extrair_funcionario(bloco)
            eventos = self.extrator_eventos.extrair_eventos(bloco)
            funcionario_dict = funcionario.to_dict()
            funcionario_dict["eventos"] = [evento.to_dict() for evento in eventos]
            funcionarios.append(funcionario_dict)

        return {
            "empresa": empresa.to_dict(),
            "funcionarios": funcionarios,
            "bases": bases.to_dict(),
            "totais": totais.to_dict()
        }
if __name__ == "__main__":
    extrator = ExtratorPDF()
    resultado = extrator.extrair_dados("files/payroll.pdf")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

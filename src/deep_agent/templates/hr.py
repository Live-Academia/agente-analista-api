"""Template de analise: Recursos Humanos."""
from deep_agent.templates.base import AnalysisTemplate

HR = AnalysisTemplate(
    name="rh",
    label="Recursos Humanos",
    description="Analise de pessoas: headcount, salarios, turnover e distribuicao por area.",
    key_columns=[
        "funcionario", "salario", "cargo", "departamento",
        "admissao", "demissao", "area", "nivel", "genero",
        "colaborador", "remuneracao", "turnover",
    ],
    kpis=[
        "Headcount Total",
        "Salario Medio",
        "Taxa de Turnover",
        "Distribuicao por Departamento",
        "Tempo Medio de Casa",
    ],
    insight_focus=(
        "Foque em: (1) distribuicao de headcount e salario por departamento/cargo, "
        "(2) taxa de turnover e padroes de demissao (sazonalidade, areas de risco), "
        "(3) equidade salarial (comparacao entre grupos se disponivel), "
        "(4) evolucao do quadro de funcionarios ao longo do tempo, "
        "(5) identificar areas com alta rotatividade ou subdimensionamento."
    ),
    suggested_questions=[
        "Qual departamento tem maior headcount?",
        "Qual e o salario medio por cargo?",
        "Qual a taxa de turnover?",
        "Quais areas tem maior rotatividade?",
        "Como evoluiu o quadro de funcionarios?",
        "Existe diferenca salarial entre grupos?",
    ],
)

from langchain_core.prompts import ChatPromptTemplate

QA_SYSTEM = """\
Voce e um analista de dados senior. O usuario fara perguntas sobre um conjunto de dados.
Responda com base nas informacoes estatisticas fornecidas.

Regras:
- Seja preciso e use numeros quando disponiveis
- Use os dados de segmentacao e temporais para responder com contexto
- Se a pergunta nao puder ser respondida com os dados disponiveis, diga claramente
- Responda em portugues brasileiro
- Seja conciso mas completo
- Formate com markdown quando apropriado (tabelas, listas, negrito)
"""

QA_HUMAN = """\
## Contexto dos Dados
- Linhas: {rows}
- Colunas: {columns}
- Colunas numericas: {numeric_columns}
- Colunas categoricas: {categorical_columns}

## Estatisticas Descritivas
{describe}

## Perfil Numerico
{numeric_profile}

## Correlacoes Relevantes
{correlations}

## Outliers Detectados
{outliers}

## Analise Temporal
{temporal}

## Segmentacao por Categorias
{segments}

## Metricas de Negocio
{business_metrics}

## Padroes Identificados
{patterns}

## Amostra dos Dados
{head}

## Pergunta do Usuario
{question}

Responda:
"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", QA_SYSTEM),
    ("human", QA_HUMAN),
])

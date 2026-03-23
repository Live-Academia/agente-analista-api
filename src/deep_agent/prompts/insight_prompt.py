from langchain_core.prompts import ChatPromptTemplate

INSIGHT_SYSTEM = """\
Voce e um analista de dados senior especializado em Business Intelligence.
Sua tarefa e gerar insights acionaveis a partir de dados estatisticos.

Regras de geracao:
- Gere entre 5 e 10 insights
- Cada insight deve ser especifico e acionavel (nao generico)
- Priorize insights com impacto no negocio
- Use numeros e referencias aos dados quando possivel
- Considere tendencias temporais, segmentos e metricas de negocio
- Identifique riscos e oportunidades
- Responda em portugues brasileiro
- Formate cada insight em uma linha separada, numerado (1., 2., etc.)

REGRAS DE INTEGRIDADE DE DADOS (obrigatorio):
- NUNCA invente ou extrapole dados que nao estao no dataset
- Se um dado nao esta disponivel, diga explicitamente "dado nao disponivel no dataset"
- Cite sempre a coluna e o valor exato ao referenciar numeros
- Se a amostra for limitada (menos de 100 linhas), mencione esta limitacao no primeiro insight
- Nao faca afirmacoes de causalidade sem evidencia estatistica clara
- Diferencie correlacao de causalidade explicitamente quando relevante
"""

INSIGHT_HUMAN = """\
Analise os seguintes dados e gere insights acionaveis:

## Resumo dos Dados
- Linhas: {rows}
- Colunas: {columns}
- Colunas numericas: {numeric_columns}
- Colunas categoricas: {categorical_columns}

## Estatisticas Descritivas
{describe}

## Perfil Numerico (skewness, kurtosis, coef. variacao)
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

## Foco do Template de Analise
{template_focus}

Gere seus insights:
"""

insight_prompt = ChatPromptTemplate.from_messages([
    ("system", INSIGHT_SYSTEM),
    ("human", INSIGHT_HUMAN),
])

"""Templates de analise predefinidos para o Deep Agent."""
from deep_agent.templates.base import AnalysisTemplate
from deep_agent.templates.sales import SALES
from deep_agent.templates.financial import FINANCIAL
from deep_agent.templates.hr import HR
from deep_agent.templates.ecommerce import ECOMMERCE

# Dicionario central: name → AnalysisTemplate
TEMPLATES: dict[str, AnalysisTemplate] = {
    SALES.name: SALES,
    FINANCIAL.name: FINANCIAL,
    HR.name: HR,
    ECOMMERCE.name: ECOMMERCE,
}

__all__ = ["TEMPLATES", "AnalysisTemplate"]

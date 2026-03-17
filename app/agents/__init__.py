from app.agents.competitor_analyst import SPEC as COMPETITOR_ANALYST
from app.agents.edge_case_reviewer import SPEC as EDGE_CASE_REVIEWER
from app.agents.market_scout import SPEC as MARKET_SCOUT
from app.agents.product_designer import SPEC as PRODUCT_DESIGNER
from app.agents.risk_decision_analyst import SPEC as RISK_DECISION_ANALYST
from app.agents.strategy_architect import SPEC as STRATEGY_ARCHITECT


ALL_STAGES = [
    MARKET_SCOUT,
    COMPETITOR_ANALYST,
    STRATEGY_ARCHITECT,
    PRODUCT_DESIGNER,
    EDGE_CASE_REVIEWER,
    RISK_DECISION_ANALYST,
]

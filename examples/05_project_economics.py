"""
Example 5 — Project Economics

Demonstrates: npv, breakeven_price
"""
from kolmo_stats import npv, breakeven_price

# ── npv — offshore oil field ──────────────────────────────────────────────────
print("=== npv — offshore oil field ===")

# 10-year project: annual net cashflows after opex ($ million)
cashflows = [
    -50,   # year 1: pre-production capex drawdown (negative cf in year before prod)
     80,   # year 2: first oil
    120,   # year 3
    140,   # year 4
    130,   # year 5
    110,   # year 6
     90,   # year 7
     70,   # year 8
     50,   # year 9
     30,   # year 10
]
capex = 400   # $400M upfront

result = npv(cashflows, discount_rate=0.12, initial_investment=capex)
print(f"Cashflows: {cashflows}")
print(f"Upfront CAPEX: ${capex}M")
print(f"Discount rate: 12%")
print(f"NPV: ${result:.1f}M")
print("Project creates value." if result > 0 else "Project destroys value.")

print("\n--- explain ---")
detail = npv(cashflows, discount_rate=0.12, initial_investment=capex, explain=True)
print(detail)

# ── breakeven_price — LNG project ────────────────────────────────────────────
print("\n=== breakeven_price — LNG project ===")

project_life = 20          # years
annual_production = [4_000_000] * project_life   # MMBtu/year
fixed_opex = [50_000_000] * project_life          # $50M/year fixed
variable_opex_per_mmbtu = 0.80                    # $/MMBtu variable opex
capex_lng = 3_000_000_000                         # $3B upfront

price = breakeven_price(
    capex=capex_lng,
    fixed_opex=fixed_opex,
    variable_opex_per_unit=variable_opex_per_mmbtu,
    production=annual_production,
    discount_rate=0.10,
)
print(f"CAPEX:                ${capex_lng/1e9:.1f}B")
print(f"Annual production:    {annual_production[0]/1e6:.0f}M MMBtu")
print(f"Fixed OPEX/year:      ${fixed_opex[0]/1e6:.0f}M")
print(f"Variable OPEX:        ${variable_opex_per_mmbtu:.2f}/MMBtu")
print(f"Discount rate:        10%")
print(f"Breakeven price:      ${price:.2f}/MMBtu")
print(f"")
print(f"If LNG sells above ${price:.2f}/MMBtu the project is NPV positive.")

detail = breakeven_price(
    capex_lng, fixed_opex, variable_opex_per_mmbtu,
    annual_production, 0.10, explain=True
)
print("\n--- explain ---")
print(detail)

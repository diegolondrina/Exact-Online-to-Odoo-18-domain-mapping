# Cross-Domain Dependencies

## Migration Order
1. Foundational: res.company, res.users, res.currency, uom.uom, 
   account.tax, account.account, account.payment.term
2. Master data: product categories, products, partners, plans
3. Transactional: orders, lines, invoices

## Mapped (domain → workbook)
- Units of Measure: /mappings/uom_mapping.xlsx
- Subscriptions: /mappings/subscriptions_mapping.xlsx
- Contacts & Accounts: /mappings/contacts_mapping.xlsx
- Purchases: /mappings/purchases_mapping.xlsx
- Product Categories: /mappings/product_categories_mapping.xlsx

## Dependency Chain
```
uom.uom ────────────┐
product.category ───┼──►  product.template  ──►  sale.order / sale.order.line
(ItemGroups)        │     (Items)                (Subscriptions)
                    │
account.account ────┘     (GL accounts on product.category — pending)

res.partner ─┐
uom.uom ─────┼──►  purchase.order / purchase.order.line
product.product ──┘  (Purchases)
```
UoM must be migrated before Products, which must be migrated before
Subscriptions. The Items sheet in subscriptions_mapping.xlsx maps
`Unit` → `uom_id` (Relational) and relies on uom_mapping.xlsx for
the resolution lookup (Exact Unit Code → Odoo uom.uom via x_aa_code).

Purchases depend on: res.partner (Contacts), product.product (Items),
uom.uom (UoM), account.payment.term (Contacts) — all already mapped.

## Pending Dependencies
- account.account: 4 relational GL fields on product.category (GLCosts, GLRevenue, GLPurchasePriceDifference, GLStock) + 4 ambiguous GL fields preserved as custom (GLPurchaseAccount, GLStockVariance, GLCostsWIP, GLRevenueWIP). All GL resolution blocked until account.account is mapped.
- res.users: PurchaseAgent → user_id, Creator/Modifier → create_uid/write_uid (Purchases, Subscriptions, Product Categories)
- account.tax: VATCode → taxes_id on purchase.order.line (Purchases)
- account.analytic.account: CostCenter → analytic_distribution (Purchases)
- stock.picking.type: Warehouse → picking_type_id on purchase.order (Purchases)

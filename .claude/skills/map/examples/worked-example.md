# Worked Example

The following rows are extracted from a completed Subscriptions domain mapping (Exact Subscriptions → Odoo sale.order). They illustrate one of each category at the expected level of detail.

### Direct

| Exact Field | Exact Type | Category | Odoo Field | Odoo Type | Odoo Model | Notes |
|---|---|---|---|---|---|---|
| StartDate | Edm.DateTime | Direct | start_date | date | sale.order | Direct mapping. Exact DateTime → Odoo date (strip time component). |

The semantic match is unambiguous: both fields represent when the subscription begins. The only conversion needed is dropping the time component.

### Relational

| Exact Field | Exact Type | Category | Odoo Field | Odoo Type | Odoo Model | Notes |
|---|---|---|---|---|---|---|
| OrderedBy | Edm.Guid | Relational | partner_id | many2one → res.partner | sale.order | Subscriber account. Requires lookup: Exact Account GUID → Odoo res.partner. |

The field is a foreign key to another entity. The Notes specify what the resolution path is — which Exact table it comes from and which Odoo model it resolves to.

### Custom

| Exact Field | Exact Type | Category | Odoo Field | Odoo Type | Odoo Model | Notes |
|---|---|---|---|---|---|---|
| InvoiceDay | Edm.Byte | Custom | x_aa_invoice_day | integer | sale.order | Day-of-month (or weekday) for invoice generation. Odoo's sale.subscription.plan has billing_first_day (boolean: align to 1st), which is much simpler. No equivalent for arbitrary day selection. |

The Notes explain *why* there is no native equivalent — not just "no equivalent" but what Odoo offers instead and why it doesn't fit. This helps a reviewer understand the decision.

### Derived

| Exact Field | Exact Type | Category | Odoo Field | Odoo Type | Odoo Model | Notes |
|---|---|---|---|---|---|---|
| — | — | Derived | is_subscription | boolean | sale.order | Always set to True for migrated subscription records. |

No Exact source field. The Notes document the derivation logic — in this case a simple constant, but for more complex fields (like `subscription_state`) the Notes would describe the conditional logic.

### Skip

| Exact Field | Exact Type | Category | Odoo Field | Odoo Type | Odoo Model | Notes |
|---|---|---|---|---|---|---|
| OrderedByName | Edm.String | Skip | — | — | — | Denormalized display field. Value derivable from OrderedBy → res.partner.name. |

The justification is concise: it's a display copy, and the actual data lives on the relation. A reviewer can see at a glance that this field was evaluated, not overlooked.
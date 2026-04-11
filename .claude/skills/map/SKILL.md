---
name: map
description: Execute field-level mapping for a domain whose metadata 
  has been collected. Classifies every field, resolves dependencies, 
  produces the mapping table as CSV source files. Use after /new-domain 
  is complete.
---
# Map Domain: $ARGUMENTS

First verify that metadata files exist in `/metadata/exact/` and
`/metadata/odoo/` for this domain's tables. If any are missing, tell
the user which files are needed before proceeding — run /new-domain
if the domain hasn't been set up yet.

Read the collected metadata and reference @examples/worked-example.md
for the expected level of detail.

## Mapping Procedure
For each Exact→Odoo table pair:

1. **Table-level structural mapping** — document rationale 
   (e.g., "Exact Subscriptions → sale.order because...")
2. **Classify every Exact field** — work systematically:
   identity fields → relational → dates → amounts/quantities → audit
3. **Add Derived rows** for Odoo fields with no Exact source but 
   required for model function (e.g., is_subscription, state, type)
4. **Flag dependency chains** — if a mapping references an unmapped
   table, document it and alert the user
5. **Update references/dependency-tracker.md** — add new entries to
   Pending Dependencies and update Mapped when complete

Apply patterns from @reference/exact-patterns.md (audit fields, display fields, free fields).
Apply type conversion defaults from @reference/type-conversions.md.
Consult @reference/odoo-skip-patterns.md when filtering Odoo fields.

## Output Format
Write each table-pair mapping as a CSV in `mappings/data/{domain}/`.

**Filename convention:** `NN_ExactEntity-OdooModel.csv`
- `NN` = two-digit sequence number controlling sheet order (00, 01, ...)
- Example: `00_Subscriptions-sale.order.csv`

**CSV columns** (standard 8-column header, must match exactly):
```
Exact Field,Exact Type,Category,Odoo Field,Odoo Type,Odoo Model,Related Model,Notes
```

`Odoo Type` is the raw Odoo field type (e.g., `many2one`, `char`, `selection`).
`Related Model` is the target model for relational fields (e.g., `res.partner`) —
left empty for non-relational rows, `—` for Skip rows.

These CSVs are the **source of truth** — the xlsx workbooks are generated
from them. This keeps the mapping data human-readable, diffable, and
version-controllable as plain text.

Present mapping to user for review before proceeding to /deliver.
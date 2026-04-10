---
name: quality-gate
description: Run the quality gate checklist against a completed
  mapping before delivery. Verifies completeness and consistency.
  Use before /deliver or when reviewing a mapping.
disable-model-invocation: true
---
# Quality Gate: $ARGUMENTS

Read the CSV source files in `mappings/data/{domain}/` and verify
against all criteria:

## Structural checks
- [ ] CSVs exist in `mappings/data/{domain}/` with correct naming
      (`NN_[ExactEntity]-[OdooModel].csv`)
- [ ] Each CSV has the standard 7-column header:
      Exact Field, Exact Type, Category, Odoo Field, Odoo Type, Odoo Model, Notes
- [ ] Every Exact field in every in-scope metadata table has a row

## Classification checks
- [ ] Every row has a Category assigned (Direct/Relational/Custom/Derived/Skip)
- [ ] Every Relational row identifies target model + resolution path
- [ ] Every Custom row uses x_aa_ prefix + snake_case
- [ ] Every Derived row documents derivation logic in Notes
- [ ] Every Skip row has justification in Notes

## Completeness checks
- [ ] x_aa_exact_id present on every target Odoo model
- [ ] Cross-domain dependencies identified and documented in
      references/dependency-tracker.md
- [ ] Migration order for domain's tables is clear
- [ ] Odoo mandatory fields and behavioral flags accounted for

Report: pass/fail per item, with specifics on any failures.
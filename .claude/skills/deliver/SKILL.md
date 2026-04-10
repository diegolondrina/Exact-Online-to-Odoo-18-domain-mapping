---
name: deliver
description: Generate the final Excel workbook for a completed domain 
  mapping. Produces color-coded, formatted .xlsx output from CSV source
  files. Use after mapping is reviewed and approved.
---
# Deliver Mapping: $ARGUMENTS

Generate the Excel workbook from the CSV source files in
`mappings/data/{domain}/`, following @spec/output-spec.md.

## Delivery Steps

1. **Verify CSVs exist** in `mappings/data/{domain}/`. Each CSV
   represents one sheet, named `NN_[ExactEntity]-[OdooModel].csv`.
   If CSVs are missing, the mapping step was not completed — run
   /map first.

2. **Generate the workbook:**
   ```bash
   python generate_workbook.py {domain}
   ```
   This reads all CSVs in the domain folder, creates one sheet per CSV
   (filename becomes the sheet title: `ExactEntity → OdooModel`),
   appends the Legend sheet, and saves to
   `mappings/{domain}_mapping.xlsx`.

3. **Apply formatting:**
   ```bash
   python format_workbooks.py
   ```
   Applies all visual formatting (colors, fonts, borders, freeze panes,
   auto-filter) per @spec/output-spec.md.

Do **not** write one-off Python scripts to generate workbooks — the
general `generate_workbook.py` handles all domains.

## Present to User
- Summary of key decisions
- Notable asymmetries
- Open dependencies
- Migration order recommendation
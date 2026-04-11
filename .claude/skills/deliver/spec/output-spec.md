# Output Spec

## Pipeline

Mapping data flows through three stages:

1. **CSV source files** (`mappings/data/{domain}/`) — the source of truth.
   Written by /map, human-editable, diffable, version-controllable.
2. **`generate_workbook.py {domain}`** — reads CSVs, produces xlsx with
   proper sheet names and Legend.
3. **`format_workbooks.py`** — applies all visual formatting.

Never write one-off scripts to generate workbooks. Always use the
general pipeline.

## CSV Convention

Each table-pair mapping is one CSV file:

- **Location:** `mappings/data/{domain}/`
- **Filename:** `NN_ExactEntity-OdooModel.csv`
  - `NN` = two-digit sequence controlling sheet order (00, 01, ...)
  - The first hyphen separates the Exact entity from the Odoo model
    (Odoo model names may contain dots, e.g. `purchase.order.line`)
  - `generate_workbook.py` converts this to sheet title `ExactEntity → OdooModel`
- **Example:** `00_Subscriptions-sale.order.csv` → sheet "Subscriptions → sale.order"

## Workbook Structure

The deliverable for each mapping batch is an Excel workbook (.xlsx) with:

1. **One sheet per Exact-to-Odoo table mapping**, named
   `ExactEntity → OdooModel` (derived from CSV filename).

2. **Eight columns per sheet:**

   | Column | Content |
   |---|---|
   | Exact Field | The Exact field name (or "—" for Derived rows) |
   | Exact Type | The Exact EDM type (or "—" for Derived rows) |
   | Category | One of: Direct, Relational, Custom, Derived, Skip |
   | Odoo Field | Target Odoo field name, `x_aa_...` for Custom, or "—" for Skip |
   | Odoo Type | The raw Odoo field type (e.g. `many2one`, `char`, `selection`) |
   | Odoo Model | The target Odoo model |
   | Related Model | For relational fields, the target model (e.g. `res.partner`); empty for non-relational rows; `—` for Skip rows |
   | Notes | Rationale, conversion rules, caveats, cross-references |

3. **Formatting applied by `format_workbooks.py`:**
   - Color-coded Category column (Direct=blue, Relational=green, Custom=yellow, Derived=red, Skip=grey)
   - Header row: dark blue (#0B5394), white bold Arial 10pt, centered, wrapped
   - Data rows: Arial 10pt, wrap text, top-aligned, thin bottom border
   - Category column bold in data rows
   - Frozen header row (A2) with auto-filter
   - Standardized column widths

4. **A Legend sheet** explaining the five categories (appended automatically
   by `generate_workbook.py`).

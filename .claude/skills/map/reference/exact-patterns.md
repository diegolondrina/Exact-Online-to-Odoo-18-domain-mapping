## Audit Fields (present on nearly every table)
- Created → create_date (Direct)
- Creator → create_uid (Relational, default to admin)
- CreatorFullName → Skip
- Modified → write_date (Direct)
- Modifier → write_uid (Relational)
- ModifierFullName → Skip
- Division → company_id (Relational)

## Denormalized Display Fields
Pattern: SomeField (GUID) + SomeFieldCode + SomeFieldDescription
→ Map the GUID, skip the display copies with a note.

## Free Fields
FreeBoolField_01–05, FreeTextField_01–10, FreeNumberField_01–08, FreeDateField_01–05
→ Map as x_aa_free_bool_01 etc. Suggest user check actual population.

## CustomField Endpoint
"Custom field endpoint. Provided only for Premium users." → Always skip.

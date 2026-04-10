| Exact Type | Default Odoo Type | Notes |
|---|---|---|
| Edm.Guid | char | Unless foreign key → many2one |
| Edm.String | char | Use text for known long-content fields |
| Edm.Int16/Int32 | integer | |
| Edm.Double | float | monetary only if Odoo target is monetary |
| Edm.DateTime | datetime or date | Strip time when mapping to date |
| Edm.Boolean | boolean | |
| Edm.Byte | boolean or integer | 0/1 flags → boolean; numeric → integer |
| Edm.Binary | binary | Typically images |

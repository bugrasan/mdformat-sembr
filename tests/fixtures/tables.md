| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `min_chars` | int | `15` | Minimum length of the segment before a break is allowed. |
| `abbreviations` | list[str] | see below | Tokens after which no sentence break is inserted. |
| `break_clauses` | bool | `false` | Enable clause-level breaks (SemBr "SHOULD"). Off by default. |
| `clause_chars` | str | `",;:—"` | Clause punctuation set (only used when `break_clauses` true). |

Some prose after the table. First sentence here. Second sentence follows.

| Left | Center | Right |
| :--- | :----: | ----: |
| alpha | beta sentence. Next sentence. | gamma |
| delta | epsilon | zeta |

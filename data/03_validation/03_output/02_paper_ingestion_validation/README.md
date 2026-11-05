# Paper-Ingestion Knowledge-Graph Validation Outputs

This directory retains only three machine-readable UTF-8 BOM CSV files that Excel can open directly:

1. `01_field_semantic_similarity_details.csv`: semantic-similarity details for 35 papers × 28 fields. Titles, years, and DOIs use normalized exact matching; the remaining comparable fields use cosine similarity between multilingual sentence embeddings.
2. `02_field_factual_accuracy_details.csv`: factual-accuracy details for the same 980 fields, including whether each field is included in the denominator, whether the fact is correct, the LLM judgment explanation, and the reason for missing data.
3. `03_overall_summary.csv`: a one-row overall summary containing semantic similarity, factual accuracy, and coverage counts.

Both detail tables are sorted by paper → model instance → field and retain the field code, English/Chinese field names, original human-Gold value, Gold English translation, knowledge-graph value, Gold file, and matching method. For long text, consecutive whitespace is collapsed into a single space without truncating the content, so each field record occupies only one row in the CSV for convenient filtering and auditing.

Overall semantic similarity is averaged only across fields for which both sides have values. Factual accuracy is the number of fields judged correct by the LLM divided by the number of fields actually included in factual judgment. Fields missing on one side and fields missing on both sides are excluded from the denominator, and an explicit status is retained for them in both detail tables.

If knowledge-graph records cannot be matched one-to-one with the human Gold by DOI or title, the program raises an error and stops saving output; it no longer generates an empty `issues.csv` with no downstream use.

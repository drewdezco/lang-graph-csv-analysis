# Test Data Files

This folder contains sample CSV files to test the data quality analysis pipeline.

## Files Description

### `sample_good.csv`
A clean dataset with minimal issues. Good for testing basic schema profiling.

### `sample_nulls.csv`
Contains various null/missing values across different columns to test null detection:
- Missing age (row 2)
- Missing email (row 3)
- Missing salary (row 4)
- Missing department (rows 5, 7)
- Missing name (row 6)

### `sample_duplicates.csv`
Contains duplicate rows to test duplicate detection:
- Rows 1 and 4 are identical
- Rows 2 and 6 are identical
- Rows 3 and 8 are identical

### `sample_type_mismatch.csv`
Contains numeric values stored as text (with currency symbols and commas) to test type mismatch detection:
- Salary column has values like "$50,000" and "$70,000" instead of numeric values

### `sample_empty_column.csv`
Contains an empty column (`notes`) to test empty column detection.

### `sample_mixed_issues.csv`
A comprehensive test file with multiple types of issues:
- Null values in various columns
- Duplicate rows (rows 1 and 4, rows 2 and 8)
- Type mismatches (salary with currency symbols)
- Empty values

## Usage

Upload any of these files through the frontend interface or via the API to test different aspects of the data quality pipeline:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_data/sample_mixed_issues.csv"
```

## Expected Results

- **Schema Profile**: All files should show column information, types, null counts, and sample values
- **Quality Issues**: Each file should trigger different issue types
- **Explanations**: LLM-generated explanations for detected issues
- **Recommendations**: LLM-generated fix recommendations


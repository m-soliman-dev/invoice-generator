# invoice-generator

Turn a JSON list of items into a clean, printable PDF invoice. The PDF is
written directly with Python's standard library - no packages to install, no
internet needed.

## What it does

- Reads client name, line items, tax and discount from a small JSON file
- Calculates line totals, subtotal, discount, tax and the grand total
- Writes a one-page A4 PDF invoice with a proper item table
- Handles any currency label (EGP, USD, EUR, ...)

## Usage

```bash
python invoice_generator.py example_invoice.json
# saved invoice-001.pdf - total 4,446.00 EGP

python invoice_generator.py example_invoice.json --output my-invoice.pdf
```

The JSON file looks like this:

```json
{
  "number": "001",
  "from": "My Business",
  "client": "Client Name",
  "currency": "EGP",
  "tax_percent": 14,
  "discount_percent": 0,
  "items": [
    {"description": "Website page", "quantity": 2, "unit_price": 500}
  ]
}
```

Note: the built-in PDF writer uses the Helvetica font, so invoice text should
use Latin characters (English names and numbers work perfectly).

## Running the tests

```bash
python -m unittest test_invoice_generator.py -v
```

## What I learned building this

- How a PDF file is structured (objects, xref table, content streams) by
  writing one byte-for-byte with no libraries
- Careful money calculations with rounding at every step
- Separating calculation, layout and output so each part is testable

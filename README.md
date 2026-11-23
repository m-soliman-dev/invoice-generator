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

## Case study

**The problem.** A freelancer needs a clean, printable invoice fast, without
paying for software or trusting an online generator with client data.

**Technologies.** Python 3 standard library only. The PDF is written
directly, byte for byte - PDF objects, the xref table and the content stream
- using the built-in Helvetica fonts. Calculation, layout and file output
are separate functions, so each is unit-tested on its own, and money is
rounded at every step.

**The result.** A small JSON file (client, items, tax, discount) becomes a
one-page A4 PDF invoice with an item table, subtotal, discount, tax and
grand total, in any currency label.

**Limits (being upfront).** One page per invoice, and the built-in Helvetica
font covers Latin characters, so item descriptions are written in English -
rendering Arabic text would require embedding a font, which is where a
library such as reportlab would take over. Writing the PDF by hand was a
deliberate exercise to understand the format; for heavy production use a
dedicated library is the pragmatic choice.

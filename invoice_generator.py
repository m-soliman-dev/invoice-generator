#!/usr/bin/env python3
"""invoice-generator - turn a list of items into a clean PDF invoice.

Reads invoice details from a JSON file (client name, line items, tax and
discount) and writes a professional one-page PDF. Pure Python 3 standard
library: the PDF is written directly, no packages to install.

Usage:
    python invoice_generator.py invoice.json
    python invoice_generator.py invoice.json --output invoice-042.pdf

JSON format:
    {
      "number": "042",
      "from": "My Business",
      "client": "Client Name",
      "currency": "EGP",
      "tax_percent": 14,
      "discount_percent": 0,
      "items": [
        {"description": "Website page", "quantity": 2, "unit_price": 500}
      ]
    }
"""

import json
import sys
from datetime import date


# ---------- calculations ----------

def calculate(invoice):
    """Return the invoice with per-line totals and grand totals added."""
    items = []
    for item in invoice["items"]:
        line_total = round(item["quantity"] * item["unit_price"], 2)
        items.append({**item, "line_total": line_total})
    subtotal = round(sum(i["line_total"] for i in items), 2)
    discount = round(subtotal * invoice.get("discount_percent", 0) / 100, 2)
    taxable = subtotal - discount
    tax = round(taxable * invoice.get("tax_percent", 0) / 100, 2)
    total = round(taxable + tax, 2)
    return {**invoice, "items": items, "subtotal": subtotal,
            "discount": discount, "tax": tax, "total": total}


# ---------- minimal PDF writer (standard library only) ----------

def _escape(text):
    """Escape text for a PDF string and keep it in Latin-1."""
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_pdf(lines, title):
    """Build a simple one-page PDF from [(x, y, size, bold, text), ...].

    Coordinates are in points from the bottom-left of an A4 page.
    """
    content = []
    for x, y, size, bold, text in lines:
        font = "F2" if bold else "F1"
        content.append(f"BT /{font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET")
    stream = "\n".join(content).encode("latin-1")

    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                   b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> "
                   b"/Contents 6 0 R >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Length %d >>\nstream\n%s\nendstream"
                   % (len(stream), stream))

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref_start = len(pdf)
    pdf += b"xref\n0 %d\n" % (len(objects) + 1)
    pdf += b"0000000000 65535 f \n"
    for offset in offsets:
        pdf += b"%010d 00000 n \n" % offset
    pdf += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objects) + 1, xref_start))
    return bytes(pdf)


def layout(invoice):
    """Turn a calculated invoice into positioned text lines for the PDF."""
    currency = invoice.get("currency", "")
    money = lambda value: f"{value:,.2f} {currency}".strip()
    lines = [
        (50, 790, 24, True, "INVOICE"),
        (50, 768, 11, False, f"Number: {invoice.get('number', '-')}"
                             f"    Date: {invoice.get('date', date.today().isoformat())}"),
        (50, 740, 12, True, f"From: {invoice.get('from', '')}"),
        (50, 722, 12, True, f"To: {invoice.get('client', '')}"),
        (50, 690, 11, True, "Description"),
        (300, 690, 11, True, "Qty"),
        (350, 690, 11, True, "Unit price"),
        (450, 690, 11, True, "Total"),
    ]
    y = 668
    for item in invoice["items"]:
        lines.append((50, y, 10, False, item["description"][:60]))
        lines.append((300, y, 10, False, f"{item['quantity']:g}"))
        lines.append((350, y, 10, False, money(item["unit_price"])))
        lines.append((450, y, 10, False, money(item["line_total"])))
        y -= 20
        if y < 200:
            break  # keep the invoice on one page
    y -= 12
    lines.append((350, y, 11, False, f"Subtotal:  {money(invoice['subtotal'])}"))
    y -= 18
    if invoice["discount"]:
        lines.append((350, y, 11, False,
                      f"Discount:  -{money(invoice['discount'])}"))
        y -= 18
    if invoice["tax"]:
        lines.append((350, y, 11, False, f"Tax:       {money(invoice['tax'])}"))
        y -= 18
    lines.append((350, y, 13, True, f"Total:     {money(invoice['total'])}"))
    return lines


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("invoice_json", help="JSON file with the invoice data")
    parser.add_argument("--output", help="output PDF file name")
    args = parser.parse_args()

    try:
        with open(args.invoice_json, encoding="utf-8") as handle:
            invoice = calculate(json.load(handle))
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    output = args.output or f"invoice-{invoice.get('number', 'draft')}.pdf"
    with open(output, "wb") as handle:
        handle.write(build_pdf(layout(invoice), title="Invoice"))
    print(f"saved {output} - total {invoice['total']:,.2f} "
          f"{invoice.get('currency', '')}".strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

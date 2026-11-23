import unittest

from invoice_generator import build_pdf, calculate, layout


def sample_invoice(**overrides):
    invoice = {
        "number": "001",
        "from": "Mohamed Soliman",
        "client": "Corner Shop",
        "currency": "EGP",
        "tax_percent": 14,
        "discount_percent": 10,
        "items": [
            {"description": "Website page", "quantity": 2, "unit_price": 500},
            {"description": "Logo", "quantity": 1, "unit_price": 300},
        ],
    }
    invoice.update(overrides)
    return invoice


class CalculateTest(unittest.TestCase):
    def test_line_totals_and_grand_total(self):
        invoice = calculate(sample_invoice())
        self.assertEqual(invoice["items"][0]["line_total"], 1000.0)
        self.assertEqual(invoice["subtotal"], 1300.0)
        self.assertEqual(invoice["discount"], 130.0)
        self.assertEqual(invoice["tax"], 163.8)
        self.assertEqual(invoice["total"], 1333.8)

    def test_no_tax_no_discount(self):
        invoice = calculate(sample_invoice(tax_percent=0, discount_percent=0))
        self.assertEqual(invoice["discount"], 0)
        self.assertEqual(invoice["tax"], 0)
        self.assertEqual(invoice["total"], 1300.0)


class PdfTest(unittest.TestCase):
    def test_pdf_structure(self):
        invoice = calculate(sample_invoice())
        pdf = build_pdf(layout(invoice), title="Invoice")
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"xref", pdf)
        self.assertIn(b"trailer", pdf)

    def test_pdf_contains_invoice_text(self):
        invoice = calculate(sample_invoice())
        pdf = build_pdf(layout(invoice), title="Invoice")
        self.assertIn(b"Corner Shop", pdf)
        self.assertIn(b"INVOICE", pdf)


if __name__ == "__main__":
    unittest.main()

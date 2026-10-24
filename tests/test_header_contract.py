"""Static contract checks, not a replacement for Odoo/browser integration tests."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "alvina_website_order_entry"


class HeaderContractTest(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(ADDON / "views/website_templates.xml")

    def test_only_verified_website_dependency_and_views(self):
        manifest = ast.literal_eval((ADDON / "__manifest__.py").read_text())
        self.assertEqual(manifest["depends"], ["website", "alvinha_mrp"])
        self.assertEqual(
            {item.attrib["inherit_id"] for item in self.tree.findall("template")},
            {"website.navbar_nav", "website.submenu"},
        )

    def test_real_date_input_is_extended_without_replacing_form(self):
        tree = ET.parse(ADDON / "views/production_form.xml")
        template = tree.find("template")
        self.assertEqual(template.attrib["inherit_id"], "alvinha_mrp.production_form")
        operation = template.find("xpath")
        self.assertEqual(operation.attrib["position"], "attributes")
        self.assertIn("input[@name='date_order']", operation.attrib["expr"])
        attrs = {node.attrib["name"]: node.text for node in operation}
        self.assertEqual(attrs["t-att-value"], "today")
        self.assertEqual(attrs["t-att-min"], "today")
        self.assertEqual(attrs["required"], "1")

    def test_single_unconditional_link_precedes_menu_slot(self):
        template = self.tree.find("template[@id='navbar_order_entry']")
        xpath = template.find("xpath")
        self.assertEqual(xpath.attrib, {"expr": "//t[@t-out='0']", "position": "before"})
        links = template.findall(".//a")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].attrib["href"], "/portal/production/new")
        self.assertEqual(links[0].text, "Realizar Pedido")
        self.assertFalse(template.findall(".//*[@t-if]"))

    def test_menu_duplicate_filter_handles_suffixes_and_empty_urls(self):
        attributes = self.tree.findall(".//attribute")
        self.assertEqual(len(attributes), 2)
        for attribute in attributes:
            for url, visible in [
                ("/portal/production/new", False),
                ("/portal/production/new/", False),
                ("/portal/production/new?x=1#form", False),
                ("/contactus", True), (None, True), ("", True),
            ]:
                with self.subTest(url=url, branch=attribute.attrib["name"]):
                    submenu = SimpleNamespace(_clean_url=lambda: url)
                    self.assertEqual(eval(attribute.attrib["add"], {"__builtins__": {}}, {
                        "submenu": submenu,
                    }), visible)

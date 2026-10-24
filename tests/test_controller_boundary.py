"""Exercise our real controller with stand-ins for Odoo and the parent.

These prove preconditions and delegation, not HTTP dispatch or real ORM writes.
"""

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ADDON = Path(__file__).resolve().parents[1] / "alvina_website_order_entry"
NOW = datetime(2026, 10, 24, 17, tzinfo=timezone.utc)


def module(name, **attrs):
    value = ModuleType(name)
    value.__dict__.update(attrs)
    return value


def route(**routing):
    def decorate(method):
        method.routing = routing
        return method
    return decorate


class ControllerBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.request = SimpleNamespace(
            env=object(), validate_csrf=Mock(side_effect=lambda token: token == "valid"),
        )
        self.parent_form = Mock(return_value=SimpleNamespace(qcontext={
            "today": "wrong-zone", "companies": [1], "agrupadores": [2],
        }))
        self.parent_create = Mock(return_value={"redirect_url": "/portal/production/success"})
        parent = type("OriginalController", (), {
            "portal_production_form": self.parent_form,
            "portal_create_production": self.parent_create,
        })
        packages = {
            "odoo": module("odoo", http=SimpleNamespace(route=route)),
            "odoo.http": module("odoo.http", request=self.request),
            "odoo.addons.alvinha_mrp.controllers.main": module(
                "odoo.addons.alvinha_mrp.controllers.main", PortalProductionController=parent,
            ),
            "_alvina_boundary": module("_alvina_boundary", __path__=[str(ADDON)]),
            "_alvina_boundary.controllers": module(
                "_alvina_boundary.controllers", __path__=[str(ADDON / "controllers")],
            ),
        }
        self.modules_patch = patch.dict(sys.modules, packages)
        self.modules_patch.start()
        self.addCleanup(self.modules_patch.stop)
        spec = importlib.util.spec_from_file_location(
            "_alvina_boundary.controllers.portal", ADDON / "controllers/portal.py",
        )
        self.portal = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.portal)
        real_validate = self.portal.validate_new_order_date
        self.portal.validate_new_order_date = lambda value: real_validate(value, now=NOW)
        self.controller = self.portal.AlvinaOrderEntryController()

    def test_form_reuses_parent_and_replaces_only_date(self):
        with patch.object(self.portal, "new_order_date_values", return_value={
            "default_date": "2026-10-25", "min_date": "2026-10-25",
        }):
            response = self.controller.portal_production_form(existing="preserved")
        self.parent_form.assert_called_once_with(existing="preserved")
        self.assertEqual(response.qcontext, {
            "today": "2026-10-25", "companies": [1], "agrupadores": [2],
        })

    def test_controller_environment_uses_request(self):
        self.assertIs(self.controller.env, self.request.env)

    def test_routes_retain_authenticated_access(self):
        self.assertEqual(self.controller.portal_production_form.routing, {"auth": "user"})
        self.assertEqual(self.controller.portal_create_production.routing, {
            "auth": "user", "methods": ["POST"],
        })

    def test_valid_batch_is_delegated_once_with_all_values_unchanged(self):
        payload = {
            "csrf_token": "valid", "date_order": "2026-10-25", "partner_id": 2,
            "company_id": 3, "agrupador_id": 4, "exist_other_orders": True,
            "lines": [{"product_id": 5, "qty": 10}, {"product_id": 6, "qty": 20}],
        }
        result = self.controller.portal_create_production(**payload)
        self.parent_create.assert_called_once_with(**payload)
        self.assertEqual(result, {"redirect_url": "/portal/production/success"})

    def test_invalid_date_never_reaches_order_creation(self):
        for date in (None, "", "2026-10-24", "2026-10-23", "2026-02-30", "garbage"):
            with self.subTest(date=date):
                result = self.controller.portal_create_production(
                    csrf_token="valid", date_order=date, lines=[{"qty": 1}],
                )
                self.assertIn("error", result)
                self.assertNotIn("redirect_url", result)
        self.parent_create.assert_not_called()

    def test_absent_or_invalid_csrf_never_reaches_order_creation(self):
        for token in (None, "", "forged", 123, []):
            with self.subTest(token=token):
                result = self.controller.portal_create_production(
                    csrf_token=token, date_order="2026-10-25",
                )
                self.assertIn("error", result)
        self.parent_create.assert_not_called()

    def test_malformed_csrf_does_not_crash(self):
        self.request.validate_csrf.side_effect = ValueError("malformed")
        result = self.controller.portal_create_production(
            csrf_token="broken", date_order="2026-10-25",
        )
        self.assertIn("error", result)
        self.parent_create.assert_not_called()

    def test_original_business_error_is_preserved(self):
        self.parent_create.return_value = {"error": "Agrupador no disponible"}
        self.assertEqual(self.controller.portal_create_production(
            csrf_token="valid", date_order="2026-10-26",
        ), {"error": "Agrupador no disponible"})

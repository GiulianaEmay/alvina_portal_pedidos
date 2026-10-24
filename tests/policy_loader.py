"""Load the pure date policy without bootstrapping an Odoo registry."""

import importlib.util
from pathlib import Path


path = Path(__file__).resolve().parents[1] / "alvina_website_order_entry/services/order_date.py"
spec = importlib.util.spec_from_file_location("alvina_date_policy_test", path)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

import unittest
from datetime import date, datetime, timezone

from policy_loader import policy

InvalidOrderDate = policy.InvalidOrderDate
minimum_order_date = policy.minimum_order_date
new_order_date_values = policy.new_order_date_values
validate_new_order_date = policy.validate_new_order_date


class OrderDatePolicyTest(unittest.TestCase):
    now = datetime(2026, 10, 24, 17, tzinfo=timezone.utc)

    def test_new_form_default_and_minimum(self):
        self.assertEqual(new_order_date_values(now=self.now), {
            "default_date": "2026-10-25", "min_date": "2026-10-25",
        })

    def test_lima_day_changes_at_0500_utc(self):
        before = datetime(2026, 10, 25, 4, 59, 59, tzinfo=timezone.utc)
        after = datetime(2026, 10, 25, 5, tzinfo=timezone.utc)
        self.assertEqual(minimum_order_date(now=before), date(2026, 10, 25))
        self.assertEqual(minimum_order_date(now=after), date(2026, 10, 26))
        with self.assertRaises(InvalidOrderDate):
            validate_new_order_date("2026-10-25", now=after)

    def test_year_and_leap_boundaries(self):
        for instant, expected in [
            (datetime(2026, 12, 31, 18, tzinfo=timezone.utc), date(2027, 1, 1)),
            (datetime(2028, 2, 28, 18, tzinfo=timezone.utc), date(2028, 2, 29)),
        ]:
            with self.subTest(instant=instant):
                self.assertEqual(minimum_order_date(now=instant), expected)

    def test_tomorrow_and_future_are_accepted(self):
        for value in ("2026-10-25", "2026-11-30", date(2027, 1, 1)):
            with self.subTest(value=value):
                self.assertIsInstance(validate_new_order_date(value, now=self.now), date)

    def test_today_and_past_are_rejected(self):
        for value in ("2026-10-24", "2026-10-23", date(2000, 1, 1)):
            with self.subTest(value=value), self.assertRaisesRegex(
                InvalidOrderDate, "25/10/2026"
            ):
                validate_new_order_date(value, now=self.now)

    def test_missing_malformed_and_tampered_values(self):
        for value in (None, "", "2026-02-30", "25/10/2026", "20261025",
                      "2026-10-25T00:00:00", " 2026-10-25", 123, [],
                      datetime(2026, 10, 25, tzinfo=timezone.utc)):
            with self.subTest(value=value), self.assertRaises(InvalidOrderDate):
                validate_new_order_date(value, now=self.now)

    def test_naive_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            minimum_order_date(now=datetime(2026, 10, 24))

    def test_default_uses_current_lima_date(self):
        # Bound both sides so this remains valid across a midnight boundary.
        before = minimum_order_date()
        actual = new_order_date_values()
        after = minimum_order_date()
        self.assertIn(actual["default_date"], {before.isoformat(), after.isoformat()})
        self.assertEqual(actual["default_date"], actual["min_date"])

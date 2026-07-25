import unittest
from unittest.mock import patch

from src.config import service_name


class ConfigTest(unittest.TestCase):
    def test_service_name_uses_default(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual("demo-service", service_name())


if __name__ == "__main__":
    unittest.main()

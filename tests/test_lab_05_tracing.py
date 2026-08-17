from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SOLUTION_FILE = (
    Path(__file__).parents[1]
    / "lab-05-observability-evaluation"
    / "solution"
    / "tracing_setup.py"
)
RUNNER_FILE = SOLUTION_FILE.with_name("run_traced_workflow.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tracing_setup = load_module("tracing_setup", SOLUTION_FILE)
run_traced_workflow = load_module("run_traced_workflow", RUNNER_FILE)


class TracingSetupTests(unittest.TestCase):
    def test_configures_maf_otel_with_safe_defaults(self) -> None:
        with patch.object(tracing_setup, "configure_otel_providers") as configure:
            tracing_setup.configure_workshop_tracing()

        configure.assert_called_once_with(
            vs_code_extension_port=4317,
            enable_sensitive_data=False,
        )

    def test_sensitive_capture_must_be_explicit(self) -> None:
        with patch.object(tracing_setup, "configure_otel_providers") as configure:
            tracing_setup.configure_workshop_tracing(
                port=5000,
                capture_sensitive_data=True,
            )

        configure.assert_called_once_with(
            vs_code_extension_port=5000,
            enable_sensitive_data=True,
        )

    def test_detects_when_trace_receiver_is_unavailable(self) -> None:
        with patch.object(
            run_traced_workflow.socket,
            "create_connection",
            side_effect=ConnectionRefusedError,
        ):
            self.assertFalse(run_traced_workflow.trace_receiver_is_running())

    def test_detects_when_trace_receiver_is_running(self) -> None:
        connection = unittest.mock.MagicMock()
        with patch.object(
            run_traced_workflow.socket,
            "create_connection",
            return_value=connection,
        ) as create_connection:
            self.assertTrue(run_traced_workflow.trace_receiver_is_running())

        create_connection.assert_called_once_with(("localhost", 4317), timeout=1.0)
        connection.__enter__.assert_called_once_with()
        connection.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
import pytest
import os
import sys
import json
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import AgentController, QATestContext


class TestDashboardGeneration:
    @pytest.fixture
    def controller(self):
        return AgentController()

    @pytest.fixture
    def mock_contexto(self):
        contexto = QATestContext()
        contexto.repo_name = "python-simple-rest-api"
        contexto.repo_path = "projects/python-simple-rest-api"
        contexto.cobertura_inicial = "42%"
        contexto.cobertura_final = "63%"
        contexto.resultado_testes_depois_bruto = """
============================= test session starts =============================
tests/test_server.py ..........                                          [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.3-final-0 _______________
Name                   Stmts   Miss  Cover
------------------------------------------
server.py                100     37    63%
tests\test_server.py      56      0   100%
------------------------------------------
TOTAL                    156     37    63%
============================= 10 passed in 0.02s
        """
        contexto.start_time = datetime.now()
        return contexto

    def test_parse_coverage(self, controller):
        assert controller._parse_coverage("42%") == 42.0
        assert controller._parse_coverage("63.5%") == 63.5
        assert controller._parse_coverage("Não detectada") == 0.0
        assert controller._parse_coverage("") == 0.0

    def test_parse_test_logs(self, controller):
        logs = """
============================= test session starts =============================
tests/test_server.py ..........                                          [100%]
============================= 10 passed in 0.02s
        """
        result = controller._parse_test_logs(logs)
        assert result["passed"] == 10
        assert result["failed"] == 0

    def test_parse_test_logs_with_coverage(self, controller):
        logs = """
============================= test session starts =============================
tests/test_server.py ..........                                          [100%]
TOTAL                    156     37    63%
============================= 10 passed in 0.02s
        """
        result = controller._parse_test_logs(logs)
        assert result["passed"] == 10
        assert result["failed"] == 0
        assert result["coverage"] == 63.0

    def test_parse_test_logs_with_failures(self, controller):
        logs = """
============================= test session starts =============================
tests/test_server.py ..F..F..                                          [100%]
============================= 2 failed, 8 passed in 0.02s
        """
        result = controller._parse_test_logs(logs)
        assert result["passed"] == 8
        assert result["failed"] == 2

    def test_update_history_trend(self, controller):
        history = {
            "labels": ["Run 1"],
            "cov_before": [40.0],
            "cov_after": [60.0],
            "tests_exec": [50],
            "tests_fail": [0],
            "gen_time": [100],
            "exec_time": [10],
        }
        qa_data = {
            "coverage": {"before_pct": 42.0, "after_pct": 63.0},
            "tests": {"total_executed": 60, "failures": 0},
            "performance": {
                "generation_time_seconds": 120,
                "execution_time_seconds": 15,
            },
        }
        result = controller._update_history_trend(history, qa_data)

        assert len(result["labels"]) == 2
        assert result["cov_before"][-1] == 42.0
        assert result["cov_after"][-1] == 63.0

    def test_inject_qa_data_into_html(self, controller):
        template = """<!DOCTYPE html>
<html>
<script>
    const __QA_DATA__ = {"old": "data"};
</script>
</html>"""

        qa_data = {
            "metadata": {"run_id": "test-123", "timestamp": "2026-04-04"},
            "coverage": {
                "before_pct": 42.0,
                "after_pct": 63.0,
                "delta_absolute": 21.0,
                "delta_percentual": 50.0,
            },
            "tests": {"total_created": 10, "total_executed": 10, "failures": 0},
            "performance": {
                "generation_time_seconds": 120,
                "execution_time_seconds": 15,
            },
            "breakdown": [],
            "insights": {"en": ["test"], "pt": ["teste"]},
            "history_trend": {
                "labels": [],
                "cov_before": [],
                "cov_after": [],
                "tests_exec": [],
                "tests_fail": [],
                "gen_time": [],
                "exec_time": [],
            },
        }

        result = controller._inject_qa_data_into_html(template, qa_data)

        assert "__QA_DATA__" in result
        assert "test-123" in result
        assert "42.0" in result
        assert "63.0" in result

    @pytest.mark.asyncio
    async def test_gerar_dashboard_full(self, controller, mock_contexto):
        import tempfile
        from core.config import settings

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = os.path.join(tmpdir, "test-project")
            os.makedirs(project_dir)

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            mock_contexto.repo_path = project_dir

            with patch.object(settings, "BASE_DIR", base_dir):
                with patch.object(settings, "TMP_DIR", tmpdir):
                    tempo_total = 5

                    await controller._gerar_dashboard(mock_contexto, tempo_total)

                    json_path = os.path.join(project_dir, "qagent_metrics_log.json")
                    html_path = os.path.join(project_dir, "qa_coverage_dashboard.html")

                    assert os.path.exists(json_path), "JSON log should be created"
                    assert os.path.exists(html_path), "HTML dashboard should be created"

                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    assert data["coverage"]["before_pct"] == 42.0
                    assert data["coverage"]["after_pct"] == 63.0
                    assert data["tests"]["total_executed"] == 10
                    assert data["tests"]["failures"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

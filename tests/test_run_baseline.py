
from unittest.mock import MagicMock, patch

from veriquery.benchmark.executor import BenchmarkRunSummary

from veriquery.benchmark import run_baseline


def test_dry_run_does_not_initialize_gemini(capsys):
    with patch.object(
        run_baseline,
        "GeminiSQLClient",
    ) as mock_client:
        with patch.object(
            run_baseline,
            "load_dev_questions",
        ) as mock_loader:
            with patch.object(
                run_baseline,
                "prepare_benchmark_run",
            ) as mock_prepare:

                mock_loader.return_value = [
                    MagicMock() for _ in range(40)
                ]

                mock_prepare.return_value = [
                    MagicMock() for _ in range(39)
                ]

                with patch(
                    "sys.argv",
                    ["run_baseline", "--dry-run"],
                ):
                    run_baseline.main()

        mock_client.assert_not_called()

    output = capsys.readouterr().out

    assert "Development questions loaded: 40" in output
    assert "Pending questions: 39" in output
    assert "DRY RUN COMPLETE" in output
    assert "No Gemini API requests were made." in output


def test_default_run_configuration_skips_failed_attempts():
    with patch.object(
        run_baseline,
        "load_dev_questions",
        return_value=[],
    ), patch.object(
        run_baseline,
        "ExperimentRecorder",
    ), patch.object(
        run_baseline,
        "prepare_benchmark_run",
        return_value=[],
    ) as mock_prepare, patch(
        "sys.argv",
        ["run_baseline", "--dry-run"],
    ):
        run_baseline.main()

    config = mock_prepare.call_args.kwargs["config"]

    assert config.retry_failed is False


def test_retry_failed_flag_is_passed_to_run_configuration():
    with patch.object(
        run_baseline,
        "load_dev_questions",
        return_value=[],
    ), patch.object(
        run_baseline,
        "ExperimentRecorder",
    ), patch.object(
        run_baseline,
        "prepare_benchmark_run",
        return_value=[],
    ) as mock_prepare, patch(
        "sys.argv",
        ["run_baseline", "--retry-failed", "--dry-run"],
    ):
        run_baseline.main()

    config = mock_prepare.call_args.kwargs["config"]

    assert config.retry_failed is True


def test_empty_pending_list_does_not_initialize_gemini(capsys):
    with patch.object(
        run_baseline,
        "load_dev_questions",
        return_value=[],
    ), patch.object(
        run_baseline,
        "prepare_benchmark_run",
        return_value=[],
    ), patch.object(
        run_baseline,
        "GeminiSQLClient",
    ) as mock_client, patch(
        "sys.argv",
        ["run_baseline"],
    ):
        run_baseline.main()

    mock_client.assert_not_called()

    output = capsys.readouterr().out
    assert "No pending questions. Nothing to execute." in output


def test_normal_run_executes_pending_questions(capsys):
    pending_questions = [MagicMock(), MagicMock()]

    fake_summary = BenchmarkRunSummary(
        total_questions=2,
        successful=1,
        failed=1,
        skipped=0,
    )

    with patch.object(
        run_baseline,
        "load_dev_questions",
        return_value=[],
    ), patch.object(
        run_baseline,
        "prepare_benchmark_run",
        return_value=pending_questions,
    ), patch.object(
        run_baseline,
        "GeminiSQLClient",
    ) as mock_client, patch.object(
        run_baseline,
        "BenchmarkExecutor",
    ) as mock_executor, patch(
        "sys.argv",
        ["run_baseline"],
    ):
        mock_executor.return_value.execute.return_value = fake_summary

        run_baseline.main()

    mock_client.assert_called_once()
    mock_executor.assert_called_once()

    mock_executor.return_value.execute.assert_called_once_with(
        pending_questions
    )

    output = capsys.readouterr().out

    assert "Processed: 2" in output
    assert "Successful: 1" in output
    assert "Failed: 1" in output

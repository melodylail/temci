"""
Tests for reporters
"""
import json

from tests.utils import run_temci, run_temci_proc


def test_console_reporter_auto_mode():
    d = lambda d: {
        "attributes": {"description": "XYZ" + d},
        "data": {"p": [1]}
    }
    out = run_temci("report in.yaml --console_mode auto",
                    files={
                        "in.yaml": [d(""), d(""), d(""), d("W"), d("X")]
                    }).out
    assert "Report for XYZ" in out
    assert any("XYZ [1]" in l and "XYZ [2]" in l for l in out.split("\n"))
    assert "XYZX" in out


def test_support_multiple_inputs():
    d = lambda: {
        "attributes": {"description": "XYZ"},
        "data": {"p": [1]}
    }
    out = run_temci("report in1.yaml in2.yaml --console_mode auto",
                    files={
                        "in1.yaml": [d()],
                        "in2.yaml": [d(), d()]
                    }).out
    assert any("XYZ [1]" in l and "XYZ [2]" in l for l in out.split("\n"))


def test_html2_with_single():
    assert "report.html" in run_temci("report --reporter html2 in.yaml", files={
        "in.yaml": [
            {
                "attributes": {"description": "XYZ"},
                "data": {"p": [1]}
            }
        ]
    }).file_contents


def test_properties_regexp():
    out = run_temci(r"report in.yaml --properties 'p.*'", files={
        "in.yaml": [
            {
                "attributes": {"description": "XYZ"},
                "data": {"p456": [1], "z111": [2]}
            }
        ]
    }).out
    assert "p456" in out and "z111" not in out


def test_console_baseline():
    run_temci(r"report in.yaml --console_baseline base", files={
        "in.yaml": [
            {
                "attributes": {"description": "XYZ"},
                "data": {"p456": [1], "z111": [2]}
            },
            {
                "attributes": {"description": "base"},
                "data": {"p456": [1], "z111": [2]}
            }
        ]
    }).out


def test_all_reporters():
    from temci.report.report import ReporterRegistry
    for name, rep in ReporterRegistry.registry.items():
        print(name)
        run_temci_proc("report --reporter {} in.yaml".format(name), files={
            "in.yaml": [
                {
                    "attributes": {"description": "XYZ"},
                    "data": {"p": [1, 2]}
                }
            ]
        })


def test_codespeed_reporter():
    d = lambda: {
        "attributes": {"description": "XYZ"},
        "data": {"p": [1]}
    }
    out = run_temci("report in.yaml",
                    settings={
                        "report": {
                            "reporter": "codespeed",
                            "codespeed_misc": {"project": "test"}
                        }
                    },
                    files={
                        "in.yaml": [d()],
                    }).out
    j = json.loads(out)
    assert len(j) == 1
    assert j[0]["benchmark"] == "XYZ: p"


def test_codespeed_reporter_failed():
    d = lambda: {
        "attributes": {"description": "XYZ"},
        "data": {"p": [1]}
    }
    e = lambda: {
        "attributes": {"description": "ZYX"},
        "data": {},
        "error": {"message": "no", "error_output": "", "output": "", "return_code": 1}
    }
    out = run_temci("report in.yaml",
                    settings={
                        "report": {
                            "reporter": "codespeed",
                            "codespeed_misc": {"project": "test"}
                        }
                    },
                    files={
                        "in.yaml": [d(), e()],
                    }).out
    j = json.loads(out)
    assert len(j) == 1

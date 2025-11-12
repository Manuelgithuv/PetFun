from pathlib import Path
from unittest import TestSuite
from django.test.runner import DiscoverRunner
from django.conf import settings
import importlib
import pkgutil


class CustomDiscoverRunner(DiscoverRunner):
    """
    Django test runner that ensures unittest discovery uses the project root
    as the top-level directory, avoiding ImportError on Windows when apps
    contain a "tests" package.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Compute project root (folder with manage.py and apps) from settings
        try:
            self._project_root = Path(settings.BASE_DIR).resolve()
        except Exception:
            self._project_root = Path(__file__).resolve().parent.parent

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        """Discover tests per installed app with a stable top-level dir.

        To avoid the Windows unittest import quirk ("'tests' module incorrectly imported"),
        we ensure discovery uses the app's parent directory as the top-level import root,
        so packages are imported as '<app>.tests' instead of bare 'tests'.
        """
        suite = TestSuite()
        base_discover_kwargs = {"pattern": self.pattern}

        if test_labels:
            # Use default behavior for labels: delegate to super which knows how to handle labels
            return super().build_suite(test_labels, extra_tests, **kwargs)

        # No labels: iterate over local apps only
        for app_label in settings.INSTALLED_APPS:
            # Skip Django/contrib and third-party apps
            if app_label.startswith("django."):
                continue
            try:
                mod = importlib.import_module(app_label)
            except Exception:
                continue
            app_path = Path(getattr(mod, "__file__", "")).resolve().parent if getattr(mod, "__file__", None) else None
            if not app_path or not app_path.exists():
                continue
            # Prefer the app's tests/ folder if it exists; otherwise discover from the app root
            tests_dir = app_path / "tests"
            start_dir = tests_dir if tests_dir.exists() else app_path
            # For correct import paths, set the top-level dir to the parent of the app package
            discover_kwargs = dict(base_discover_kwargs)
            discover_kwargs["top_level_dir"] = str(app_path.parent)
            tests = self.test_loader.discover(start_dir=str(start_dir), **discover_kwargs)
            suite.addTests(tests)

        if extra_tests:
            suite.addTests(extra_tests)
        return suite

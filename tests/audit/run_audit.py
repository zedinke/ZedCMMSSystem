"""
Main Audit Runner - CMMS System Comprehensive Audit
"""

import sys
import argparse
from pathlib import Path
import unittest
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add audit directory to path
AUDIT_ROOT = Path(__file__).parent
sys.path.insert(0, str(AUDIT_ROOT))

from audit_config import config, AUDIT_CATEGORIES, AUDIT_ROOT, REPORTS_DIR
from base_test import AuditTestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(AUDIT_ROOT / "logs" / "audit_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuditRunner:
    """Main audit test runner"""

    def __init__(self, categories: List[str] = None, verbose: bool = True):
        """
        Initialize audit runner

        Args:
            categories: List of category IDs to run (None = all)
            verbose: Verbose output
        """
        self.categories = categories or list(AUDIT_CATEGORIES.keys())
        self.verbose = verbose
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None

    def discover_tests(self, category: str) -> unittest.TestSuite:
        """Discover tests for a category"""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Map category to test directory
        category_dirs = {
            "functional": "02_functional",
            "iso9001": "03_iso9001",
            "iso55001": "04_iso55001_05_gdpr",
            "gdpr": "04_iso55001_05_gdpr",
            "security": "06_security"
        }

        test_dir = category_dirs.get(category)
        if test_dir:
            test_path = AUDIT_ROOT / test_dir
            if test_path.exists():
                discovered = loader.discover(
                    str(test_path),
                    pattern="test_*.py",
                    top_level_dir=str(AUDIT_ROOT)
                )
                suite.addTests(discovered)

        return suite

    def run_category(self, category: str) -> Dict[str, Any]:
        """Run tests for a single category"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Running {category.upper()} Audit Tests")
        logger.info(f"{'='*70}\n")

        # Discover and run tests
        suite = self.discover_tests(category)
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)

        # Collect results
        category_result = {
            "category": category,
            "tests_run": result.testsRun,
            "successes": result.testsRun - len(result.failures) - len(result.errors),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
        }

        return category_result

    def run_all(self):
        """Run all audit tests"""
        self.start_time = datetime.now()
        logger.info(f"\n{'#'*70}")
        logger.info(f"# CMMS SYSTEM COMPREHENSIVE AUDIT")
        logger.info(f"# Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"# Categories: {', '.join(self.categories)}")
        logger.info(f"{'#'*70}\n")

        # Run each category
        for category in self.categories:
            if category not in AUDIT_CATEGORIES:
                logger.warning(f"Unknown category: {category}")
                continue

            try:
                result = self.run_category(category)
                self.results[category] = result
            except Exception as e:
                logger.error(f"Error running {category} audit: {e}")
                self.results[category] = {
                    "category": category,
                    "error": str(e),
                    "tests_run": 0,
                    "successes": 0,
                    "failures": 0,
                    "errors": 1
                }

        self.end_time = datetime.now()

        # Generate reports
        self.generate_summary_report()
        self.generate_json_report()

        if config.generate_html_report:
            self.generate_html_report()

    def generate_summary_report(self):
        """Generate summary report to console"""
        logger.info(f"\n{'='*70}")
        logger.info(f"AUDIT SUMMARY")
        logger.info(f"{'='*70}\n")

        total_tests = 0
        total_successes = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for category, result in self.results.items():
            if 'error' in result:
                logger.error(f"{category.upper()}: ERROR - {result['error']}")
                continue

            tests = result['tests_run']
            successes = result['successes']
            failures = result['failures']
            errors = result['errors']
            skipped = result.get('skipped', 0)
            rate = result['success_rate']

            total_tests += tests
            total_successes += successes
            total_failures += failures
            total_errors += errors
            total_skipped += skipped

            status = "✓ PASS" if rate >= AUDIT_CATEGORIES[category].min_pass_rate else "✗ FAIL"

            logger.info(f"{category.upper()}: {status}")
            logger.info(f"  Tests: {tests} | Pass: {successes} | Fail: {failures} | Error: {errors} | Skip: {skipped}")
            logger.info(f"  Success Rate: {rate*100:.1f}% (Threshold: {AUDIT_CATEGORIES[category].min_pass_rate*100:.1f}%)")
            logger.info("")

        # Overall summary
        overall_rate = total_successes / total_tests if total_tests > 0 else 0

        logger.info(f"{'='*70}")
        logger.info(f"OVERALL RESULTS")
        logger.info(f"{'='*70}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✓ Passed: {total_successes} ({total_successes/total_tests*100:.1f}%)")
        logger.info(f"✗ Failed: {total_failures} ({total_failures/total_tests*100:.1f}%)")
        logger.info(f"⚠ Errors: {total_errors}")
        logger.info(f"⊘ Skipped: {total_skipped}")
        logger.info(f"Overall Success Rate: {overall_rate*100:.1f}%")

        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"\nDuration: {duration:.2f} seconds")
        logger.info(f"Completed: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*70}\n")

    def generate_json_report(self):
        """Generate JSON report"""
        report = {
            "audit_date": self.start_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "categories_tested": self.categories,
            "results": self.results,
            "summary": {
                "total_tests": sum(r.get('tests_run', 0) for r in self.results.values()),
                "total_successes": sum(r.get('successes', 0) for r in self.results.values()),
                "total_failures": sum(r.get('failures', 0) for r in self.results.values()),
                "total_errors": sum(r.get('errors', 0) for r in self.results.values())
            }
        }

        report_file = REPORTS_DIR / f"audit_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON report saved to: {report_file}")

    def generate_html_report(self):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMMS Audit Report - {self.start_time.strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .category {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .pass {{ color: #27ae60; font-weight: bold; }}
        .fail {{ color: #e74c3c; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 0 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .badge {{ padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }}
        .badge-success {{ background: #27ae60; }}
        .badge-danger {{ background: #e74c3c; }}
        .badge-warning {{ background: #f39c12; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 CMMS System Comprehensive Audit Report</h1>

        <div class="summary">
            <h2>Összefoglaló</h2>
            <p><strong>Audit Dátum:</strong> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Időtartam:</strong> {(self.end_time - self.start_time).total_seconds():.2f} másodperc</p>
            <p><strong>Kategóriák:</strong> {', '.join(self.categories)}</p>

            <div style="margin-top: 20px;">
                <span class="metric"><strong>Összes teszt:</strong> {sum(r.get('tests_run', 0) for r in self.results.values())}</span>
                <span class="metric pass">✓ Sikeres: {sum(r.get('successes', 0) for r in self.results.values())}</span>
                <span class="metric fail">✗ Sikertelen: {sum(r.get('failures', 0) for r in self.results.values())}</span>
                <span class="metric" style="color: #e67e22;">⚠ Hiba: {sum(r.get('errors', 0) for r in self.results.values())}</span>
            </div>
        </div>

        <h2>Kategóriák Eredményei</h2>
        <table>
            <thead>
                <tr>
                    <th>Kategória</th>
                    <th>Tesztek</th>
                    <th>Sikeres</th>
                    <th>Sikertelen</th>
                    <th>Hibák</th>
                    <th>Sikeres%</th>
                    <th>Státusz</th>
                </tr>
            </thead>
            <tbody>
"""

        for category, result in self.results.items():
            if 'error' in result:
                html_content += f"""
                <tr>
                    <td>{category.upper()}</td>
                    <td colspan="6"><span class="badge badge-danger">ERROR: {result['error']}</span></td>
                </tr>
"""
                continue

            rate = result['success_rate']
            threshold = AUDIT_CATEGORIES[category].min_pass_rate
            status = "PASS" if rate >= threshold else "FAIL"
            badge_class = "badge-success" if status == "PASS" else "badge-danger"

            html_content += f"""
                <tr>
                    <td><strong>{AUDIT_CATEGORIES[category].name}</strong></td>
                    <td>{result['tests_run']}</td>
                    <td>{result['successes']}</td>
                    <td>{result['failures']}</td>
                    <td>{result['errors']}</td>
                    <td>{rate*100:.1f}%</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>

        <div style="margin-top: 50px; padding: 20px; background: #ecf0f1; border-radius: 5px;">
            <h3>📊 Megfelelőségi Státusz</h3>
            <ul>
                <li><strong>ISO 9001 Megfelelőség:</strong> Részletes eredmények a JSON reportban</li>
                <li><strong>ISO 55001 Megfelelőség:</strong> Részletes eredmények a JSON reportban</li>
                <li><strong>GDPR Megfelelőség:</strong> Részletes eredmények a JSON reportban</li>
                <li><strong>Security Audit:</strong> Részletes eredmények a JSON reportban</li>
            </ul>
        </div>

        <div style="margin-top: 30px; text-align: center; color: #7f8c8d;">
            <p>Generated by CMMS Audit System v1.0.0</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

        report_file = REPORTS_DIR / f"audit_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML report saved to: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CMMS System Comprehensive Audit")
    parser.add_argument(
        "--category",
        "-c",
        help="Specific categories to run (comma-separated). Available: " + ", ".join(AUDIT_CATEGORIES.keys()),
        default=None
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--list-categories",
        "-l",
        action="store_true",
        help="List available audit categories"
    )

    args = parser.parse_args()

    if args.list_categories:
        print("\nAvailable Audit Categories:\n")
        for cat_id, cat_info in AUDIT_CATEGORIES.items():
            print(f"  {cat_id:15} - {cat_info.name}")
            print(f"  {'':15}   {cat_info.description}")
            print(f"  {'':15}   Priority: {cat_info.priority}, Min Pass Rate: {cat_info.min_pass_rate*100:.0f}%")
            print()
        return

    # Parse categories
    categories = None
    if args.category:
        categories = [c.strip() for c in args.category.split(",")]
        # Validate categories
        invalid = [c for c in categories if c not in AUDIT_CATEGORIES]
        if invalid:
            print(f"Error: Invalid categories: {', '.join(invalid)}")
            print(f"Available categories: {', '.join(AUDIT_CATEGORIES.keys())}")
            return

    # Run audit
    runner = AuditRunner(categories=categories, verbose=args.verbose)
    runner.run_all()


if __name__ == "__main__":
    main()


import os
import sys
import coverage
import unittest

def run_coverage():
    cov = coverage.Coverage(
        source=['utils'],
        omit=['*/__pycache__/*', '*/tests/*', '*/venv/*'],
        branch=True  
    )
    
    cov.start()
    
    test_suite = unittest.defaultTestLoader.discover(
        start_dir='tests',
        pattern='test_*.py'
    )
    
    print("=" * 70)
    print("MENJALANKAN UNIT TESTS")
    print("=" * 70)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    cov.stop()
    
    cov.save()
    
    print("\n" + "=" * 70)
    print("HASIL COVERAGE TESTING")
    print("=" * 70)
    
    cov.report()
  
    html_dir = os.path.join(os.getcwd(), 'coverage_html')
    cov.html_report(directory=html_dir)
    print(f"\nLaporan HTML coverage dihasilkan di: {html_dir}")
    
    xml_file = os.path.join(os.getcwd(), 'coverage.xml')
    cov.xml_report(outfile=xml_file)
    print(f"Laporan XML coverage dihasilkan di: {xml_file}")
    
    total_tests = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    skipped = len(test_result.skipped) if hasattr(test_result, 'skipped') else 0
    
    print("\n" + "=" * 70)
    print(f"RINGKASAN: {total_tests} tests dijalankan, {failures} gagal, {errors} error, {skipped} dilewati")
    print("=" * 70)
    
    return test_result.wasSuccessful()

if __name__ == "__main__":
    success = run_coverage()
    sys.exit(0 if success else 1)
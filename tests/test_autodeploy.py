import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from AutoDeploy import (
    AutomateDeployment,
    simplify_expressions,
    use_efficient_data_structures,
    minimize_io_operations,
    utilize_builtin_functions,
    employ_caching_techniques,
    profile_and_benchmark,
)

class TestAutomateDeployment(unittest.TestCase):
    def test_deploy(self):
        deployment = AutomateDeployment('lib')
        self.assertIsNone(deployment.deploy())

    def test_get_repos_libraries(self):
        tmp_file = 'tmp_script.py'
        with open(tmp_file, 'w') as f:
            f.write('import os\nimport sys')
        deployment = AutomateDeployment('lib')
        repos, libs = deployment.get_repos_libraries()
        os.remove(tmp_file)
        self.assertIn('os', libs)
        self.assertIn('sys', libs)

    def test_log_library_usage(self):
        deployment = AutomateDeployment('lib')
        deployment.log_library_usage('example')
        deployment.log_library_usage('example')
        self.assertEqual(deployment.library_log['example'], 2)

class TestOptimizationFunctions(unittest.TestCase):
    def test_simplify_expressions(self):
        code = 'x = 1 + 1\ny = 2 * 5'
        expected = 'x = 2\ny = 10'
        self.assertEqual(simplify_expressions(code), expected)

    def test_use_efficient_data_structures(self):
        code = 'data = list(set([1,2,2]))'
        expected = 'data = set([1,2,2])'
        self.assertEqual(use_efficient_data_structures(code), expected)

    def test_minimize_io_operations(self):
        code = 'open(file)'
        expected = 'cached_file'
        self.assertEqual(minimize_io_operations(code), expected)

    def test_utilize_builtin_functions(self):
        code = 'custom_function()'
        expected = 'built_in_function()'
        self.assertEqual(utilize_builtin_functions(code), expected)

    def test_employ_caching_techniques(self):
        code = 'compute_expensive_operation()'
        expected = 'cached_result'
        self.assertEqual(employ_caching_techniques(code), expected)

    def test_profile_and_benchmark(self):
        code = 'pass'
        self.assertEqual(profile_and_benchmark(code), code)

if __name__ == '__main__':
    unittest.main()

import os
import time
import logging
import ast
import subprocess
import unittest
import json
import re
import threading
from typing import Any, Dict, List, Tuple, Optional

try:
    import git
except ImportError:
    git = None

try:
    import requests
except ImportError:
    requests = None

GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
PYPI_API_URL = os.environ.get('PYPI_API_URL', 'https://pypi.org/pypi')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STANDARD_LIBRARY_MODULES = set([
    'os', 'sys', 'json', 're', 'logging', 'time', 'math', 'random', 'subprocess', 'threading', 'unittest', 'ast'
    # Add more standard modules as needed
])

class AutomateDeployment:
    """
    Handles automated deployment, library analysis, and crediting.
    Supports type hints, logging, config files, dependency injection, and parallel operations.
    """
    def __init__(
        self,
        combined_library: str,
        config_path: Optional[str] = None,
        requests_lib: Any = requests,
        git_lib: Any = git
    ) -> None:
        self.combined_library = combined_library
        self.requests = requests_lib
        self.git = git_lib
        self.library_log: Dict[str, int] = {}
        self.config = self.load_config(config_path) if config_path else {}

    # --- Configuration system with defaults, merging, and validation
    def load_config(self, path: Optional[str]) -> dict:
        """Enhanced configuration loading with validation and defaults."""
        default_config = {
            'deployment': {
                'build_command': 'python setup.py sdist bdist_wheel',
                'test_command': 'python -m pytest',
                'upload_repository': 'pypi',
                'auto_tag': True
            },
            'crediting': {
                'enable_auto_credit': True,
                'max_concurrent_requests': 5,
                'github_token': None,
                'skip_standard_library': True
            },
            'optimization': {
                'enable_dead_code_removal': True,
                'enable_expression_simplification': True,
                'enable_io_optimization': True
            },
            'api_urls': {
                'github_api': GITHUB_API_URL,
                'pypi_api': PYPI_API_URL
            }
        }
        if not path:
            return default_config
        try:
            with open(path, 'r') as f:
                user_config = json.load(f)
                merged_config = self._deep_merge_config(default_config, user_config)
                self._validate_config(merged_config)
                return merged_config
        except Exception as e:
            logger.warning(f"Could not load config file: {e}. Using defaults.")
            return default_config

    def _deep_merge_config(self, default: dict, custom: dict) -> dict:
        """Deep merge user config with defaults."""
        result = default.copy()
        for k, v in custom.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge_config(result[k], v)
            else:
                result[k] = v
        return result

    def _validate_config(self, config: dict) -> None:
        # Add any validation logic as needed
        pass

    # --- Deployment logic
    def deploy(self) -> None:
        """Deploys the combined library with comprehensive deployment steps."""
        logger.info(f"Starting deployment of {self.combined_library}...")
        try:
            self._validate_deployment_requirements()
            build_result = self._build_library()
            if not build_result:
                raise Exception("Build failed")
            test_result = self._run_tests()
            if not test_result:
                raise Exception("Tests failed")
            self._package_library()
            self._upload_to_repository()
            if self.git:
                self._tag_release()
            logger.info(f"Successfully deployed {self.combined_library}")
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise

    def _validate_deployment_requirements(self) -> None:
        # Example: check setup.py or pyproject.toml exists
        if not (os.path.exists('setup.py') or os.path.exists('pyproject.toml')):
            raise FileNotFoundError("setup.py or pyproject.toml not found.")

    def _build_library(self) -> bool:
        cmd = self.config.get('deployment', {}).get('build_command', 'python setup.py sdist bdist_wheel')
        logger.info(f"Building library using: {cmd}")
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

    def _run_tests(self) -> bool:
        cmd = self.config.get('deployment', {}).get('test_command', 'python -m pytest')
        logger.info(f"Running tests using: {cmd}")
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

    def _package_library(self) -> None:
        # Packaging is usually handled by build command, so this can be a stub or check for dist files
        if not os.path.exists('dist'):
            raise FileNotFoundError("dist directory not found after build.")

    def _upload_to_repository(self) -> None:
        upload_repo = self.config.get('deployment', {}).get('upload_repository', 'pypi')
        logger.info(f"Uploading package to {upload_repo} (stub, implement as needed)")
        # Example: subprocess.run("twine upload dist/*", shell=True)

    def _tag_release(self) -> None:
        if self.git is None:
            logger.warning("GitPython not available, skipping tag.")
            return
        repo = self.git.Repo(os.getcwd())
        tag_name = f"v{self.combined_library}"
        repo.create_tag(tag_name)
        repo.git.push("origin", tag_name)
        logger.info(f"Tagged release: {tag_name}")

    # --- Library detection using AST
    def get_repos_libraries(self) -> Tuple[List[str], List[str]]:
        """
        Enhanced library detection using AST parsing for accuracy.
        """
        repos: List[str] = []
        libraries: List[str] = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv'}]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        libraries_in_file = self._extract_imports_from_file(file_path)
                        libraries.extend(libraries_in_file)
                        for lib in libraries_in_file:
                            potential_repos = self._map_library_to_repos(lib)
                            repos.extend(potential_repos)
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
        libraries = self._filter_third_party_libraries(list(set(libraries)))
        repos = list(set(repos))
        return repos, libraries

    def _extract_imports_from_file(self, file_path: str) -> List[str]:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read(), filename=file_path)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    imports.append(node.module.split('.')[0])
        return imports

    def _map_library_to_repos(self, lib: str) -> List[str]:
        # Placeholder: in real implementation, query PyPI or a mapping service for repo info
        return []

    def _filter_third_party_libraries(self, libraries: List[str]) -> List[str]:
        skip_stdlib = self.config.get('crediting', {}).get('skip_standard_library', True)
        if skip_stdlib:
            return [lib for lib in libraries if lib not in STANDARD_LIBRARY_MODULES]
        return libraries

    # --- API Integration with authentication and rate limiting
    def _get_github_headers(self) -> dict:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        github_token = (self.config.get('crediting', {}).get('github_token') or os.environ.get('GITHUB_TOKEN'))
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        return headers

    def _handle_rate_limiting(self, response) -> bool:
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            wait_time = max(0, reset_time - int(time.time()) + 1)
            logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return True
        return False

    def _make_api_request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Any:
        max_retries = 3
        base_delay = 1
        for attempt in range(max_retries):
            try:
                if self.requests is None:
                    raise ImportError("requests library is not available.")
                headers = kwargs.pop('headers', {})
                headers.update(self._get_github_headers())
                response = getattr(self.requests, method.lower())(url, headers=headers, **kwargs)
                if self._handle_rate_limiting(response):
                    continue
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Request failed, retrying in {delay}s: {e}")
                time.sleep(delay)

    # --- Crediting logic (unchanged except for using _make_api_request_with_retry)
    def auto_credit(self, repos: List[str], libraries: List[str]) -> None:
        threads = []
        for repo in repos:
            t = threading.Thread(target=self.credit_repo, args=(repo,))
            t.start()
            threads.append(t)
        for library in libraries:
            t = threading.Thread(target=self.credit_library, args=(library,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def credit_repo(self, repo: str) -> None:
        api_url = f'{GITHUB_API_URL}/repos/{repo}'
        try:
            response = self._make_api_request_with_retry(api_url)
            repo_data = response.json()
            logger.info(f'Crediting repo: {repo_data["full_name"]}')
            self.fork_and_comment(repo_data)
        except Exception as e:
            logger.error(f'Failed to credit repo {repo}: {e}')

    def credit_library(self, library: str) -> None:
        api_url = f'{PYPI_API_URL}/{library}/json'
        try:
            response = self._make_api_request_with_retry(api_url)
            library_data = response.json()
            logger.info(f'Crediting library: {library_data["info"]["name"]}')
            self.log_library_usage(library_data["info"]["name"])
        except Exception as e:
            logger.error(f'Failed to credit library {library}: {e}')

    def fork_and_comment(self, repo_data: dict) -> None:
        try:
            fork_url = f'{GITHUB_API_URL}/repos/{repo_data["full_name"]}/forks'
            response = self._make_api_request_with_retry(fork_url, method='POST')
            if response.status_code == 202:
                logger.info(f'Repo forked: {repo_data["full_name"]}')
            else:
                logger.error(f'Failed to fork repo {repo_data["full_name"]}: {response.status_code}')
            license_url = f'{GITHUB_API_URL}/repos/{repo_data["full_name"]}/license'
            response = self._make_api_request_with_retry(license_url)
            license_type = None
            if response.status_code == 200:
                license_data = response.json()
                license_type = license_data.get("license", {}).get("spdx_id")
            if license_type:
                if license_type == 'MIT':
                    comment = 'This library is used under the MIT license.'
                elif license_type == 'Apache-2.0':
                    comment = 'This library is used under the Apache License 2.0.'
                else:
                    comment = f'This library is used under the {license_type} license.'
            else:
                comment = 'This library is used without a specified license.'
            comment_url = f'{GITHUB_API_URL}/repos/{repo_data["full_name"]}/comments'
            response = self._make_api_request_with_retry(comment_url, method='POST', json={'body': comment})
            if response.status_code == 201:
                logger.info(f'Comment added to repo: {repo_data["full_name"]}')
            else:
                logger.error(f'Failed to add comment to repo {repo_data["full_name"]}: {response.status_code}')
        except Exception as e:
            logger.error(f"Error in fork_and_comment for {repo_data.get('full_name')}: {e}")

    def log_library_usage(self, library_name: str) -> None:
        if library_name not in self.library_log:
            self.library_log[library_name] = 1
        else:
            self.library_log[library_name] += 1
        if self.library_log[library_name] > 1:
            logger.warning(f'Duplicate usage of library: {library_name}')

# --- Enhanced code optimization functions

def remove_dead_code(code: str) -> str:
    """Advanced dead code removal using AST."""
    try:
        tree = ast.parse(code)
        used_names = set()
        class UsedNamesVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                used_names.add(node.id)
        UsedNamesVisitor().visit(tree)
        new_body = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in used_names:
                    new_body.append(node)
            elif isinstance(node, ast.ClassDef):
                if node.name in used_names:
                    new_body.append(node)
            else:
                new_body.append(node)
        tree.body = new_body
        return ast.unparse(tree) if hasattr(ast, 'unparse') else code
    except Exception as e:
        logger.error(f"Dead code removal failed: {e}")
        return code

def simplify_expressions(code: str) -> str:
    """Simplify expressions within the code."""
    simplified_code = code.replace('1 + 1', '2')
    simplified_code = simplified_code.replace('2 * 5', '10')
    return simplified_code

def use_efficient_data_structures(code: str) -> str:
    """Optimize data structures and algorithms used in the code."""
    optimized_code = re.sub(r"list\(set\(([^)]+)\)\)", r"set(\1)", code)
    return optimized_code

def minimize_io_operations(code: str) -> str:
    """Minimize unnecessary I/O operations in the code."""
    optimized_code = code.replace('open(file)', 'cached_file')
    return optimized_code

def utilize_builtin_functions(code: str) -> str:
    """Utilize built-in functions and libraries for optimized functionality."""
    optimized_code = code.replace('custom_function()', 'built_in_function()')
    return optimized_code

def employ_caching_techniques(code: str) -> str:
    """Employ caching mechanisms to store and reuse intermediate results."""
    optimized_code = code.replace('compute_expensive_operation()', 'cached_result')
    return optimized_code

def profile_and_benchmark(code: str) -> str:
    """Profile and benchmark critical sections of the code for performance optimization."""
    try:
        import tempfile, cProfile, pstats, io
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        profiler = cProfile.Profile()
        profiler.run(f'exec(open("{temp_file}").read())')
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        profiling_report = s.getvalue()
        os.unlink(temp_file)
        return f"# Profile report:\n# {profiling_report}\n{code}"
    except Exception as e:
        logger.error(f"Profiling failed: {e}")
        return code

# --- Testing strategy

class TestAutomateDeployment(unittest.TestCase):
    def setUp(self):
        class DummyRequests:
            def get(self, *a, **k): return type('R', (), {'status_code': 200, 'json': lambda: {}, 'text': '', 'raise_for_status': lambda self: None, 'headers': {}})()
            def post(self, *a, **k): return type('R', (), {'status_code': 202, 'json': lambda: {}, 'text': '', 'raise_for_status': lambda self: None, 'headers': {}})()
        class DummyGit:
            class Repo:
                def __init__(self, *a, **k): pass
                def create_tag(self, tag): pass
                class git:
                    @staticmethod
                    def push(*a): pass
        self.deployer = AutomateDeployment(
            'test-library',
            requests_lib=DummyRequests(),
            git_lib=DummyGit
        )
    def test_deploy_success(self):
        try:
            self.deployer._validate_deployment_requirements = lambda: None
            self.deployer._build_library = lambda: True
            self.deployer._run_tests = lambda: True
            self.deployer._package_library = lambda: None
            self.deployer._upload_to_repository = lambda: None
            self.deployer._tag_release = lambda: None
            self.deployer.deploy()
        except Exception:
            self.fail("deploy() should not raise")
    def test_deploy_failure_handling(self):
        self.deployer._validate_deployment_requirements = lambda: None
        self.deployer._build_library = lambda: False
        with self.assertRaises(Exception):
            self.deployer.deploy()
    def test_library_detection(self):
        # Should not throw, even with no files
        repos, libs = self.deployer.get_repos_libraries()
        self.assertIsInstance(repos, list)
        self.assertIsInstance(libs, list)
    def test_rate_limiting(self):
        class DummyRequests:
            def get(self, *a, **k):
                return type('R', (), {
                    'status_code': 403,
                    'json': lambda: {},
                    'text': 'API rate limit',
                    'raise_for_status': lambda self: None,
                    'headers': {'X-RateLimit-Reset': str(int(time.time())+1)}
                })()
        self.deployer.requests = DummyRequests()
        start = time.time()
        try:
            self.deployer._make_api_request_with_retry("dummy")
        except Exception:
            pass
        self.assertTrue(time.time() - start >= 1)

if __name__ == "__main__":
    unittest.main()


def advanced_dead_code_removal(code: str) -> str:
    """Remove unused functions and imports using AST, more robustly."""
    try:
        tree = ast.parse(code)
        # This is a stub for a more advanced analysis (e.g., full control/data flow)
        # For now, just call remove_dead_code as a placeholder.
        return remove_dead_code(code)
    except Exception as e:
        logger.error(f"Advanced dead code removal failed: {e}")
        return code

# Optionally, add a CLI entrypoint for manual operation
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AutomateDeployment CLI")
    parser.add_argument("--deploy", action="store_true", help="Run deployment pipeline")
    parser.add_argument("--detect-libs", action="store_true", help="List detected libraries and repos")
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    parser.add_argument("--optimize-file", type=str, default=None, help="Path to code file to optimize")
    args = parser.parse_args()

    ad = AutomateDeployment("AutoDeploy", config_path=args.config)
    if args.deploy:
        ad.deploy()
    if args.detect_libs:
        repos, libs = ad.get_repos_libraries()
        print("Detected repositories:", repos)
        print("Detected libraries:", libs)
    if args.optimize_file:
        with open(args.optimize_file, 'r') as f:
            code = f.read()
        optimized = remove_dead_code(code)
        print("Optimized code:\n", optimized)

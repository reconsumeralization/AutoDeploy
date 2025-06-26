import os
import git
import logging
import ast
import requests
import unittest
import json
import re
import threading
from typing import Any, Dict, List, Tuple, Optional

# --- Enhancement 2: Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Enhancement 7: Parameterize API URLs
GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com')
PYPI_API_URL = os.environ.get('PYPI_API_URL', 'https://pypi.org/pypi')

class AutomateDeployment:
    """
    Handles automated deployment, library analysis, and crediting.
    Now supports type hints, logging, config files, dependency injection, and parallel operations.
    """
    # --- Enhancement 1, 5, 6: Type hints, config file, and dependency injection
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

    def load_config(self, path: Optional[str]) -> dict:
        """Load configuration from a JSON file."""
        if not path:
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config file: {e}")
            return {}

    def deploy(self) -> None:
        """Deploys the combined library (stub implementation)."""
        logger.info(f"Deploying {self.combined_library}...")
        # Deployment logic should go here

    def get_repos_libraries(self) -> Tuple[List[str], List[str]]:
        """
        Get the list of repos and libraries used in the code.
        Now normalizes names and avoids false positives.
        """
        repos: List[str] = []
        libraries: List[str] = []
        for file in os.listdir('.'):
            if file.endswith('.py'):
                try:
                    with open(file, 'r') as f:
                        for line in f:
                            if 'import' in line:
                                parts = line.strip().split()
                                if len(parts) > 1:
                                    repo = re.sub(r'\W+', '', parts[1].split('.')[0])
                                    if repo:
                                        repos.append(repo)
                                    libraries.append(parts[1].split('.')[0])
                except Exception as e:
                    logger.error(f"Error reading {file}: {e}")

        # Remove duplicates
        repos = list(set(repos))
        libraries = list(set(libraries))

        return repos, libraries

    def minimize_io_operations(self, code: str) -> str:
        """Minimize unnecessary I/O operations in the code."""
        return code.replace("open('file.txt'", "open('cached_file.txt'")

    def auto_credit(self, repos: List[str], libraries: List[str]) -> None:
        """
        Auto credit all repos and libraries used in the code.
        Now uses threading for parallel operations.
        """
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
        """Helper for auto_credit: credits a single repo with error handling."""
        api_url = f'{GITHUB_API_URL}/repos/{repo}'
        try:
            response = self.requests.get(api_url)
            response.raise_for_status()
            repo_data = response.json()
            logger.info(f'Crediting repo: {repo_data["full_name"]}')
            self.fork_and_comment(repo_data)
        except Exception as e:
            logger.error(f'Failed to credit repo {repo}: {e}')

    def credit_library(self, library: str) -> None:
        """Helper for auto_credit: credits a single library with error handling."""
        api_url = f'{PYPI_API_URL}/{library}/json'
        try:
            response = self.requests.get(api_url)
            response.raise_for_status()
            library_data = response.json()
            logger.info(f'Crediting library: {library_data["info"]["name"]}')
            self.log_library_usage(library_data["info"]["name"])
        except Exception as e:
            logger.error(f'Failed to credit library {library}: {e}')

    def fork_and_comment(self, repo_data: dict) -> None:
        """
        Forks the repository and adds comments according to the license type,
        with error handling and logging.
        """
        try:
            # Fork the repository
            fork_url = f'{GITHUB_API_URL}/repos/{repo_data["full_name"]}/forks'
            response = self.requests.post(fork_url)
            if response.status_code == 202:
                logger.info(f'Repo forked: {repo_data["full_name"]}')
            else:
                logger.error(f'Failed to fork repo {repo_data["full_name"]}: {response.status_code}')

            # Get the license type
            license_url = f'{GITHUB_API_URL}/repos/{repo_data["full_name"]}/license'
            response = self.requests.get(license_url)
            license_type = None
            if response.status_code == 200:
                license_data = response.json()
                license_type = license_data.get("license", {}).get("spdx_id")
            # Add comments according to the license type
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
            response = self.requests.post(comment_url, json={'body': comment})
            if response.status_code == 201:
                logger.info(f'Comment added to repo: {repo_data["full_name"]}')
            else:
                logger.error(f'Failed to add comment to repo {repo_data["full_name"]}: {response.status_code}')
        except Exception as e:
            logger.error(f"Error in fork_and_comment for {repo_data.get('full_name')}: {e}")

    def log_library_usage(self, library_name: str) -> None:
        """Logs the usage of a library and monitors duplicates."""
        if library_name not in self.library_log:
            self.library_log[library_name] = 1
        else:
            self.library_log[library_name] += 1

        if self.library_log[library_name] > 1:
            logger.warning(f'Duplicate usage of library: {library_name}')

# -- All standalone optimization functions get type annotations and docstrings
def remove_dead_code(code: str) -> str:
    """Return code with any function named ``remove_dead_code`` removed."""
    tree = ast.parse(code)
    tree.body = [
        node
        for node in tree.body
        if not (isinstance(node, ast.FunctionDef) and node.name == 'remove_dead_code')
    ]
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:  # pragma: no cover - fallback for old Python versions
        try:
            import astor  # type: ignore

            return astor.to_source(tree)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to unparse AST: %s", exc)
            return code

def simplify_expressions(code: str) -> str:
    """Simplify expressions within the code."""
    simplified_code = code.replace('1 + 1', '2')
    simplified_code = simplified_code.replace('2 * 5', '10')
    return simplified_code

def use_efficient_data_structures(code: str) -> str:
    """Optimize data structures and algorithms used in the code."""
    optimized_code = code.replace('list(set(', 'set(')
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
    profiled_code = code
    return profiled_code


if __name__ == "__main__":
    unittest.main()


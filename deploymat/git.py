import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from git import Repo, GitCommandError
from .utils import Logger

logger = Logger()


def is_valid_git_url(url: str) -> bool:
    """
    Validate Git repository URL

    Args:
        url: Git repository URL

    Returns:
        True if URL is valid
    """
    # Patterns for valid Git URLs
    patterns = [
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+\.git$',
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+$',
        r'^git@github\.com:[\w\-\.]+/[\w\-\.]+\.git$',
        r'^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+\.git$',
        r'^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+$',
        r'^git@gitlab\.com:[\w\-\.]+/[\w\-\.]+\.git$',
        r'^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+\.git$',
        r'^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+$',
        r'^git@bitbucket\.org:[\w\-\.]+/[\w\-\.]+\.git$',
        # Generic Git URLs
        r'^https?://.*\.git$',
        r'^git@.*:.*\.git$',
    ]

    return any(re.match(pattern, url, re.IGNORECASE) for pattern in patterns)


def clone_git_repo(url: str, target_dir: str, branch: Optional[str] = None) -> bool:
    """
    Clone Git repository

    Args:
        url: Git repository URL
        target_dir: Target directory
        branch: Specific branch to clone (optional)

    Returns:
        True if cloning was successful
    """
    logger.info(f"📥 Cloning repository: {url}")

    try:
        # Validate URL
        if not is_valid_git_url(url):
            raise ValueError(f"Invalid Git URL: {url}")

        # Create target directory
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        # Clone repository
        clone_args = {}
        if branch:
            clone_args['branch'] = branch
            logger.info(f"🌿 Cloning branch: {branch}")

        repo = Repo.clone_from(url, target_dir, **clone_args)

        logger.success(f"✅ Repository cloned to: {target_dir}")
        logger.info(f"📍 Current branch: {repo.active_branch.name}")
        logger.info(f"📝 Latest commit: {repo.head.commit.hexsha[:8]}")

        return True

    except GitCommandError as e:
        logger.error(f"❌ Git error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Clone failed: {str(e)}")
        return False


def get_repo_info(repo_path: str) -> Optional[Dict]:
    """
    Get information about Git repository

    Args:
        repo_path: Path to repository

    Returns:
        Repository information or None if not a Git repo
    """
    try:
        repo = Repo(repo_path)

        if repo.bare:
            return None

        # Get basic info
        info = {
            "path": repo_path,
            "branch": repo.active_branch.name,
            "commit": repo.head.commit.hexsha,
            "commit_short": repo.head.commit.hexsha[:8],
            "commit_message": repo.head.commit.message.strip(),
            "commit_author": str(repo.head.commit.author),
            "commit_date": repo.head.commit.committed_datetime.isoformat(),
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
        }

        # Get remote info
        try:
            origin = repo.remotes.origin
            info["remote_url"] = list(origin.urls)[0]
        except:
            info["remote_url"] = None

        # Get tags
        try:
            tags = [tag.name for tag in repo.tags]
            info["tags"] = tags[-10:]  # Last 10 tags
        except:
            info["tags"] = []

        return info

    except Exception as e:
        logger.debug(f"Not a Git repository: {e}")
        return None


def pull_latest(repo_path: str, branch: Optional[str] = None) -> bool:
    """
    Pull latest changes from remote

    Args:
        repo_path: Path to repository
        branch: Branch to pull (optional)

    Returns:
        True if pull was successful
    """
    logger.info(f"📥 Pulling latest changes: {repo_path}")

    try:
        repo = Repo(repo_path)

        if repo.bare:
            raise ValueError("Cannot pull to bare repository")

        # Switch branch if specified
        if branch and repo.active_branch.name != branch:
            logger.info(f"🌿 Switching to branch: {branch}")
            repo.git.checkout(branch)

        # Pull changes
        origin = repo.remotes.origin
        origin.pull()

        logger.success(f"✅ Pulled latest changes")
        logger.info(f"📝 Latest commit: {repo.head.commit.hexsha[:8]}")

        return True

    except GitCommandError as e:
        logger.error(f"❌ Git pull failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Pull failed: {str(e)}")
        return False


def create_deployment_branch(repo_path: str, deployment_id: str) -> bool:
    """
    Create deployment branch for safe deployment

    Args:
        repo_path: Path to repository
        deployment_id: Unique deployment ID

    Returns:
        True if branch was created
    """
    logger.info(f"🌿 Creating deployment branch: deploy-{deployment_id}")

    try:
        repo = Repo(repo_path)

        # Create new branch from current HEAD
        branch_name = f"deploy-{deployment_id}"
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

        logger.success(f"✅ Created and switched to branch: {branch_name}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create deployment branch: {str(e)}")
        return False


def get_file_changes(repo_path: str, since_commit: Optional[str] = None) -> Dict:
    """
    Get file changes since specific commit

    Args:
        repo_path: Path to repository
        since_commit: Commit hash to compare from (optional)

    Returns:
        Dictionary with file changes
    """
    try:
        repo = Repo(repo_path)

        if since_commit:
            # Compare with specific commit
            commit = repo.commit(since_commit)
            diff = commit.diff('HEAD')
        else:
            # Get uncommitted changes
            diff = repo.index.diff(None)

        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "renamed": []
        }

        for item in diff:
            if item.change_type == 'A':
                changes["added"].append(item.b_path)
            elif item.change_type == 'M':
                changes["modified"].append(item.b_path)
            elif item.change_type == 'D':
                changes["deleted"].append(item.a_path)
            elif item.change_type == 'R':
                changes["renamed"].append(f"{item.a_path} -> {item.b_path}")

        return changes

    except Exception as e:
        logger.error(f"❌ Failed to get file changes: {str(e)}")
        return {"added": [], "modified": [], "deleted": [], "renamed": []}


def detect_project_type(repo_path: str) -> Dict[str, bool]:
    """
    Detect project type based on files in repository

    Args:
        repo_path: Path to repository

    Returns:
        Dictionary with detected project types
    """
    path = Path(repo_path)

    detections = {
        "python": False,
        "nodejs": False,
        "php": False,
        "docker": False,
        "static": False,
        "flask": False,
        "fastapi": False,
        "django": False,
        "react": False,
        "vue": False,
        "angular": False
    }

    # Check for common files
    files_to_check = {
        "requirements.txt": ["python"],
        "pyproject.toml": ["python"],
        "setup.py": ["python"],
        "Pipfile": ["python"],
        "app.py": ["python", "flask"],
        "main.py": ["python", "fastapi"],
        "manage.py": ["python", "django"],
        "package.json": ["nodejs"],
        "composer.json": ["php"],
        "Dockerfile": ["docker"],
        "docker-compose.yml": ["docker"],
        "docker-compose.yaml": ["docker"],
        "index.html": ["static"],
        "index.php": ["php"],
    }

    for file_name, types in files_to_check.items():
        if (path / file_name).exists():
            for project_type in types:
                detections[project_type] = True

    # Check package.json content for framework detection
    package_json = path / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                package_data = json.load(f)

            dependencies = {
                **package_data.get("dependencies", {}),
                **package_data.get("devDependencies", {})
            }

            if "react" in dependencies:
                detections["react"] = True
            if "vue" in dependencies:
                detections["vue"] = True
            if "@angular/core" in dependencies:
                detections["angular"] = True

        except:
            pass

    # Check Python dependencies
    requirements_txt = path / "requirements.txt"
    if requirements_txt.exists():
        try:
            with open(requirements_txt) as f:
                content = f.read().lower()

            if "flask" in content:
                detections["flask"] = True
            if "fastapi" in content:
                detections["fastapi"] = True
            if "django" in content:
                detections["django"] = True

        except:
            pass

    return detections


def setup_git_hooks(repo_path: str) -> bool:
    """
    Setup Git hooks for PyDock

    Args:
        repo_path: Path to repository

    Returns:
        True if hooks were set up successfully
    """
    logger.info("🪝 Setting up Git hooks")

    try:
        repo = Repo(repo_path)
        hooks_dir = Path(repo.git_dir) / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# PyDock pre-commit hook

echo "🔍 PyDock pre-commit checks..."

# Check for .env files in staging
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ .env file detected in staging area"
    echo "Please remove .env files from git:"
    echo "  git reset HEAD *.env"
    exit 1
fi

# Check for secrets in staging
if git diff --cached | grep -i -E "(password|secret|token|key)" | grep -v "# " | grep -q "="; then
    echo "⚠️  Potential secrets detected in staging area"
    echo "Please review your changes before committing"
fi

echo "✅ Pre-commit checks passed"
exit 0
"""

        with open(pre_commit_hook, 'w') as f:
            f.write(pre_commit_content)

        # Make executable
        pre_commit_hook.chmod(0o755)

        # Post-commit hook
        post_commit_hook = hooks_dir / "post-commit"
        post_commit_content = """#!/bin/bash
# PyDock post-commit hook

echo "📝 Commit $(git rev-parse --short HEAD) created"
echo "🚀 Ready for deployment with: pydock deploy"
"""

        with open(post_commit_hook, 'w') as f:
            f.write(post_commit_content)

        post_commit_hook.chmod(0o755)

        logger.success("✅ Git hooks installed")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup Git hooks: {str(e)}")
        return False


def get_commit_history(repo_path: str, limit: int = 10) -> List[Dict]:
    """
    Get commit history

    Args:
        repo_path: Path to repository
        limit: Number of commits to retrieve

    Returns:
        List of commit information
    """
    try:
        repo = Repo(repo_path)
        commits = []

        for commit in repo.iter_commits(max_count=limit):
            commits.append({
                "hash": commit.hexsha,
                "hash_short": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files)
            })

        return commits

    except Exception as e:
        logger.error(f"❌ Failed to get commit history: {str(e)}")
        return []


def create_gitignore_for_pydock(repo_path: str) -> bool:
    """
    Create or update .gitignore with PyDock-specific entries

    Args:
        repo_path: Path to repository

    Returns:
        True if .gitignore was updated
    """
    logger.info("📝 Updating .gitignore for PyDock")

    try:
        gitignore_path = Path(repo_path) / ".gitignore"

        pydock_entries = [
            "",
            "# PyDock",
            ".env",
            ".env.local",
            ".env.production",
            "pydock.json",
            ".pydock/",
            "deployments/",
            "*.log",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            ".coverage",
            "htmlcov/",
            "dist/",
            "build/",
            "*.egg-info/",
            ".venv/",
            "venv/",
            "node_modules/",
            ".npm/",
            ".docker/",
            "Dockerfile.prod",
            "docker-compose.prod.yml",
            "Caddyfile.prod",
        ]

        # Read existing content
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()

        # Check if PyDock section already exists
        if "# PyDock" in existing_content:
            logger.info("✅ PyDock entries already exist in .gitignore")
            return True

        # Append PyDock entries
        with open(gitignore_path, 'a') as f:
            f.write('\n'.join(pydock_entries))

        logger.success("✅ Updated .gitignore with PyDock entries")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to update .gitignore: {str(e)}")
        return False


def validate_repo_for_deployment(repo_path: str) -> Dict[str, Any]:
    """
    Validate repository for deployment readiness

    Args:
        repo_path: Path to repository

    Returns:
        Validation results
    """
    logger.info("🔍 Validating repository for deployment")

    validation = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "project_type": {},
        "required_files": {},
        "recommendations": []
    }

    try:
        path = Path(repo_path)

        # Check if it's a Git repository
        repo_info = get_repo_info(repo_path)
        if not repo_info:
            validation["errors"].append("Not a Git repository")
            validation["valid"] = False
            return validation

        # Detect project type
        validation["project_type"] = detect_project_type(repo_path)

        # Check for uncommitted changes
        if repo_info["is_dirty"]:
            validation["warnings"].append("Repository has uncommitted changes")

        # Check for untracked files
        if repo_info["untracked_files"]:
            validation["warnings"].append(f"Repository has {len(repo_info['untracked_files'])} untracked files")

        # Check for required files based on project type
        required_files = {
            "Dockerfile": (path / "Dockerfile").exists(),
            "docker-compose.yml": (path / "docker-compose.yml").exists() or (path / "docker-compose.yaml").exists(),
            ".gitignore": (path / ".gitignore").exists(),
        }

        # Project-specific requirements
        if validation["project_type"]["python"]:
            required_files["requirements.txt or pyproject.toml"] = (
                    (path / "requirements.txt").exists() or
                    (path / "pyproject.toml").exists()
            )

        if validation["project_type"]["nodejs"]:
            required_files["package.json"] = (path / "package.json").exists()

        validation["required_files"] = required_files

        # Check for missing required files
        missing_files = [name for name, exists in required_files.items() if not exists]
        if missing_files:
            validation["errors"].extend([f"Missing required file: {file}" for file in missing_files])

        # Recommendations
        if not (path / "README.md").exists():
            validation["recommendations"].append("Add README.md for documentation")

        if not (path / ".env.template").exists():
            validation["recommendations"].append("Add .env.template for environment configuration")

        if not required_files.get("Dockerfile", False):
            validation["recommendations"].append("Add Dockerfile for containerization")

        # Final validation
        if validation["errors"]:
            validation["valid"] = False

        return validation

    except Exception as e:
        validation["errors"].append(f"Validation failed: {str(e)}")
        validation["valid"] = False
        return validation
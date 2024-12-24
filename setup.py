from setuptools import setup, find_packages, Command
import subprocess
import os
import shutil
import sys
from pathlib import Path

class BuildFrontendCommand(Command):
    description = 'build frontend assets'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self._build_frontend()
        except Exception as e:
            print(f"Error building frontend: {str(e)}", file=sys.stderr)
            raise

    def _build_frontend(self):
        frontend_dir = Path(__file__).parent / 'frontend'
        if not frontend_dir.exists():
            print(f"Frontend directory not found at {frontend_dir}", file=sys.stderr)
            return

        print("Building frontend assets...")
        try:
            # Run npm install with error handling
            result = subprocess.run(['npm', 'install'], cwd=frontend_dir, 
                                 capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print(f"npm install failed: {result.stderr}", file=sys.stderr)
                raise Exception("npm install failed")

            # Run npm build with error handling
            result = subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, 
                                 capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print(f"npm build failed: {result.stderr}", file=sys.stderr)
                raise Exception("npm build failed")

            # Copy the built assets
            self._copy_assets(frontend_dir)

        except subprocess.CalledProcessError as e:
            print(f"Failed to build frontend: {str(e)}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Unexpected error building frontend: {str(e)}", file=sys.stderr)
            raise

    def _copy_assets(self, frontend_dir):
        dist_dir = frontend_dir / 'dist'
        if not dist_dir.exists():
            raise Exception(f"Build directory not found at {dist_dir}")

        package_static_dir = Path(__file__).parent / 'preswald' / 'static'
        package_static_dir.mkdir(parents=True, exist_ok=True)

        # Copy dist contents
        print(f"Copying built assets to {package_static_dir}")
        for item in dist_dir.iterdir():
            dest = package_static_dir / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # Copy public assets
        public_dir = frontend_dir / 'public'
        if public_dir.exists():
            print("Copying public assets...")
            for item in public_dir.iterdir():
                dest = package_static_dir / item.name
                if not dest.exists():
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)

# Setup configuration
setup(
    name="preswald",
    version="0.1.0",
    author="Structured",
    author_email="founders@structuredlabs.com",
    description="A lightweight data workflow SDK.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/StructuredLabs/preswald",
    license="Apache License 2.0",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8,<3.13",
    include_package_data=True,
    package_data={
        'preswald': ['static/*', 'static/assets/*'],
    },
    install_requires=[
        'fastapi>=0.68.0,<1.0.0',
        'uvicorn>=0.15.0,<1.0.0',
        'websockets>=10.0,<11.0',
        'python-multipart>=0.0.5,<0.1.0',
        'httpx>=0.23.0,<1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'preswald=preswald.cli:cli',
        ],
    },
    python_requires='>=3.7',
    cmdclass={
        'build_frontend': BuildFrontendCommand,
    },
)

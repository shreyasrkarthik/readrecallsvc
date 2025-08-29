#!/usr/bin/env python3
"""
Test script to verify ReadRecall FastAPI service setup
"""

import sys
import os
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'alembic',
        'jose',
        'passlib',
        'opensearchpy',
        'PyPDF2',
        'ebooklib',
        'google.generativeai',
        'pydantic',
        'python_dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module.replace('-', '_'))
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful!")
    return True


def test_app_structure():
    """Test if the app structure is correct"""
    print("\n📁 Testing app structure...")
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/core/__init__.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/core/security.py',
        'app/models/__init__.py',
        'app/models/user.py',
        'app/models/book.py',
        'app/models/summary.py',
        'app/models/character.py',
        'app/models/reading_state.py',
        'app/api/__init__.py',
        'app/api/deps.py',
        'app/api/auth.py',
        'app/api/books.py',
        'app/api/summaries.py',
        'app/api/characters.py',
        'app/api/reading_state.py',
        'app/services/__init__.py',
        'app/services/opensearch_service.py',
        'app/services/gemini_service.py',
        'app/services/book_processor.py',
        'app/services/file_manager.py',
        'app/utils/__init__.py',
        'app/utils/schemas.py',
        'requirements.txt',
        'env.example',
        'alembic.ini',
        'alembic/env.py',
        'README.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"  ❌ Missing: {file_path}")
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ App structure is correct!")
    return True


def test_directories():
    """Test if required directories exist"""
    print("\n📂 Testing directories...")
    
    required_dirs = [
        'uploads',
        'uploads/books',
        'uploads/covers', 
        'uploads/temp',
        'tests',
        'alembic',
        'alembic/versions'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"  ❌ Missing: {dir_path}")
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing_dirs:
        print(f"\n⚠️  Missing directories: {', '.join(missing_dirs)}")
        print("Run: mkdir -p " + " ".join(missing_dirs))
    else:
        print("✅ All directories exist!")
    
    return len(missing_dirs) == 0


def test_env_file():
    """Test if .env file exists"""
    print("\n🔧 Testing environment configuration...")
    
    if Path('.env').exists():
        print("  ✅ .env file exists")
        return True
    elif Path('env.example').exists():
        print("  ⚠️  .env file not found, but env.example exists")
        print("  Run: cp env.example .env")
        return False
    else:
        print("  ❌ Neither .env nor env.example found")
        return False


def test_app_startup():
    """Test if the app can start without errors"""
    print("\n🚀 Testing app startup...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        # Try to import the main app
        from app.main import app
        print("  ✅ App imports successfully")
        
        # Try to create a test client
        from fastapi.testclient import TestClient
        client = TestClient(app)
        print("  ✅ Test client created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ App startup failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🔍 ReadRecall FastAPI Service Setup Test\n")
    
    tests = [
        test_imports,
        test_app_structure,
        test_directories,
        test_env_file,
        test_app_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Configure your .env file")
        print("2. Run database migrations: alembic upgrade head")
        print("3. Start the server: python run_dev.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

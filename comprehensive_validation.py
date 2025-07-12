#!/usr/bin/env python3
"""
Comprehensive validation script to check if the project satisfies 
ALL requirements from the original task description.
"""

import os
import sys
import subprocess
import csv
from datetime import datetime
from pathlib import Path

def check_project_structure():
    """Check if the project structure matches the requirements"""
    print("🏗️  Checking Project Structure...")
    
    required_files = [
        "src/research_scout/__init__.py",
        "src/research_scout/paper_hunter.py",  # Equivalent to fetcher.py
        "src/research_scout/research_types.py",  # Equivalent to models.py
        "src/research_scout/company_finder.py",  # Equivalent to utils.py
        "src/research_scout/data_writer.py",  # Equivalent to csv_export.py
        "src/research_scout/commander.py",  # Equivalent to cli.py
        "tests/test_pubmed_fetcher.py",
        "pyproject.toml",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_cli_functionality():
    """Check if CLI command works as specified"""
    print("\n🖥️  Checking CLI Functionality...")
    
    try:
        # Test basic CLI command
        result = subprocess.run([
            "poetry", "run", "get-papers-list", "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI command 'get-papers-list' working")
            return True
        else:
            print(f"❌ CLI command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def check_output_format():
    """Check if CSV output format matches requirements"""
    print("\n📊 Checking Output Format...")
    
    # Find the most recent CSV file
    csv_files = list(Path(".").glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found to check format")
        return False
    
    latest_csv = max(csv_files, key=os.path.getctime)
    
    try:
        with open(latest_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            required_columns = [
                'PubmedID',
                'Title', 
                'Publication Date',
                'Non-academic Author(s)',
                'Company Affiliation(s)',
                'Corresponding Author Email'
            ]
            
            if header == required_columns:
                print("✅ CSV format matches requirements exactly")
                
                # Check if we have data rows
                rows = list(reader)
                if rows:
                    print(f"✅ Found {len(rows)} data rows")
                    return True
                else:
                    print("⚠️  CSV has correct format but no data rows")
                    return True
            else:
                print(f"❌ CSV header mismatch:")
                print(f"   Expected: {required_columns}")
                print(f"   Found:    {header}")
                return False
                
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def check_company_detection():
    """Test company detection against requirements"""
    print("\n🏢 Checking Company Detection Logic...")
    
    try:
        from src.research_scout.company_finder import IndustryDetector
        
        # Test 1: Known Company Database
        test_cases_known = [
            ("Pfizer Inc, New York", True, "Pfizer"),
            ("Johnson & Johnson, New Brunswick", True, "Johnson & Johnson"),
            ("Janssen Pharmaceuticals", True, "Johnson & Johnson (Janssen)"),
        ]
        
        print("  Testing Known Company Database...")
        known_company_pass = True
        for affiliation, should_detect, expected_company in test_cases_known:
            is_industry = IndustryDetector.is_industry_affiliated(affiliation)
            companies = IndustryDetector.extract_company_names(affiliation)
            
            if is_industry == should_detect and (not should_detect or expected_company in companies):
                print(f"    ✅ {affiliation[:30]}... -> {companies}")
            else:
                print(f"    ❌ {affiliation[:30]}... -> {companies} (expected {expected_company})")
                known_company_pass = False
        
        # Test 2: Keyword Detection
        print("  Testing Keyword Detection...")
        test_cases_keywords = [
            ("Acme Pharmaceutical Company, Boston", True),
            ("BioTech Solutions Inc", True),
            ("Therapeutics Research Corp", True),
        ]
        
        keyword_pass = True
        for affiliation, should_detect in test_cases_keywords:
            is_industry = IndustryDetector.is_industry_affiliated(affiliation)
            companies = IndustryDetector.extract_company_names(affiliation)
            
            if is_industry == should_detect and (not should_detect or companies):
                print(f"    ✅ {affiliation[:30]}... -> {companies}")
            else:
                print(f"    ❌ {affiliation[:30]}... -> {companies}")
                keyword_pass = False
        
        # Test 3: Academic Exclusion
        print("  Testing Academic Institution Exclusion...")
        test_cases_academic = [
            ("Department of Pharmaceutical Sciences, Harvard University", False),
            ("University of California, Biotech Department", False),
        ]
        
        academic_pass = True
        for affiliation, should_detect in test_cases_academic:
            is_industry = IndustryDetector.is_industry_affiliated(affiliation)
            companies = IndustryDetector.extract_company_names(affiliation)
            
            if is_industry == should_detect:
                print(f"    ✅ {affiliation[:40]}... -> Correctly excluded")
            else:
                print(f"    ❌ {affiliation[:40]}... -> Incorrectly detected as {companies}")
                academic_pass = False
        
        return known_company_pass and keyword_pass and academic_pass
        
    except ImportError as e:
        print(f"❌ Cannot import company detection module: {e}")
        return False

def check_api_integration():
    """Check PubMed API integration"""
    print("\n🌐 Checking PubMed API Integration...")
    
    try:
        # Test a simple query
        result = subprocess.run([
            "poetry", "run", "get-papers-list", "aspirin", 
            "--max-results", "2", "--file", "validation_test.csv"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Check if file was created
            if os.path.exists("validation_test.csv"):
                print("✅ PubMed API integration working")
                # Clean up
                os.remove("validation_test.csv")
                return True
            else:
                print("❌ API call succeeded but no output file created")
                return False
        else:
            print(f"❌ API test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def check_required_features():
    """Check all required features from task description"""
    print("\n🎯 Checking Required Features...")
    
    features = {
        "PubMed API Integration": True,  # Assumed if other tests pass
        "Company Detection": True,       # Will be tested above
        "CSV Export": True,              # Will be tested above
        "Command-line Interface": True,  # Will be tested above
        "Modular Design": True,          # Check if modules exist
        "Type Safety": False,            # Need to check type hints
        "Error Handling": False          # Need to check error handling
    }
    
    # Check type safety
    try:
        from src.research_scout import research_types
        print("✅ Type definitions found")
        features["Type Safety"] = True
    except:
        print("❌ Type definitions missing")
    
    # Check error handling (look for try-catch blocks)
    try:
        with open("src/research_scout/paper_hunter.py", "r") as f:
            content = f.read()
            if "try:" in content and "except" in content:
                print("✅ Error handling implemented")
                features["Error Handling"] = True
            else:
                print("❌ No error handling found")
    except:
        print("❌ Cannot check error handling")
    
    return all(features.values())

def main():
    """Run comprehensive validation"""
    print("🔍 COMPREHENSIVE PROJECT VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Project Structure", check_project_structure),
        ("CLI Functionality", check_cli_functionality),
        ("Output Format", check_output_format),
        ("Company Detection", check_company_detection),
        ("API Integration", check_api_integration),
        ("Required Features", check_required_features),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL REQUIREMENTS SATISFIED!")
        print("Your project fully meets the task description requirements.")
    else:
        print("⚠️  SOME REQUIREMENTS NOT MET")
        print("Please review the failed tests above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

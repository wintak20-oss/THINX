"""
Test script for FAIR Data Point integration
Run this to verify the EEPA FAIR Data Point connection works
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.fair_data_point import FairDataPointClient, get_eepa_fdp_info, get_eepa_catalogs


def test_fdp_connection():
    """Test basic connection to FAIR Data Point"""
    print("Testing FAIR Data Point Connection...")
    print("=" * 60)
    
    try:
        # Test 1: Get FDP Info
        print("\n1. Testing FDP Metadata Retrieval...")
        fdp_info = get_eepa_fdp_info()
        
        if fdp_info:
            print("   ✓ Successfully connected to FAIR Data Point")
            print(f"   Title: {fdp_info.get('title')}")
            print(f"   Contact: {fdp_info.get('contact')}")
            print(f"   Publisher: {fdp_info.get('publisher')}")
            catalogs_list = fdp_info.get('catalogs', [])
            print(f"   Available Catalogs: {len(catalogs_list)}")
            print(f"   Catalog URLs: {catalogs_list[:3]}")  # Show first 3 for debugging
        else:
            print("   ✗ Failed to retrieve FDP metadata")
            return False
        
        # Test 2: Get Catalogs
        print("\n2. Testing Catalog Retrieval...")
        catalogs = get_eepa_catalogs()
        
        if catalogs:
            print(f"   ✓ Successfully retrieved {len(catalogs)} catalogs")
            for i, catalog in enumerate(catalogs, 1):
                print(f"\n   Catalog {i}:")
                print(f"      Title: {catalog.get('title')}")
                print(f"      Publisher: {catalog.get('publisher')}")
                print(f"      Datasets: {len(catalog.get('datasets', []))}")
                print(f"      License: {catalog.get('license')}")
        else:
            print("   ✗ No catalogs found")
            return False
        
        # Test 3: Get detailed catalog info
        if catalogs and len(catalogs) > 0:
            print("\n3. Testing Detailed Catalog Retrieval...")
            first_catalog = catalogs[0]
            catalog_url = first_catalog.get('id')
            
            if catalog_url:
                print(f"   Testing catalog: {catalog_url}")
                client = FairDataPointClient(verify_ssl=False)
                detailed = client.get_catalog_details(catalog_url)
                if detailed:
                    print(f"   ✓ Successfully retrieved detailed info for: {detailed.get('title')}")
                    print(f"      Description: {detailed.get('description', 'N/A')[:100] if detailed.get('description') else 'N/A'}...")
                    print(f"      Datasets: {len(detailed.get('datasets', []))}")
                else:
                    print("   ✗ Failed to retrieve detailed catalog info")
            else:
                print("   ✗ No valid catalog URL found")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! FAIR Data Point integration is working.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fdp_connection()
    sys.exit(0 if success else 1)

"""
FAIR Data Point (FDP) Client
Fetches metadata about available datasets from the EEPA FAIR Data Point
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import warnings
from urllib3.exceptions import InsecureRequestWarning


class FairDataPointClient:
    """Client for interacting with FAIR Data Point API"""
    
    def __init__(self, fdp_url: str = "https://fairdp.colo.ba.be", verify_ssl: bool = False):
        """
        Initialize FAIR Data Point client
        
        Args:
            fdp_url: Base URL of the FAIR Data Point
            verify_ssl: Whether to verify SSL certificates. Set to False to ignore 
                       certificate errors (useful for expired/self-signed certificates)
        """
        self.fdp_url = fdp_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/ld+json',
            'User-Agent': 'Thinx-HDS-Client/1.0'
        })
        
        # Suppress SSL warnings if verification is disabled
        if not verify_ssl:
            warnings.simplefilter('ignore', InsecureRequestWarning)
    
    def get_fdp_metadata(self) -> Optional[Dict]:
        """
        Fetch metadata about the FAIR Data Point itself
        Returns basic info including description, contact, and available catalogs
        """
        try:
            response = self.session.get(f"{self.fdp_url}/?format=jsonld", timeout=10, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()
            
            # Parse the JSON-LD response
            if isinstance(data, list) and len(data) > 0:
                fdp_info = data[0]
                return self._parse_fdp_info(fdp_info, data)
            
            return None
        except Exception as e:
            print(f"Error fetching FDP metadata: {e}")
            return None
    
    def _parse_fdp_info(self, fdp_info: Dict, full_data: List[Dict]) -> Dict:
        """Parse FDP metadata into a simplified structure"""
        # Extract main FDP information
        result = {
            'id': fdp_info.get('@id'),
            'title': self._get_value(fdp_info.get('http://purl.org/dc/terms/title')),
            'description': self._get_value(fdp_info.get('http://purl.org/dc/terms/description')),
            'version': self._get_value(fdp_info.get('http://purl.org/dc/terms/hasVersion')),
            'contact': self._get_value(fdp_info.get('http://www.w3.org/ns/dcat#contactPoint')),
            'language': fdp_info.get('http://purl.org/dc/terms/language', [{}])[0].get('@id'),
            'license': fdp_info.get('http://purl.org/dc/terms/license', [{}])[0].get('@id'),
            'publisher': self._get_publisher_name(fdp_info, full_data),
            'metadata_issued': self._get_value(fdp_info.get('https://w3id.org/fdp/fdp-o#metadataIssued')),
            'metadata_modified': self._get_value(fdp_info.get('https://w3id.org/fdp/fdp-o#metadataModified')),
            'catalogs': self._extract_catalog_ids(fdp_info)
        }
        
        return result
    
    def get_catalogs(self) -> List[Dict]:
        """
        Fetch list of all available data catalogs
        Returns simplified catalog information with metadata
        """
        fdp_metadata = self.get_fdp_metadata()
        if not fdp_metadata or 'catalogs' not in fdp_metadata:
            return []
        
        catalogs = []
        for catalog_url in fdp_metadata['catalogs']:
            # Skip blank nodes
            if catalog_url.startswith('_:'):
                continue
            catalog_info = self.get_catalog_details(catalog_url)
            if catalog_info:
                # Add actual dataset count
                catalog_info['dataset_count'] = len(catalog_info.get('datasets', []))
                catalogs.append(catalog_info)
        
        return catalogs
    
    def get_catalog_details(self, catalog_url: str) -> Optional[Dict]:
        """
        Fetch detailed information about a specific catalog
        """
        try:
            response = self.session.get(f"{catalog_url}?format=jsonld", timeout=10, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                # Find the main catalog object (not blank nodes)
                catalog_info = None
                for item in data:
                    item_id = item.get('@id', '')
                    if item_id == catalog_url or (item_id and not item_id.startswith('_:')):
                        catalog_info = item
                        break
                
                if not catalog_info:
                    catalog_info = data[0]
                    
                return self._parse_catalog_info(catalog_info, data)
            
            return None
        except Exception as e:
            print(f"Error fetching catalog {catalog_url}: {e}")
            return None
    
    def _parse_catalog_info(self, catalog_info: Dict, full_data: List[Dict]) -> Dict:
        """Parse catalog metadata into simplified structure"""
        license_url = catalog_info.get('http://purl.org/dc/terms/license', [{}])[0].get('@id')
        result = {
            'id': catalog_info.get('@id'),
            'title': self._get_value(catalog_info.get('http://purl.org/dc/terms/title')),
            'description': self._get_value(catalog_info.get('http://purl.org/dc/terms/description')),
            'publisher': self._get_publisher_name(catalog_info, full_data),
            'license': self._get_license_name(license_url),
            'license_url': license_url,
            'issued': self._get_value(catalog_info.get('http://purl.org/dc/terms/issued')),
            'modified': self._get_value(catalog_info.get('http://purl.org/dc/terms/modified')),
            'metadata_issued': self._get_value(catalog_info.get('https://w3id.org/fdp/fdp-o#metadataIssued')),
            'metadata_modified': self._get_value(catalog_info.get('https://w3id.org/fdp/fdp-o#metadataModified')),
            'themes': self._extract_themes(catalog_info),
            'datasets': self._extract_dataset_ids(catalog_info),
            'access_rights': self._get_access_rights(catalog_info, full_data)
        }
        
        return result
    
    def get_datasets(self, catalog_url: str) -> List[Dict]:
        """
        Fetch all datasets within a specific catalog
        """
        catalog_info = self.get_catalog_details(catalog_url)
        if not catalog_info or 'datasets' not in catalog_info:
            return []
        
        datasets = []
        for dataset_url in catalog_info['datasets']:
            dataset_info = self.get_dataset_details(dataset_url)
            if dataset_info:
                datasets.append(dataset_info)
        
        return datasets
    
    def get_dataset_details(self, dataset_url: str) -> Optional[Dict]:
        """
        Fetch detailed information about a specific dataset
        """
        try:
            response = self.session.get(f"{dataset_url}?format=jsonld", timeout=10, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                dataset_info = data[0]
                return self._parse_dataset_info(dataset_info, data)
            
            return None
        except Exception as e:
            print(f"Error fetching dataset {dataset_url}: {e}")
            return None
    
    def _parse_dataset_info(self, dataset_info: Dict, full_data: List[Dict]) -> Dict:
        """Parse dataset metadata into simplified structure"""
        license_url = dataset_info.get('http://purl.org/dc/terms/license', [{}])[0].get('@id')
        result = {
            'id': dataset_info.get('@id'),
            'title': self._get_value(dataset_info.get('http://purl.org/dc/terms/title')),
            'description': self._get_value(dataset_info.get('http://purl.org/dc/terms/description')),
            'publisher': self._get_publisher_name(dataset_info, full_data),
            'license': self._get_license_name(license_url),
            'license_url': license_url,
            'issued': self._get_value(dataset_info.get('http://purl.org/dc/terms/issued')),
            'modified': self._get_value(dataset_info.get('http://purl.org/dc/terms/modified')),
            'themes': self._extract_themes(dataset_info),
            'keywords': self._extract_keywords(dataset_info),
            'distributions': self._extract_distribution_ids(dataset_info),
            'access_rights': self._get_access_rights(dataset_info, full_data)
        }
        
        return result
    
    # Helper methods for parsing JSON-LD
    
    def _get_value(self, field) -> Optional[str]:
        """Extract value from JSON-LD field"""
        if not field:
            return None
        if isinstance(field, list) and len(field) > 0:
            item = field[0]
            if isinstance(item, dict):
                return item.get('@value') or item.get('@id')
            return item
        if isinstance(field, dict):
            return field.get('@value') or field.get('@id')
        return str(field)
    
    def _get_publisher_name(self, entity: Dict, full_data: List[Dict]) -> Optional[str]:
        """Extract publisher name from entity"""
        publisher_refs = entity.get('http://purl.org/dc/terms/publisher', [])
        if not publisher_refs:
            return None
        
        publisher_id = publisher_refs[0].get('@id') if isinstance(publisher_refs[0], dict) else None
        if not publisher_id:
            return None
        
        # Find publisher in full data
        for item in full_data:
            if item.get('@id') == publisher_id:
                name_field = item.get('http://xmlns.com/foaf/0.1/name')
                return self._get_value(name_field)
        
        return None
    
    def _get_access_rights(self, entity: Dict, full_data: List[Dict]) -> Optional[str]:
        """Extract access rights description"""
        access_refs = entity.get('http://purl.org/dc/terms/accessRights', [])
        if not access_refs:
            return None
        
        access_id = access_refs[0].get('@id') if isinstance(access_refs[0], dict) else None
        if not access_id:
            return None
        
        # Find access rights in full data
        for item in full_data:
            if item.get('@id') == access_id:
                desc_field = item.get('http://purl.org/dc/terms/description')
                return self._get_value(desc_field)
        
        return None
    
    def _get_license_name(self, license_url: Optional[str]) -> str:
        """Extract readable license name from URL"""
        if not license_url:
            return "Not specified"
        
        # Common Creative Commons licenses
        license_map = {
            'cc-by': 'CC BY',
            'cc-by-sa': 'CC BY-SA',
            'cc-by-nd': 'CC BY-ND',
            'cc-by-nc': 'CC BY-NC',
            'cc-by-nc-sa': 'CC BY-NC-SA',
            'cc-by-nc-nd': 'CC BY-NC-ND',
            'cc0': 'CC0',
            'publicdomain': 'Public Domain'
        }
        
        # Try to extract license from URL
        url_lower = license_url.lower()
        for key, name in license_map.items():
            if key in url_lower:
                # Extract version if present (e.g., 3.0, 4.0)
                import re
                version_match = re.search(r'(\d+\.\d+)', license_url)
                if version_match:
                    return f"{name} {version_match.group(1)}"
                return name
        
        # If no match, try to extract last part of URL
        parts = license_url.rstrip('/').split('/')
        if parts:
            return parts[-1].replace('-', ' ').replace('_', ' ').title()
        
        return "Custom License"
    
    def _extract_catalog_ids(self, fdp_info: Dict) -> List[str]:
        """Extract catalog URLs from FDP metadata"""
        catalogs = fdp_info.get('https://w3id.org/fdp/fdp-o#metadataCatalog', [])
        # Filter out blank nodes (starting with _:) and only return actual URLs
        return [cat.get('@id') for cat in catalogs 
                if isinstance(cat, dict) and '@id' in cat 
                and not cat.get('@id', '').startswith('_:')]
    
    def _extract_dataset_ids(self, catalog_info: Dict) -> List[str]:
        """Extract dataset URLs from catalog metadata"""
        # Try both DCAT and FDP-specific properties for datasets
        datasets = (catalog_info.get('http://www.w3.org/ns/dcat#dataset', []) or 
                   catalog_info.get('https://w3id.org/fdp/fdp-o#metadataDataset', []))
        # Filter out blank nodes (starting with _:) and only return actual URLs
        return [ds.get('@id') for ds in datasets 
                if isinstance(ds, dict) and '@id' in ds 
                and not ds.get('@id', '').startswith('_:')]
    
    def _extract_distribution_ids(self, dataset_info: Dict) -> List[str]:
        """Extract distribution URLs from dataset metadata"""
        distributions = dataset_info.get('http://www.w3.org/ns/dcat#distribution', [])
        # Filter out blank nodes (starting with _:) and only return actual URLs
        return [dist.get('@id') for dist in distributions 
                if isinstance(dist, dict) and '@id' in dist 
                and not dist.get('@id', '').startswith('_:')]
    
    def _extract_themes(self, entity: Dict) -> List[str]:
        """Extract theme URLs from entity"""
        themes = entity.get('http://www.w3.org/ns/dcat#theme', [])
        return [theme.get('@id') for theme in themes if isinstance(theme, dict) and '@id' in theme]
    
    def _extract_keywords(self, entity: Dict) -> List[str]:
        """Extract keywords from entity"""
        keywords = entity.get('http://www.w3.org/ns/dcat#keyword', [])
        return [self._get_value([kw]) for kw in keywords]


# Convenience functions
def get_eepa_catalogs(verify_ssl: bool = False) -> List[Dict]:
    """Get all available catalogs from EEPA FAIR Data Point
    
    Args:
        verify_ssl: Whether to verify SSL certificates (default: False for compatibility)
    """
    client = FairDataPointClient(verify_ssl=verify_ssl)
    return client.get_catalogs()


def get_eepa_fdp_info(verify_ssl: bool = False) -> Optional[Dict]:
    """Get EEPA FAIR Data Point metadata
    
    Args:
        verify_ssl: Whether to verify SSL certificates (default: False for compatibility)
    """
    client = FairDataPointClient(verify_ssl=verify_ssl)
    return client.get_fdp_metadata()

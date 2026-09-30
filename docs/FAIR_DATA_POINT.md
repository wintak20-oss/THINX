# FAIR Data Point Integration

## Overview

The Thinx platform integrates with the **EEPA FAIR Data Point** (https://fairdp.colo.ba.be), allowing researchers to discover and access sensitive refugee and human trafficking research datasets through a FAIR (Findable, Accessible, Interoperable, Reusable) data infrastructure.

## What is a FAIR Data Point

A FAIR Data Point (FDP) is a metadata service that publishes information about data catalogs, datasets, and distributions. It provides:

- **Metadata about datasets**: Title, description, publisher, license, themes
- **Contact information**: Who to contact to request data access
- **Discovery**: Browse available data before requesting credentials
- **FAIR principles**: Ensures data follows international standards for findability and accessibility

## FAIR Principles

### Findable

Data and metadata are easy to find for both humans and computers:
- Datasets have persistent identifiers (URIs)
- Metadata is searchable
- Datasets are registered in searchable resources (FDP)

### Accessible

Data is retrievable via standardized protocols:
- Uses standard web protocols (HTTP/HTTPS)
- Authentication and authorization when required
- Metadata remains accessible even if data is restricted

### Interoperable

Data can be integrated with other data and work with applications:
- Uses formal, accessible vocabularies
- Follows community standards
- Includes references to other data

### Reusable

Data is well-described and can be used in different contexts:
- Clear usage licenses
- Detailed provenance information
- Follows community standards for the domain

## Integration Features

### 1. Browse Available Catalogs

The EEPA FAIR Data Point contains multiple data catalogs. Researchers can browse these catalogs to discover datasets before requesting access.

**Access the FDP:**
- URL: https://fairdp.colo.ba.be
- Browse catalogs and datasets through web interface
- View metadata without requiring authentication

### 2. Dataset Metadata

For each dataset, the FDP provides:

- **Title**: Dataset name
- **Description**: What the dataset contains
- **Publisher**: Organization responsible for the data
- **License**: Usage rights and restrictions
- **Themes**: Subject areas covered
- **Keywords**: Search terms
- **Contact Point**: Who to contact for access
- **Distribution**: Available formats and access methods

### 3. Request Access

After finding a relevant dataset:

1. Note the dataset identifier and contact information
2. Contact the data publisher using provided contact point
3. Request credentials (server, repository, username, password)
4. Once received, use credentials to create connection in Thinx

### 4. Add Connection with Metadata

When creating a connection in Thinx, you can optionally include the FDP URL:

**Connection Form Fields:**
- Connection Name
- Server URL/IP
- Port
- Repository Name
- Username
- Password
- **FAIR Data Point URL** (optional) - Link back to the dataset metadata

This creates a link between your local connection and the original dataset in the FDP.

### 5. View Catalog Information

If a connection includes an FDP URL, Thinx can fetch and display:

- Dataset title and description
- Publisher information
- License terms
- Last modified date
- Contact information
- Available distributions

## FAIR-OLR Compliance

Thinx implements **FAIR-OLR** (FAIR - Ontology-based Layered Routing) principles:

### Ontology-Based Data Model

- Uses `hds_cdm.ttl` (Human Data Science Common Data Model)
- Semantic web standards (RDF, SPARQL)
- Consistent vocabulary across datasets

### Layered Architecture

```
┌────────────────────────┐
│   User Interface       │ Layer 3: Presentation
├────────────────────────┤
│   API Layer            │ Layer 2: Business Logic
├────────────────────────┤
│   Data Access Layer    │ Layer 1: Data Storage
└────────────────────────┘
```

### Routing

- Multiple data sources can be accessed through single interface
- Each connection routes to different data repository
- Maintains metadata link to original FDP

## Using FAIR Metadata in Thinx

### Step 1: Discover Dataset

1. Visit EEPA FAIR Data Point: https://fairdp.colo.ba.be
2. Browse catalogs
3. Find dataset of interest
4. Review metadata and access conditions
5. Note the FDP URL for the dataset

### Step 2: Request Access

1. Find contact information in FDP metadata
2. Send access request email including:
   - Your name and affiliation
   - Research purpose
   - Required dataset
   - Ethical approval (if applicable)
3. Wait for response with credentials

### Step 3: Create Connection in Thinx

1. Open Thinx at http://localhost
2. Click "Add New Connection"
3. Fill in connection details received from data provider:
   - Name: Descriptive name for this dataset
   - Server: AllegroGraph server address
   - Port: Usually 10035
   - Repository: Repository name
   - Username: Provided username
   - Password: Provided password
4. Optional: Add FAIR Data Point URL for the dataset
5. Click "Save Connection"

### Step 4: Access Data

1. Select connection from list
2. Click "View Data"
3. Explore dataset using Thinx interface
4. Run queries and analyses

## API Endpoints

### Fetch FDP Metadata

```http
GET /api/fair-metadata?url=https://fairdp.colo.ba.be/catalog/dataset-id
```

**Response:**
```json
{
  "success": true,
  "metadata": {
    "title": "Human Trafficking Dataset Libya 2023",
    "description": "Interview data from refugees...",
    "publisher": "EEPA Research Institute",
    "license": "CC-BY-NC 4.0",
    "modified": "2023-12-01",
    "themes": ["Human Trafficking", "Migration", "Human Rights"],
    "keywords": ["refugees", "Libya", "trafficking"],
    "contactPoint": "data@eepa.org"
  }
}
```

## Benefits of FDP Integration

### For Researchers

- **Discoverability**: Find relevant datasets before requesting access
- **Transparency**: Clear information about data content and usage rights
- **Standardization**: Consistent metadata across different datasets
- **Efficiency**: Faster access to appropriate data

### For Data Providers

- **Visibility**: Datasets more easily discovered by researchers
- **Control**: Maintain access control while providing metadata
- **Compliance**: Meets FAIR data standards
- **Documentation**: Centralized metadata management

### For Research Community

- **Interoperability**: Datasets can work together
- **Reproducibility**: Clear provenance and metadata
- **Citation**: Persistent identifiers for proper attribution
- **Collaboration**: Easier data sharing across institutions

## Technical Implementation

### RDF Data Model

Thinx uses RDF (Resource Description Framework) to align with FAIR principles:

```turtle
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://example.org/dataset/1> a dcat:Dataset ;
    dcterms:title "Human Trafficking Dataset" ;
    dcterms:description "Interview data..." ;
    dcterms:publisher "EEPA" ;
    dcterms:license <http://creativecommons.org/licenses/by-nc/4.0/> .
```

### SPARQL Queries

Access data using standard SPARQL protocol:

```sparql
PREFIX ht: <http://example.org/humantrafficking/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?victim ?age ?nationality
WHERE {
  ?victim a ht:Victim ;
          ht:age ?age ;
          ht:nationality ?nationality .
}
```

### Metadata Standards

Thinx follows these standards:

- **DCAT** (Data Catalog Vocabulary) - For dataset metadata
- **Dublin Core** - For basic metadata elements
- **FOAF** (Friend of a Friend) - For contact information
- **VoID** (Vocabulary of Interlinked Datasets) - For dataset statistics

## Best Practices

### For Researchers

1. **Check FDP first**: Before requesting access, browse FDP to find appropriate datasets
2. **Read license terms**: Understand usage restrictions before accessing data
3. **Include FDP URL**: When creating connections, link to original metadata
4. **Cite properly**: Use persistent identifiers when publishing research

### For Data Providers

1. **Complete metadata**: Provide thorough descriptions in FDP
2. **Keep updated**: Regularly update metadata as data changes
3. **Clear licensing**: Specify usage terms explicitly
4. **Responsive contact**: Respond promptly to access requests

### For System Administrators

1. **Maintain links**: Ensure FDP URLs remain valid
2. **Monitor access**: Log connection usage for accountability
3. **Update regularly**: Keep metadata synchronized with FDP
4. **Document processes**: Maintain clear documentation for users

## Troubleshooting

### Cannot access FAIR Data Point

**Problem**: FDP website not loading

**Solutions**:
- Check internet connection
- Verify URL is correct: https://fairdp.colo.ba.be
- Try accessing from different network
- Contact FDP administrator

### Metadata not displaying in Thinx

**Problem**: FDP metadata not showing in connection details

**Solutions**:
- Verify FDP URL is correct and complete
- Check backend logs: `docker-compose logs backend`
- Test FDP URL in browser directly
- Ensure backend can access internet

### Access request not answered

**Problem**: No response after requesting dataset access

**Solutions**:
- Check spam folder for response
- Verify contact email is correct
- Allow 2-3 business days for response
- Follow up with alternative contact if provided

## References

- **FAIR Principles**: https://www.go-fair.org/fair-principles/
- **EEPA FAIR Data Point**: https://fairdp.colo.ba.be
- **DCAT Vocabulary**: https://www.w3.org/TR/vocab-dcat-2/
- **RDF Primer**: https://www.w3.org/TR/rdf11-primer/
- **SPARQL Query Language**: https://www.w3.org/TR/sparql11-query/

## Support

For questions about:
- **FDP usage**: Contact EEPA at data@eepa.org
- **Thinx integration**: See main documentation
- **Access requests**: Contact dataset publishers directly
- **Technical issues**: See [Troubleshooting](../README.md#troubleshooting)

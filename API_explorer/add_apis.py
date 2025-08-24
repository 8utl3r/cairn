#!/usr/bin/env python3
import json

# New developer tool APIs to add
new_apis = [
    {
        "id": "jsonplaceholder",
        "name": "JSONPlaceholder API",
        "description": "Fake REST API for testing and prototyping",
        "base_url": "https://jsonplaceholder.typicode.com",
        "use_case": "API testing, frontend development, prototyping, learning REST APIs",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["Posts", "Comments", "Users", "Photos", "Todos"],
        "tags": ["testing", "prototyping", "fake-data", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://jsonplaceholder.typicode.com"
    },
    {
        "id": "httpbin",
        "name": "HTTPBin API",
        "description": "HTTP request and response testing service",
        "base_url": "https://httpbin.org",
        "use_case": "HTTP testing, debugging, API development, learning HTTP methods",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["HTTP methods", "Status codes", "Headers", "Cookies", "Authentication testing"],
        "tags": ["testing", "http", "debugging", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://httpbin.org"
    },
    {
        "id": "reqres",
        "name": "ReqRes API",
        "description": "Sample REST API for testing and development",
        "base_url": "https://reqres.in/api",
        "use_case": "API testing, frontend development, learning, prototyping",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["Users", "Resources", "Authentication", "CRUD operations", "Pagination"],
        "tags": ["testing", "sample-data", "development", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://reqres.in"
    },
    {
        "id": "postman-echo",
        "name": "Postman Echo API",
        "description": "Testing service for HTTP requests and responses",
        "base_url": "https://postman-echo.com",
        "use_case": "API testing, Postman collections, HTTP debugging, development",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["HTTP methods", "Headers", "Cookies", "Form data", "JSON responses"],
        "tags": ["testing", "postman", "http", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://docs.postman-echo.com"
    },
    {
        "id": "mockapi",
        "name": "MockAPI",
        "description": "Create custom mock APIs for development and testing",
        "base_url": "https://mockapi.io/projects",
        "use_case": "Custom mock APIs, frontend development, testing, prototyping",
        "pricing": "Free tier: 1 project, Paid: $9/month for unlimited projects",
        "capabilities": ["Custom schemas", "CRUD operations", "Relationships", "Filters", "Real-time updates"],
        "tags": ["testing", "mock-apis", "custom", "free-tier", "rest-api"],
        "authentication": "Project token",
        "rate_limits": "1 project (free), unlimited projects (paid)",
        "documentation_url": "https://mockapi.io/docs"
    },
    {
        "id": "webhook",
        "name": "Webhook.site",
        "description": "Webhook testing and inspection service",
        "base_url": "https://webhook.site",
        "use_case": "Webhook testing, API development, debugging, integration testing",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["Webhook endpoints", "Request inspection", "Response testing", "Custom responses", "Real-time monitoring"],
        "tags": ["webhooks", "testing", "debugging", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://webhook.site"
    },
    {
        "id": "cors-anywhere",
        "name": "CORS Anywhere",
        "description": "CORS proxy for development and testing",
        "base_url": "https://cors-anywhere.herokuapp.com",
        "use_case": "CORS testing, frontend development, API integration, development",
        "pricing": "Free tier: Limited requests, No paid plans",
        "capabilities": ["CORS proxy", "Request forwarding", "Header modification", "Development tool"],
        "tags": ["cors", "proxy", "development", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "Limited requests",
        "documentation_url": "https://github.com/Rob--W/cors-anywhere"
    },
    {
        "id": "ipify",
        "name": "IPify API",
        "description": "Simple IP address lookup service",
        "base_url": "https://api.ipify.org",
        "use_case": "IP detection, geolocation apps, network tools, development",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["IP address", "JSON response", "Plain text", "Multiple formats"],
        "tags": ["ip", "network", "utilities", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://www.ipify.org"
    },
    {
        "id": "uuid-generator",
        "name": "UUID Generator API",
        "description": "Generate UUIDs and GUIDs for development",
        "base_url": "https://www.uuidgenerator.net/api",
        "use_case": "UUID generation, development, testing, unique identifiers",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["UUID v1", "UUID v4", "Multiple formats", "Bulk generation"],
        "tags": ["uuid", "generation", "development", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://www.uuidgenerator.net/api"
    },
    {
        "id": "hash-generator",
        "name": "Hash Generator API",
        "description": "Generate various hash values for development",
        "base_url": "https://api.hashify.net",
        "use_case": "Hash generation, security testing, development, cryptography",
        "pricing": "Free tier: Unlimited, No paid plans",
        "capabilities": ["MD5", "SHA1", "SHA256", "SHA512", "Multiple algorithms"],
        "tags": ["hashing", "cryptography", "security", "free", "rest-api"],
        "authentication": "No authentication required",
        "rate_limits": "No specific limits",
        "documentation_url": "https://hashify.net/api"
    }
]

def add_apis_to_database():
    # Load existing database
    with open('public_apis_database.json', 'r') as f:
        data = json.load(f)
    
    # Add new APIs
    data['apis'].extend(new_apis)
    
    # Update metadata
    data['metadata']['total_apis'] = len(data['apis'])
    
    # Save updated database
    with open('public_apis_database.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Added {len(new_apis)} new APIs to database")
    print(f"Total APIs: {data['metadata']['total_apis']}")

if __name__ == "__main__":
    add_apis_to_database()



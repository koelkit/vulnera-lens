import requests

def fetch_cve_data(vendor, product):
    """
    Connects to the free public CIRCL CVE API 
    and fetches all known vulnerabilities for a specific product.
    """
    vendor_clean = vendor.lower().strip().replace(" ", "_")
    product_clean = product.lower().strip().replace(" ", "_")
    
    url = f"https://cve.circl.lu/api/search/{vendor_clean}/{product_clean}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "Product or vendor not found in the registry."}
        else:
            return {"error": f"Database error (Status code: {response.status_code})"}
    except requests.exceptions.Timeout:
        return {"error": "Connection timed out. Please try again in a few moments."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

'''
Created by the bioinformatics team @ Synnovis
Guy's & St. Thomas' NHS Trust

Simple script to generate CSV containing all current gene/panel relations using PanelApp API
Includes data only from signed-off panels
Stores gene_symbol, hgnc_id, panel[name], confidence_level

Usage: python3 panelapp_gene_query.py
panelapp_gene_data.csv will be saved in the current working directory
'''

import csv
import requests

def fetch_data(url):
    """Call the API"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data from the API. Status code: {response.status_code}")
        return None

def check_panel_signed(panel_id, signed_panels_cache, invalid_panels_cache):
    """Check if the panel is signed off using the signed_off panels endpoint"""

    # If panel_id already checked, skip check to avoid extra API calls
    if panel_id in signed_panels_cache:
        # Already checked and signed-off
        return True
    if panel_id in invalid_panels_cache:
        # Already checked and not signed-off
        return False
    
    # New panel_id found, use API to check status and cache results
    url = f"https://panelapp.genomicsengland.co.uk/api/v1/panels/signedoff/{panel_id}"
    response = requests.get(url)
    if response.status_code == 200 and "detail" not in response.json():
        print(f"Panel {panel_id} is signed off. Caching as signed-off.")
        signed_panels_cache.add(panel_id)
        return True
    else:
        print(f"Panel {panel_id} is not a signed-off panel or does not exist. Caching as invalid.")
        invalid_panels_cache.add(panel_id)
        return False

def write_data_to_csv(data, file_path, signed_panels_cache, invalid_panels_cache):
    """Write to CSV"""
    with open(file_path, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Gene Symbol", "HGNC ID", "Panel Name", "Confidence Level", "Panel ID"])
        write_rows(writer, data, signed_panels_cache, invalid_panels_cache)

def write_rows(writer, data, signed_panels_cache, invalid_panels_cache):
    """Helper function to write rows in CSV"""
    for result in data["results"]:
        gene_data = result["gene_data"]
        gene_symbol = gene_data["gene_symbol"]
        hgnc_id = gene_data["hgnc_id"]
        panel_name = result["panel"]["name"]
        panel_id = result["panel"]["id"]
        confidence_level = result["confidence_level"]

        # Check if the panel is present in the signed-off panel list before adding to list
        if check_panel_signed(panel_id, signed_panels_cache, invalid_panels_cache):
            writer.writerow([gene_symbol, hgnc_id, panel_name, confidence_level, panel_id])

def handle_pagination(data, writer, signed_panels_cache, invalid_panels_cache):
    """Handle pagination"""
    while data["next"]:
        data = fetch_data(data["next"])
        if data:
            write_rows(writer, data, signed_panels_cache, invalid_panels_cache)
        else:
            break

def main():
    url = "https://panelapp.genomicsengland.co.uk/api/v1/genes/"
    output_file = "panelapp_gene_data.csv"
    signed_panels_cache = set()
    invalid_panels_cache = set()
    
    # Initial data fetch
    initial_data = fetch_data(url)
    if initial_data:
        write_data_to_csv(initial_data, output_file, signed_panels_cache, invalid_panels_cache)
        
        # Handle rest of pages
        with open(output_file, mode="a", newline='') as file:
            writer = csv.writer(file)
            handle_pagination(initial_data, writer, signed_panels_cache, invalid_panels_cache)
        
        print(f"Gene data saved to {output_file}")

if __name__ == "__main__":
    main()
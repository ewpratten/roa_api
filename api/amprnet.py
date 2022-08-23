from http.server import BaseHTTPRequestHandler
from datetime import datetime
import requests


def get_all_ampr_roas():
    # Build a list of prefixes that may be announced, per AS
    as_to_prefix = {}

    # Make an irrexplorer query for every ANMPR prefix
    irr_data = requests.get(
        f"https://irrexplorer.nlnog.net/api/prefixes/prefix/44.0.0.0/9").json()

    # Handle each entry
    for entry in irr_data:
        for source in entry["irrRoutes"]:
            for roa in entry["irrRoutes"][source]:

                # Get the prefix and asn
                prefix, asn = roa["rpslPk"].split("AS")

                # Create the ASN in the table if it doesn't exist
                if asn not in as_to_prefix:
                    as_to_prefix[asn] = []

                # Add the prefix to the ASN if it isn't already there
                if prefix not in as_to_prefix[asn]:
                    as_to_prefix[asn].append(prefix)
    return as_to_prefix


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Set headers
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        # Fetch the data
        ampr_roas = get_all_ampr_roas()

        # Write bird-style ROA data
        data = "# Generated by roa.va3zza.com on " + \
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        data += "\n".join(
            [f"route {prefix} max 24 as {asn}" for asn in ampr_roas for prefix in ampr_roas[asn]])
        self.wfile.write(data)
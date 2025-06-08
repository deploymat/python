import asyncio
import httpx
from typing import List, Dict, Optional, Any
import logging
from .settings import get_settings
from .utils import Logger

logger = logging.getLogger(__name__)


class CloudflareManager:
    """Manager for Cloudflare API operations"""

    def __init__(self, api_token: str, email: Optional[str] = None):
        """
        Initialize Cloudflare manager

        Args:
            api_token: Cloudflare API token
            email: Cloudflare account email (optional)
        """
        self.api_token = api_token
        self.email = email
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.logger = Logger()
        self.settings = get_settings()

        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        if email:
            self.headers["X-Auth-Email"] = email

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Cloudflare API

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data

        Returns:
            API response data
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                result = response.json()

                if not result.get("success", False):
                    errors = result.get("errors", [])
                    error_msg = "; ".join([err.get("message", "Unknown error") for err in errors])
                    raise Exception(f"Cloudflare API error: {error_msg}")

                return result.get("result", {})

            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

    async def list_zones(self) -> List[Dict]:
        """
        List all zones in the account

        Returns:
            List of zone data
        """
        self.logger.info("🌐 Fetching Cloudflare zones...")

        zones = await self._make_request("GET", "/zones")

        if isinstance(zones, list):
            self.logger.success(f"✅ Found {len(zones)} zones")
            return zones
        else:
            # Handle paginated response
            all_zones = []
            page = 1

            while True:
                response = await self._make_request("GET", f"/zones?page={page}")
                zones_data = response.get("result", [])

                if not zones_data:
                    break

                all_zones.extend(zones_data)

                # Check if there are more pages
                result_info = response.get("result_info", {})
                if page >= result_info.get("total_pages", 1):
                    break

                page += 1

            self.logger.success(f"✅ Found {len(all_zones)} zones")
            return all_zones

    async def get_zone_by_domain(self, domain: str) -> Optional[Dict]:
        """
        Get zone information by domain name

        Args:
            domain: Domain name

        Returns:
            Zone data or None if not found
        """
        self.logger.info(f"🔍 Looking for zone: {domain}")

        # Try to get zone directly by name
        try:
            zones = await self._make_request("GET", f"/zones?name={domain}")

            if isinstance(zones, list) and zones:
                zone = zones[0]
                self.logger.success(f"✅ Found zone: {zone['name']} ({zone['id']})")
                return zone

        except Exception as e:
            self.logger.debug(f"Direct zone lookup failed: {e}")

        # Fallback: search through all zones
        all_zones = await self.list_zones()

        for zone in all_zones:
            if zone.get("name") == domain:
                self.logger.success(f"✅ Found zone: {zone['name']} ({zone['id']})")
                return zone

        self.logger.error(f"❌ Zone not found for domain: {domain}")
        return None

    async def list_dns_records(self, zone_id: str, record_type: Optional[str] = None) -> List[Dict]:
        """
        List DNS records for a zone

        Args:
            zone_id: Zone ID
            record_type: Filter by record type (A, CNAME, etc.)

        Returns:
            List of DNS records
        """
        endpoint = f"/zones/{zone_id}/dns_records"

        if record_type:
            endpoint += f"?type={record_type}"

        records = await self._make_request("GET", endpoint)

        if isinstance(records, list):
            return records
        else:
            return records.get("result", [])

    async def create_dns_record(
            self,
            zone_id: str,
            record_type: str,
            name: str,
            content: str,
            ttl: int = 300,
            proxied: bool = True
    ) -> Dict:
        """
        Create DNS record

        Args:
            zone_id: Zone ID
            record_type: Record type (A, CNAME, etc.)
            name: Record name
            content: Record content (IP address, etc.)
            ttl: TTL in seconds
            proxied: Whether to proxy through Cloudflare

        Returns:
            Created record data
        """
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl
        }

        # Only add proxied for record types that support it
        if record_type in ["A", "AAAA", "CNAME"]:
            data["proxied"] = proxied

        self.logger.info(f"📝 Creating DNS record: {name} -> {content}")

        record = await self._make_request("POST", f"/zones/{zone_id}/dns_records", data)

        self.logger.success(f"✅ Created {record_type} record: {name}")
        return record

    async def update_dns_record(
            self,
            zone_id: str,
            record_id: str,
            record_type: str,
            name: str,
            content: str,
            ttl: int = 300,
            proxied: bool = True
    ) -> Dict:
        """
        Update existing DNS record

        Args:
            zone_id: Zone ID
            record_id: Record ID
            record_type: Record type
            name: Record name
            content: New content
            ttl: TTL in seconds
            proxied: Whether to proxy through Cloudflare

        Returns:
            Updated record data
        """
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl
        }

        if record_type in ["A", "AAAA", "CNAME"]:
            data["proxied"] = proxied

        self.logger.info(f"📝 Updating DNS record: {name} -> {content}")

        record = await self._make_request("PUT", f"/zones/{zone_id}/dns_records/{record_id}", data)

        self.logger.success(f"✅ Updated {record_type} record: {name}")
        return record

    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        Delete DNS record

        Args:
            zone_id: Zone ID
            record_id: Record ID

        Returns:
            True if deleted successfully
        """
        await self._make_request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")

        self.logger.success(f"✅ Deleted DNS record: {record_id}")
        return True

    async def find_dns_record(
            self,
            zone_id: str,
            name: str,
            record_type: str = "A"
    ) -> Optional[Dict]:
        """
        Find DNS record by name and type

        Args:
            zone_id: Zone ID
            name: Record name
            record_type: Record type

        Returns:
            Record data or None if not found
        """
        records = await self.list_dns_records(zone_id, record_type)

        for record in records:
            if record.get("name") == name and record.get("type") == record_type:
                return record

        return None

    async def setup_dns_records(self, domain: str, vps_ip: str) -> List[Dict]:
        """
        Setup all necessary DNS records for PyDock deployment

        Args:
            domain: Domain name
            vps_ip: VPS IP address

        Returns:
            List of created/updated records
        """
        self.logger.info(f"🌐 Setting up DNS records for {domain} -> {vps_ip}")

        # Get zone
        zone = await self.get_zone_by_domain(domain)
        if not zone:
            raise Exception(f"Zone not found for domain: {domain}")

        zone_id = zone["id"]

        # Define subdomains to create
        subdomains = [
            {"name": domain, "type": "A"},  # Root domain
            {"name": f"www.{domain}", "type": "A"},  # WWW
            {"name": f"app.{domain}", "type": "A"},  # Web app
            {"name": f"site.{domain}", "type": "A"},  # Static site
            {"name": f"api.{domain}", "type": "A"},  # API
        ]

        created_records = []

        for subdomain in subdomains:
            name = subdomain["name"]
            record_type = subdomain["type"]

            try:
                # Check if record already exists
                existing_record = await self.find_dns_record(zone_id, name, record_type)

                if existing_record:
                    # Update existing record
                    if existing_record.get("content") != vps_ip:
                        record = await self.update_dns_record(
                            zone_id=zone_id,
                            record_id=existing_record["id"],
                            record_type=record_type,
                            name=name,
                            content=vps_ip,
                            ttl=self.settings.cloudflare_ttl,
                            proxied=self.settings.cloudflare_proxy_enabled
                        )
                        created_records.append(record)
                        self.logger.info(f"📝 Updated: {name} -> {vps_ip}")
                    else:
                        self.logger.info(f"✅ Already configured: {name} -> {vps_ip}")
                        created_records.append(existing_record)
                else:
                    # Create new record
                    record = await self.create_dns_record(
                        zone_id=zone_id,
                        record_type=record_type,
                        name=name,
                        content=vps_ip,
                        ttl=self.settings.cloudflare_ttl,
                        proxied=self.settings.cloudflare_proxy_enabled
                    )
                    created_records.append(record)

            except Exception as e:
                self.logger.error(f"❌ Failed to setup {name}: {str(e)}")
                continue

        self.logger.success(f"🎉 DNS setup completed! {len(created_records)} records configured")

        # Wait a bit for DNS propagation
        self.logger.info("⏳ Waiting for DNS propagation...")
        await asyncio.sleep(5)

        return created_records

    async def cleanup_dns_records(self, domain: str) -> bool:
        """
        Remove all PyDock-related DNS records

        Args:
            domain: Domain name

        Returns:
            True if cleanup was successful
        """
        self.logger.info(f"🧹 Cleaning up DNS records for {domain}")

        zone = await self.get_zone_by_domain(domain)
        if not zone:
            self.logger.warning(f"⚠️  Zone not found for domain: {domain}")
            return False

        zone_id = zone["id"]

        # Subdomains to clean up
        subdomains_to_remove = [
            f"app.{domain}",
            f"site.{domain}",
            f"api.{domain}"
        ]

        removed_count = 0

        for subdomain in subdomains_to_remove:
            try:
                record = await self.find_dns_record(zone_id, subdomain, "A")
                if record:
                    await self.delete_dns_record(zone_id, record["id"])
                    removed_count += 1
                    self.logger.info(f"🗑️  Removed: {subdomain}")

            except Exception as e:
                self.logger.error(f"❌ Failed to remove {subdomain}: {str(e)}")
                continue

        self.logger.success(f"✅ Cleanup completed! {removed_count} records removed")
        return True

    async def verify_dns_propagation(self, domain: str, expected_ip: str) -> Dict[str, bool]:
        """
        Verify DNS propagation for all subdomains

        Args:
            domain: Domain name
            expected_ip: Expected IP address

        Returns:
            Dictionary with propagation status for each subdomain
        """
        import socket

        subdomains = [
            domain,
            f"www.{domain}",
            f"app.{domain}",
            f"site.{domain}",
            f"api.{domain}"
        ]

        results = {}

        for subdomain in subdomains:
            try:
                resolved_ip = socket.gethostbyname(subdomain)
                results[subdomain] = (resolved_ip == expected_ip)

                if results[subdomain]:
                    self.logger.success(f"✅ {subdomain} -> {resolved_ip}")
                else:
                    self.logger.warning(f"⚠️  {subdomain} -> {resolved_ip} (expected {expected_ip})")

            except socket.gaierror:
                results[subdomain] = False
                self.logger.error(f"❌ {subdomain} -> DNS resolution failed")

        return results
import requests
import sys
import json
from datetime import datetime

class InvestmentTrackerAPITester:
    def __init__(self, base_url="https://portfoliomate-10.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.demo_assets = []
        self.demo_alerts = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_demo_creation(self):
        """Test demo data creation"""
        success, response = self.run_test(
            "Create Demo Data",
            "POST",
            "demo/create",
            200
        )
        return success

    def test_demo_login(self):
        """Test demo login"""
        success, response = self.run_test(
            "Demo Login",
            "POST",
            "auth/login",
            200,
            data={"email": "demo@inversiones.com", "password": "demo123"}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response.get('user', {}).get('user_id')
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_portfolio_summary(self):
        """Test portfolio summary"""
        success, response = self.run_test(
            "Portfolio Summary",
            "GET",
            "portfolio/summary",
            200
        )
        if success:
            required_fields = ['total_investment', 'current_value', 'total_gain_loss', 'assets_count']
            for field in required_fields:
                if field not in response:
                    print(f"   ⚠️  Missing field: {field}")
                    return False
            print(f"   Assets count: {response.get('assets_count', 0)}")
            print(f"   Total investment: ${response.get('total_investment', 0):.2f}")
        return success

    def test_portfolio_assets(self):
        """Test portfolio assets with prices"""
        success, response = self.run_test(
            "Portfolio Assets with Prices",
            "GET",
            "portfolio/assets",
            200
        )
        if success and isinstance(response, list):
            self.demo_assets = response
            print(f"   Found {len(response)} assets")
            for asset in response[:2]:  # Show first 2 assets
                asset_info = asset.get('asset', {})
                print(f"   - {asset_info.get('ticker')}: ${asset.get('current_price', 'N/A')}")
        return success

    def test_get_assets(self):
        """Test get assets"""
        success, response = self.run_test(
            "Get Assets",
            "GET",
            "assets",
            200
        )
        return success

    def test_get_alerts(self):
        """Test get alerts"""
        success, response = self.run_test(
            "Get Alerts",
            "GET",
            "alerts",
            200
        )
        if success and isinstance(response, list):
            self.demo_alerts = response
            print(f"   Found {len(response)} alerts")
        return success

    def test_alert_history(self):
        """Test alert history"""
        success, response = self.run_test(
            "Alert History",
            "GET",
            "alerts/history",
            200
        )
        return success

    def test_current_price_api(self):
        """Test current price API for specific tickers"""
        tickers = ['AAPL', 'GOOGL', 'MSFT']
        all_passed = True
        
        for ticker in tickers:
            success, response = self.run_test(
                f"Current Price - {ticker}",
                "GET",
                f"prices/{ticker}/current",
                200
            )
            if success:
                price = response.get('price')
                if price and price > 0:
                    print(f"   {ticker} price: ${price:.2f}")
                else:
                    print(f"   ⚠️  Invalid price for {ticker}: {price}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_create_asset(self):
        """Test creating a new asset"""
        asset_data = {
            "asset_type": "CEDEAR",
            "ticker": "MSFT",
            "quantity": 5,
            "avg_purchase_price": 300.0,
            "purchase_date": "2024-08-01",
            "market": "NASDAQ"
        }
        
        success, response = self.run_test(
            "Create Asset",
            "POST",
            "assets",
            200,
            data=asset_data
        )
        
        if success:
            asset_id = response.get('asset_id')
            if asset_id:
                print(f"   Created asset ID: {asset_id}")
                return asset_id
        return None

    def test_create_alert(self, asset_id):
        """Test creating an alert"""
        if not asset_id:
            print("❌ Cannot create alert - no asset ID provided")
            return False
            
        alert_data = {
            "asset_id": asset_id,
            "alert_type": "target_sell",
            "target_value": 350.0,
            "is_percentage": False
        }
        
        success, response = self.run_test(
            "Create Alert",
            "POST",
            "alerts",
            200,
            data=alert_data
        )
        
        if success:
            alert_id = response.get('alert_id')
            if alert_id:
                print(f"   Created alert ID: {alert_id}")
                return alert_id
        return None

    def test_toggle_alert(self, alert_id):
        """Test toggling alert active status"""
        if not alert_id:
            print("❌ Cannot toggle alert - no alert ID provided")
            return False
            
        success, response = self.run_test(
            "Toggle Alert (Pause)",
            "PUT",
            f"alerts/{alert_id}",
            200,
            data={"is_active": False}
        )
        
        if success:
            # Test reactivating
            success2, response2 = self.run_test(
                "Toggle Alert (Reactivate)",
                "PUT",
                f"alerts/{alert_id}",
                200,
                data={"is_active": True}
            )
            return success2
        
        return success

    def test_price_history(self):
        """Test price history endpoint"""
        success, response = self.run_test(
            "Price History - AAPL",
            "GET",
            "prices/AAPL",
            200
        )
        return success

def main():
    print("🚀 Starting Investment Tracker API Tests")
    print("=" * 60)
    
    tester = InvestmentTrackerAPITester()
    
    # Test sequence
    tests = [
        ("Demo Data Creation", tester.test_demo_creation),
        ("Demo Login", tester.test_demo_login),
        ("Auth Me", tester.test_auth_me),
        ("Portfolio Summary", tester.test_portfolio_summary),
        ("Portfolio Assets", tester.test_portfolio_assets),
        ("Get Assets", tester.test_get_assets),
        ("Get Alerts", tester.test_get_alerts),
        ("Alert History", tester.test_alert_history),
        ("Current Price API", tester.test_current_price_api),
        ("Price History", tester.test_price_history),
    ]
    
    # Run basic tests
    for test_name, test_func in tests:
        if not test_func():
            print(f"\n❌ Critical test failed: {test_name}")
            break
    
    # Test CRUD operations if basic tests pass
    if tester.tests_passed >= 8:  # Most basic tests passed
        print(f"\n🔧 Testing CRUD Operations...")
        
        # Create asset
        asset_id = tester.test_create_asset()
        
        # Create alert for the asset
        alert_id = tester.test_create_alert(asset_id)
        
        # Test alert toggle
        if alert_id:
            tester.test_toggle_alert(alert_id)
    
    # Print final results
    print(f"\n" + "=" * 60)
    print(f"📊 Final Results:")
    print(f"   Tests run: {tester.tests_run}")
    print(f"   Tests passed: {tester.tests_passed}")
    print(f"   Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    elif tester.tests_passed >= tester.tests_run * 0.8:
        print("✅ Most tests passed - minor issues detected")
        return 0
    else:
        print("❌ Multiple test failures detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())
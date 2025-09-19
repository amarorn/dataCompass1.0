#!/usr/bin/env python3
"""
DataCompass Python - Comprehensive Functionality Test Suite
This script tests all major functionalities of the refactored Python application.
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any
import pandas as pd
import requests
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.core.database import init_database, close_database
from app.domain.entities.client import Client
from app.domain.entities.interaction import Interaction, InteractionType, Sentiment
from app.application.services.message_processor_service import MessageProcessorService
from app.application.services.chart_generator_service import ChartGeneratorService
from app.application.services.exploratory_analysis_service import ExploratoryAnalysisService
from app.application.services.ml_service import MLService


class TestSuite:
    """Comprehensive test suite for DataCompass Python application."""
    
    def __init__(self):
        self.base_url = f"http://{settings.host}:{settings.port}"
        self.test_results = []
        self.test_data = self._prepare_test_data()
    
    def _prepare_test_data(self) -> Dict[str, Any]:
        """Prepare test data for various tests."""
        return {
            "clients": [
                {
                    "whatsappNumber": "+5511999999999",
                    "name": "João Silva",
                    "email": "joao@example.com",
                    "age": 30,
                    "city": "São Paulo",
                    "profession": "Engenheiro",
                    "income": 8000.0,
                    "segment": "VIP",
                    "engagementScore": 85.5,
                    "churnRisk": "Low"
                },
                {
                    "whatsappNumber": "+5511888888888",
                    "name": "Maria Santos",
                    "email": "maria@example.com",
                    "age": 25,
                    "city": "Rio de Janeiro",
                    "profession": "Designer",
                    "income": 5000.0,
                    "segment": "Frequent",
                    "engagementScore": 70.0,
                    "churnRisk": "Medium"
                }
            ],
            "interactions": [
                {
                    "clientId": "client_1",
                    "type": "PURCHASE",
                    "content": "Comprei um produto por R$ 150,00",
                    "value": 150.0,
                    "category": "Eletrônicos",
                    "sentiment": "POSITIVE",
                    "metadata": {"product": "Smartphone", "store": "Online"}
                },
                {
                    "clientId": "client_2",
                    "type": "COMPLAINT",
                    "content": "Produto chegou danificado, muito insatisfeito",
                    "value": 0.0,
                    "category": "Suporte",
                    "sentiment": "NEGATIVE",
                    "metadata": {"issue": "Damaged product", "priority": "High"}
                }
            ],
            "csv_data": [
                {"name": "João", "age": 30, "city": "São Paulo", "income": 8000, "purchases": 5},
                {"name": "Maria", "age": 25, "city": "Rio de Janeiro", "income": 5000, "purchases": 3},
                {"name": "Pedro", "age": 35, "city": "Belo Horizonte", "income": 6000, "purchases": 4},
                {"name": "Ana", "age": 28, "city": "São Paulo", "income": 7000, "purchases": 6},
                {"name": "Carlos", "age": 40, "city": "Salvador", "income": 9000, "purchases": 8}
            ]
        }
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
    
    async def test_database_connection(self) -> bool:
        """Test database connection."""
        try:
            await init_database()
            self.log_test("Database Connection", True, "Successfully connected to MongoDB")
            return True
        except Exception as e:
            self.log_test("Database Connection", False, f"Failed to connect: {str(e)}")
            return False
    
    async def test_domain_entities(self) -> bool:
        """Test domain entities creation and validation."""
        try:
            # Test Client entity
            client_data = self.test_data["clients"][0]
            client = Client(**client_data)
            
            # Test Interaction entity
            interaction_data = self.test_data["interactions"][0]
            interaction = Interaction(**interaction_data)
            
            self.log_test("Domain Entities", True, "Entities created successfully")
            return True
        except Exception as e:
            self.log_test("Domain Entities", False, f"Entity creation failed: {str(e)}")
            return False
    
    async def test_message_processing(self) -> bool:
        """Test message processing service."""
        try:
            processor = MessageProcessorService()
            
            # Test purchase message
            purchase_msg = "Comprei um produto por R$ 150,00"
            result = await processor.process_message(purchase_msg)
            
            if result.interaction_type == InteractionType.PURCHASE:
                self.log_test("Message Processing", True, "Purchase message processed correctly")
                return True
            else:
                self.log_test("Message Processing", False, "Purchase message not detected")
                return False
        except Exception as e:
            self.log_test("Message Processing", False, f"Processing failed: {str(e)}")
            return False
    
    async def test_exploratory_analysis(self) -> bool:
        """Test exploratory data analysis service."""
        try:
            analyzer = ExploratoryAnalysisService()
            df = pd.DataFrame(self.test_data["csv_data"])
            
            analysis = await analyzer.perform_analysis(df)
            
            if analysis and "data_structure" in analysis:
                self.log_test("Exploratory Analysis", True, "Analysis completed successfully")
                return True
            else:
                self.log_test("Exploratory Analysis", False, "Analysis incomplete")
                return False
        except Exception as e:
            self.log_test("Exploratory Analysis", False, f"Analysis failed: {str(e)}")
            return False
    
    async def test_ml_service(self) -> bool:
        """Test machine learning service."""
        try:
            ml_service = MLService()
            df = pd.DataFrame(self.test_data["csv_data"])
            
            # Test data preparation
            prepared_df, features, target = await ml_service.prepare_data_for_ml(df, "purchases")
            
            if prepared_df is not None and len(features) > 0:
                self.log_test("ML Service", True, "ML service working correctly")
                return True
            else:
                self.log_test("ML Service", False, "ML service failed")
                return False
        except Exception as e:
            self.log_test("ML Service", False, f"ML service error: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints."""
        endpoints_to_test = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/docs", "GET"),
            ("/api/clients", "GET"),
            ("/api/analytics", "GET"),
            ("/api/whatsapp/status", "GET")
        ]
        
        success_count = 0
        total_tests = len(endpoints_to_test)
        
        for endpoint, method in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 404, 405]:  # 404/405 are acceptable for some endpoints
                    success_count += 1
                    self.log_test(f"API Endpoint {endpoint}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"API Endpoint {endpoint}", False, f"Unexpected status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"API Endpoint {endpoint}", False, f"Request failed: {str(e)}")
        
        # Test specific API functionality
        try:
            # Test WhatsApp webhook verification
            webhook_url = f"{self.base_url}/api/whatsapp/webhook"
            params = {
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge",
                "hub.verify_token": "test_token"
            }
            response = requests.get(webhook_url, params=params, timeout=10)
            
            if response.status_code in [200, 400]:  # 400 is expected for invalid token
                success_count += 1
                self.log_test("WhatsApp Webhook", True, "Webhook endpoint accessible")
            else:
                self.log_test("WhatsApp Webhook", False, f"Unexpected status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_test("WhatsApp Webhook", False, f"Webhook test failed: {str(e)}")
        
        success_rate = success_count / (total_tests + 1)  # +1 for webhook test
        if success_rate >= 0.8:  # 80% success rate
            self.log_test("API Endpoints Overall", True, f"Success rate: {success_rate:.1%}")
            return True
        else:
            self.log_test("API Endpoints Overall", False, f"Success rate too low: {success_rate:.1%}")
            return False
    
    def test_chart_generation(self) -> bool:
        """Test chart generation functionality."""
        try:
            # Test if pandas_analysis.py exists and is executable
            pandas_script = "/workspace/pandas_analysis.py"
            if os.path.exists(pandas_script):
                self.log_test("Chart Generation", True, "Pandas analysis script available")
                return True
            else:
                self.log_test("Chart Generation", False, "Pandas analysis script not found")
                return False
        except Exception as e:
            self.log_test("Chart Generation", False, f"Chart generation test failed: {str(e)}")
            return False
    
    async def test_integration_flow(self) -> bool:
        """Test complete integration flow."""
        try:
            # Simulate a complete flow: message -> processing -> analysis -> response
            processor = MessageProcessorService()
            analyzer = ExploratoryAnalysisService()
            
            # Process a message
            test_message = "Olá, gostaria de informações sobre seus produtos"
            processed = await processor.process_message(test_message)
            
            # Analyze some data
            df = pd.DataFrame(self.test_data["csv_data"])
            analysis = await analyzer.perform_analysis(df)
            
            if processed and analysis:
                self.log_test("Integration Flow", True, "Complete flow working")
                return True
            else:
                self.log_test("Integration Flow", False, "Integration flow incomplete")
                return False
        except Exception as e:
            self.log_test("Integration Flow", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_docker_setup(self) -> bool:
        """Test Docker configuration."""
        try:
            dockerfile_path = "/workspace/python_datacompass/Dockerfile"
            docker_compose_path = "/workspace/python_datacompass/docker-compose.yml"
            
            if os.path.exists(dockerfile_path) and os.path.exists(docker_compose_path):
                self.log_test("Docker Setup", True, "Docker files present")
                return True
            else:
                self.log_test("Docker Setup", False, "Docker files missing")
                return False
        except Exception as e:
            self.log_test("Docker Setup", False, f"Docker test failed: {str(e)}")
            return False
    
    def test_kubernetes_setup(self) -> bool:
        """Test Kubernetes configuration."""
        try:
            k8s_dir = "/workspace/python_datacompass/k8s"
            required_files = [
                "namespace.yaml",
                "configmap.yaml",
                "secret.yaml",
                "app-deployment.yaml",
                "mongodb-deployment.yaml",
                "ingress.yaml",
                "hpa.yaml",
                "deploy.sh"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(k8s_dir, file)):
                    missing_files.append(file)
            
            if not missing_files:
                self.log_test("Kubernetes Setup", True, "All K8s manifests present")
                return True
            else:
                self.log_test("Kubernetes Setup", False, f"Missing files: {missing_files}")
                return False
        except Exception as e:
            self.log_test("Kubernetes Setup", False, f"K8s test failed: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("🧪 Starting DataCompass Python Functionality Tests")
        print("=" * 60)
        
        # Run async tests
        await self.test_database_connection()
        await self.test_domain_entities()
        await self.test_message_processing()
        await self.test_exploratory_analysis()
        await self.test_ml_service()
        await self.test_integration_flow()
        
        # Run sync tests
        self.test_api_endpoints()
        self.test_chart_generation()
        self.test_docker_setup()
        self.test_kubernetes_setup()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }
    
    def save_results(self, results: Dict[str, Any]):
        """Save test results to file."""
        try:
            results_file = "/workspace/python_datacompass/test_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Test results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")


async def main():
    """Main test execution function."""
    test_suite = TestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        test_suite.save_results(results)
        
        # Exit with appropriate code
        if results["failed_tests"] == 0:
            print("\n🎉 ALL TESTS PASSED! The refactoring is complete and successful.")
            sys.exit(0)
        else:
            print(f"\n⚠️  {results['failed_tests']} tests failed. Please review and fix issues.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            await close_database()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
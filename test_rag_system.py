#!/usr/bin/env python3
"""
Automated RAG system test suite.
Sends multiple test questions to exercise knowledge base coverage.
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

# Test questions covering different expertise areas
TEST_QUESTIONS = [
    # Cloud migration
    {
        "question": "I need to migrate a 200-person global team's infrastructure to the cloud. What's your approach?",
        "category": "Cloud Migration",
        "should_mention": ["migration", "users", "global", "planning"]
    },
    # SOC2 compliance
    {
        "question": "What does SOC2 Type II compliance actually require for my infrastructure?",
        "category": "SOC2 Compliance",
        "should_mention": ["compliance", "soc2", "audit", "controls"]
    },
    # Disaster recovery
    {
        "question": "How should I design a disaster recovery plan for a mission-critical system?",
        "category": "Disaster Recovery",
        "should_mention": ["disaster", "recovery", "backup", "failover", "rto", "rpo"]
    },
    # Infrastructure design
    {
        "question": "What's the best way to design infrastructure for a growing company?",
        "category": "Infrastructure Design",
        "should_mention": ["infrastructure", "design", "scalable", "growth"]
    },
    # General expertise validation
    {
        "question": "Tell me about your experience with enterprise IT systems.",
        "category": "General Experience",
        "should_mention": ["years", "experience", "enterprise", "infrastructure"]
    },
    # VMware/virtualization
    {
        "question": "We're doing a P2V migration. How should we approach it?",
        "category": "Virtualization",
        "should_mention": ["p2v", "migration", "physical", "virtual", "vmware"]
    },
    # SAP integration
    {
        "question": "How do you integrate SAP with modern cloud infrastructure?",
        "category": "SAP Integration",
        "should_mention": ["sap", "integration", "business", "erp"]
    },
]

class RAGTester:
    def __init__(self, base_url="wss://dev.cwetzel.com"):
        self.base_url = base_url
        self.results = []

    async def test_question(self, q_data):
        """Send a single test question and collect response."""
        print(f"\n📝 Testing: {q_data['category']}")
        print(f"   Q: {q_data['question']}")

        try:
            uri = f"{self.base_url}/ws/chat"
            async with websockets.connect(uri) as ws:
                # Send question
                await ws.send(json.dumps({
                    "type": "chat",
                    "payload": {
                        "messages": [{"role": "user", "content": q_data["question"]}],
                        "model": "qwen2.5-coder-14b-pscode",
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }
                }))

                response = ""
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30)
                        data = json.loads(msg)

                        if data.get("type") == "chunk":
                            chunk = data.get("data", {})
                            if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                                response += chunk["choices"][0]["delta"]["content"]
                        elif data.get("type") == "done":
                            break
                    except asyncio.TimeoutError:
                        break

                # Analyze response
                response_lower = response.lower()
                found_keywords = [kw for kw in q_data.get("should_mention", [])
                                 if kw.lower() in response_lower]

                result = {
                    "category": q_data["category"],
                    "question": q_data["question"],
                    "response_length": len(response),
                    "response_preview": response[:200] + "..." if len(response) > 200 else response,
                    "keywords_found": len(found_keywords),
                    "keywords_expected": len(q_data.get("should_mention", [])),
                    "success": len(found_keywords) >= len(q_data.get("should_mention", [])) / 2
                }

                self.results.append(result)

                status = "✅" if result["success"] else "⚠️"
                print(f"   {status} Response: {result['response_preview'][:100]}...")
                print(f"   📊 Keywords: {found_keywords}/{q_data.get('should_mention', [])}")

                return result

        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append({
                "category": q_data["category"],
                "error": str(e),
                "success": False
            })
            return None

    async def run_all_tests(self):
        """Run all test questions."""
        print(f"\n{'='*60}")
        print(f"🧪 Portfolio AI RAG System Test Suite")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"Base URL: {self.base_url}")
        print(f"Test Count: {len(TEST_QUESTIONS)}")
        print(f"{'='*60}")

        for q_data in TEST_QUESTIONS:
            await self.test_question(q_data)
            await asyncio.sleep(2)  # Rate limit

        self.print_report()

    def print_report(self):
        """Print test results summary."""
        print(f"\n{'='*60}")
        print(f"📊 Test Results Summary")
        print(f"{'='*60}")

        successful = sum(1 for r in self.results if r.get("success"))
        total = len(self.results)

        print(f"\n✅ Passed: {successful}/{total}")
        print(f"Coverage: {(successful/total)*100:.1f}%\n")

        # Category breakdown
        print("By Category:")
        for result in self.results:
            status = "✅" if result.get("success") else "⚠️" if not result.get("error") else "❌"
            kw = result.get("keywords_found", 0)
            exp = result.get("keywords_expected", 0)
            print(f"  {status} {result['category']:25} ({kw}/{exp} keywords)")

        # Detailed results for debugging
        print(f"\n{'='*60}")
        print("Detailed Results:")
        print(f"{'='*60}")

        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['category']}")
            print(f"   Response Length: {result.get('response_length', 'N/A')} chars")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            else:
                print(f"   Preview: {result['response_preview']}")

        print(f"\n{'='*60}")
        print(f"Test completed: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")

async def main():
    tester = RAGTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

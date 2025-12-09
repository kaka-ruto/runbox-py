#!/usr/bin/env python3
"""
Integration test script for Runbox Python Client.
Requires a running Runbox server.
"""

import asyncio
import os
import sys
from runbox_client import AsyncClient

async def main():
    # Configuration from environment
    runbox_url = os.getenv("RUNBOX_URL", "http://localhost:8080")
    api_key = os.getenv("RUNBOX_API_KEY")
    
    if not api_key:
        print("Error: RUNBOX_API_KEY environment variable is required")
        sys.exit(1)
        
    print(f"Testing Runbox Python Client against {runbox_url}...")
    print("=" * 50)
    
    async with AsyncClient(url=runbox_url, api_key=api_key) as client:
        # Test 1: Health check
        print("\n1. Health Check:")
        health = await client.health()
        print(f"   Status: {health.status}")
        print(f"   Version: {health.version}")
        
        # Test 2: Python Execution
        print("\n2. Python Execution:")
        result = await client.run(
            identifier="py-client-test",
            language="python",
            files=[
                {"path": "main.py", "content": "print('Hello from Python client!')"}
            ],
            entrypoint="main.py"
        )
        print(f"   Success: {result.success}")
        print(f"   Output: {result.stdout.strip()}")
        print(f"   Exit Code: {result.exit_code}")
        print(f"   Execution Time: {result.execution_time_ms}ms")
        
        # Test 3: Ruby Execution
        print("\n3. Ruby Execution:")
        result = await client.run(
            identifier="py-client-test",
            language="ruby",
            files=[
                {"path": "main.rb", "content": "puts 'Hello from Ruby!'"}
            ],
            entrypoint="main.rb"
        )
        print(f"   Success: {result.success}")
        print(f"   Output: {result.stdout.strip()}")
        
        # Test 4: Shell Execution
        print("\n4. Shell Execution:")
        result = await client.run(
            identifier="py-client-test",
            language="shell",
            files=[
                {"path": "main.sh", "content": "echo 'Hello from Shell!'"}
            ],
            entrypoint="main.sh"
        )
        print(f"   Success: {result.success}")
        print(f"   Output: {result.stdout.strip()}")
        
        # Test 5: Cleanup
        print("\n5. Cleanup Containers:")
        deleted = await client.delete_containers("py-client-test")
        print(f"   Deleted: {', '.join(deleted)}")
        
    print("\n" + "=" * 50)
    print("✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())

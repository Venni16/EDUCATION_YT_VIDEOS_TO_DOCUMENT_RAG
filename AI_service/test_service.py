"""
Test Script for the AI Service
Run this AFTER starting the server with: uvicorn app:app --reload

Usage:
  python test_service.py                          # uses default test URL
  python test_service.py <youtube_url>            # use your own URL
"""

import sys
import json
import httpx

BASE_URL = "http://localhost:8000"

# A short educational video (Python tutorial — has reliable transcripts)
DEFAULT_TEST_URL = "https://youtu.be/SqcY0GlETPk?si=CQOxIJiGyEbSx9Xc"


def test_health():
    print("\n🔍 Testing /health ...")
    r = httpx.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"✅ Health: {r.json()}")


def test_generate(url: str):
    print(f"\n🚀 Testing /generate-doc with URL:\n   {url}\n")
    print("⏳ This may take 30–120 seconds (LLM cold start + multiple inferences)...\n")

    try:
        r = httpx.post(
            f"{BASE_URL}/generate-doc",
            json={"url": url},
            timeout=300,   # 5 min timeout for slow models
        )
    except httpx.ReadTimeout:
        print("❌ Request timed out. The LLM may be slow. Try again or increase timeout.")
        return

    if r.status_code != 200:
        print(f"❌ Error {r.status_code}: {r.text}")
        return

    data = r.json()

    print("=" * 60)
    print(f"✅ SUCCESS")
    print("=" * 60)
    print(f"📌 Title       : {data['title']}")
    print(f"🆔 Video ID    : {data['video_id']}")
    print(f"🖼️  Thumbnail   : {data['thumbnail_url']}")
    print(f"📄 PDF URL     : {data['pdf_url'] or '(PDF not generated)'}")
    print(f"📝 Document    : {len(data['document'])} chars")
    print("=" * 60)

    # Save the Markdown document locally for review
    output_file = f"test_output_{data['video_id']}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data["document"])
    print(f"\n📁 Document saved to: {output_file}")

    # Print first 800 chars of the document
    print("\n── Document Preview (first 800 chars) ──────────────\n")
    print(data["document"][:800])
    print("\n...")


def test_invalid_url():
    print("\n🔍 Testing /generate-doc with invalid URL ...")
    r = httpx.post(
        f"{BASE_URL}/generate-doc",
        json={"url": "https://not-a-youtube-url.com"},
        timeout=15,
    )
    print(f"   Status: {r.status_code} (expected 400 or 422)")
    print(f"   Response: {r.json()}")
    assert r.status_code in [400, 422], "Expected error response for invalid URL"
    print("✅ Invalid URL correctly rejected")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_URL

    print("=" * 60)
    print("  YouTube → Document AI Service — Test Suite")
    print("=" * 60)

    test_health()
    test_invalid_url()
    test_generate(url)

    print("\n✅ All tests done.")

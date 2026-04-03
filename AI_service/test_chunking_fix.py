import sys
import os

# Add the project root to sys.path
project_root = r"c:\Users\Elamaran\Desktop\EDUCATION_YT_VIDEOS_TO_DOCUMENT_RAG\AI_service"
sys.path.append(project_root)

from services.processing_service import split_into_chunks

def test_chunking():
    # Create a dummy text that previously caused issues (e.g., length > chunk_size)
    # chunk_size is 500, overlap is 80
    text = "This is a sentence. " * 100 # ~2000 chars
    print(f"Testing with text length: {len(text)}")
    
    try:
        chunks = split_into_chunks(text, chunk_size=500, overlap=80)
        print(f"Success! Created {len(chunks)} chunks.")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1} length: {len(chunk)}")
            if i > 5:
                print("...")
                break
    except Exception as e:
        print(f"Failed with exception: {e}")

if __name__ == "__main__":
    test_chunking()

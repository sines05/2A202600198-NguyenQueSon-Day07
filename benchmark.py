"""
Benchmark script for Group Lab — Day 7
Strategy: SentenceChunker(max_sentences_per_chunk=6)
Embedding: OpenAI text-embedding-3-large

Usage:
    python benchmark.py
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"), override=True)

from src.chunking import SentenceChunker, ChunkingStrategyComparator
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent
from src.embeddings import OpenAIEmbedder


# ── Config ──────────────────────────────────────────────────────────────
STRATEGY = SentenceChunker(max_sentences_per_chunk=6)
STRATEGY_NAME = "SentenceChunker(max_sentences=6)"

FILES = [
    ("data/65_CNTT.md", {"category": "CNTT", "type": "luat", "doc_name": "Luật CNTT"}),
    ("data/71_CNCNS.md", {"category": "CNCNS", "type": "luat", "doc_name": "Luật CN CNS"}),
    ("data/91_BVDLCN.md", {"category": "DLCN", "type": "luat", "doc_name": "Luật BV DLCN"}),
    ("data/125_NDKH.md", {"category": "NDKH", "type": "nghi_dinh", "doc_name": "NĐ Khoa học"}),
    ("data/134_TTNT.md", {"category": "TTNT", "type": "luat", "doc_name": "Luật TTNT"}),
]

BENCHMARK_QUERIES = [
    {
        "author": "Nguyễn Quốc Khánh",
        "query": "Việc xử lý dữ liệu cá nhân của trẻ em từ đủ 07 tuổi trở lên cần lưu ý gì?",
        "gold_answer": "Việc xử lý dữ liệu cá nhân của trẻ em nhằm công bố, tiết lộ thông tin về đời sống riêng tư, bí mật cá nhân của trẻ em từ đủ 07 tuổi trở lên thì phải có sự đồng ý của trẻ em và người đại diện theo pháp luật.",
    },
    {
        "author": "Lê Huy Hồng Nhật",
        "query": "Tỷ lệ trích tối thiểu từ nguồn thu học phí của các cơ sở giáo dục đại học để phục vụ hoạt động khoa học, công nghệ và đổi mới sáng tạo được quy định như thế nào?",
        "gold_answer": "Cơ sở giáo dục đại học thực hiện trích từ nguồn thu học phí với tỷ lệ tối thiểu 8% đối với đại học và 5% đối với cơ sở giáo dục đại học khác để phục vụ hoạt động khoa học, công nghệ và đổi mới sáng tạo.",
    },
    {
        "author": "Nguyễn Quế Sơn",
        "query": "Công ty tôi đang có kế hoạch đầu tư một nhà máy sản xuất sản phẩm nằm trong Danh mục sản phẩm công nghệ chiến lược. Theo quy định mới nhất, dự án này của chúng tôi sẽ được hưởng những ưu đãi đặc biệt gì về đầu tư?",
        "gold_answer": "Theo điểm a khoản 3 Điều 16, dự án đầu tư sản xuất sản phẩm công nghệ chiến lược thuộc Danh mục sản phẩm công nghệ chiến lược được hưởng chính sách ưu đãi, hỗ trợ đầu tư đặc biệt theo quy định của pháp luật về đầu tư. Ngoài ra, doanh nghiệp này còn được hưởng các mức ưu đãi, hỗ trợ cao nhất về thuế, đất đai và các chính sách khác có liên quan.",
    },
    {
        "author": "Nguyễn Tuấn Khải",
        "query": "Doanh nghiệp khởi nghiệp sáng tạo trong lĩnh vực trí tuệ nhân tạo được Nhà nước hỗ trợ những gì?",
        "gold_answer": "Doanh nghiệp khởi nghiệp sáng tạo trong lĩnh vực trí tuệ nhân tạo được Nhà nước hỗ trợ chi phí đánh giá sự phù hợp, cung cấp miễn phí hồ sơ mẫu, công cụ tự đánh giá, đào tạo và tư vấn. Được ưu tiên hỗ trợ từ Quỹ Phát triển trí tuệ nhân tạo quốc gia. Được hỗ trợ thông qua phiếu hỗ trợ để sử dụng hạ tầng tính toán, dữ liệu dùng chung, mô hình ngôn ngữ lớn, nền tảng huấn luyện, kiểm thử và dịch vụ tư vấn kỹ thuật.",
    },
    {
        "author": "Phan Văn Tấn",
        "query": "Khi tiến hành hoạt động phát thanh và truyền hình trên môi trường mạng, các tổ chức, cá nhân bắt buộc phải tuân thủ những quy định của các loại pháp luật nào?",
        "gold_answer": "Phải thực hiện các quy định của pháp luật về viễn thông, pháp luật về báo chí, và các quy định của Luật Công nghệ thông tin (Khoản 3, Điều 13).",
    },
    {
        "author": "Lê Công Thành",
        "query": "Một công ty công nghệ nước ngoài cung cấp dịch vụ quản lý dữ liệu số phục vụ riêng cho hoạt động cơ yếu để bảo vệ bí mật nhà nước tại Việt Nam. Công ty này có thuộc đối tượng áp dụng và phạm vi điều chỉnh của Luật này không?",
        "gold_answer": "Công ty công nghệ nước ngoài trong tình huống này không thuộc phạm vi điều chỉnh của Luật Công nghiệp công nghệ số đối với hoạt động cụ thể đó.",
    },
]


def demo_llm(prompt: str) -> str:
    """Mock LLM — returns the prompt preview as answer."""
    preview = prompt[:500].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


# ── Main ────────────────────────────────────────────────────────────────
def main() -> None:
    # 1. Init embedder
    embedder = OpenAIEmbedder(model_name="text-embedding-3-large")
    print(f"✅ Embedder: {embedder._backend_name}")

    # 2. Baseline comparison on 3 docs
    print("\n" + "=" * 80)
    print("PHASE 1: BASELINE CHUNKING COMPARISON")
    print("=" * 80)

    comparator = ChunkingStrategyComparator()
    baseline_files = ["data/65_CNTT.md", "data/134_TTNT.md", "data/91_BVDLCN.md"]
    for fpath in baseline_files:
        text = Path(fpath).read_text(encoding="utf-8")
        print(f"\n--- {Path(fpath).name} ({len(text)} chars) ---")
        result = comparator.compare(text, chunk_size=500)
        for name, stats in result.items():
            print(f"  {name:15s}: count={stats['count']:3d}, avg_length={stats['avg_length']:7.1f}")

    # 3. My strategy stats
    print(f"\n--- My Strategy: {STRATEGY_NAME} ---")
    for fpath in baseline_files:
        text = Path(fpath).read_text(encoding="utf-8")
        chunks = STRATEGY.chunk(text)
        count = len(chunks)
        avg_len = sum(len(c) for c in chunks) / count if count else 0
        print(f"  {Path(fpath).name:20s}: count={count:3d}, avg_length={avg_len:7.1f}")

    # 4. Load & embed all documents
    print("\n" + "=" * 80)
    print("PHASE 2: LOADING & EMBEDDING DOCUMENTS")
    print("=" * 80)

    docs: list[Document] = []
    for fpath, meta in FILES:
        text = Path(fpath).read_text(encoding="utf-8")
        chunks = STRATEGY.chunk(text)
        for i, chunk in enumerate(chunks):
            doc_id = f"{Path(fpath).stem}_chunk{i}"
            docs.append(
                Document(
                    id=doc_id,
                    content=chunk,
                    metadata={**meta, "doc_id": Path(fpath).stem, "chunk_index": i},
                )
            )
    print(f"Total chunks: {len(docs)}")
    print("Embedding all chunks (this may take a moment)...")

    store = EmbeddingStore(collection_name="benchmark", embedding_fn=embedder)
    store.add_documents(docs)
    print(f"✅ Store size: {store.get_collection_size()}")

    # 5. Run benchmark queries
    print("\n" + "=" * 80)
    print("PHASE 3: BENCHMARK QUERIES")
    print("=" * 80)

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    for qi, bq in enumerate(BENCHMARK_QUERIES, 1):
        q = bq["query"]
        results = store.search(q, top_k=3)
        print(f"\n{'─' * 80}")
        print(f"Query {qi} ({bq['author']}): {q}")
        print(f"Gold: {bq['gold_answer']}")
        print(f"{'─' * 40}")
        for i, r in enumerate(results, 1):
            content = r["content"].replace(chr(10), " ")
            print(
                f"  [{i}] score={r['score']:.4f} | {r['metadata']['doc_name']} "
                f"| chunk#{r['metadata']['chunk_index']}"
            )
            print(f"      {content}")
            print()

        # Agent answer
        agent_answer = agent.answer(q, top_k=3)
        print(f"  Agent Answer:")
        print(f"      {agent_answer}")
        print()

    # 6. Test metadata filter
    print("\n" + "=" * 80)
    print("PHASE 4: METADATA FILTER TEST")
    print("=" * 80)

    q_filter = BENCHMARK_QUERIES[0]["query"]  # DLCN query
    print(f"\nQuery: {q_filter}")
    print("\n--- Without filter ---")
    for i, r in enumerate(store.search(q_filter, top_k=3), 1):
        print(f"  [{i}] score={r['score']:.4f} | {r['metadata']['doc_name']}")

    print("\n--- With filter: category=DLCN ---")
    for i, r in enumerate(
        store.search_with_filter(q_filter, top_k=3, metadata_filter={"category": "DLCN"}), 1
    ):
        print(f"  [{i}] score={r['score']:.4f} | {r['metadata']['doc_name']}")

    print("\n" + "=" * 80)
    print("✅ BENCHMARK COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()

Lĩnh — Setup & Chạy Eval

- Cài môi trường, điền .env, chạy preflight cho đến khi pass
- Chạy baseline (v0) và đọc file JSON kết quả để tìm lỗi
- Chạy các version tiếp theo (v1, v2, v3) sau khi B/C đưa ra thay đổi
- Chạy group eval và extension eval
- Parse run log ra CSV bằng scripts/parse_runs.py

Trung — Tối ưu Prompt & Tool Declaration

- Phụ trách artifacts/system_prompt.md
- Đọc failure từ run v0, đặt giả thuyết, sửa từng thứ một
- Dẫn dắt 3 vòng tối ưu — mỗi version một giả thuyết
- Điền artifacts/version_log.csv sau mỗ

Bách — Viết Tool Mới + Eval Cases

- Viết 1 tool mới bắt buộc (tools/<name>/tool.py + TOOL.md, đăng ký vào tools/__init__.py và tools.yaml)
- Viết 10 eval case vào data/eval_group.json (5 single-turn, 5 multi-turn)
- Chạy chat.py để lấy transcript trực tường, request thiếu thông tin, requestgửi Telegram)
- Viết artifacts/REPORT.md cuối buổi dựa trên log thật
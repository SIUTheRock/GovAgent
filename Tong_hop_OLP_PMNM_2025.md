# TỔNG HỢP THÔNG TIN CUỘC THI OLP PHẦN MỀM NGUỒN MỞ 2025

## 1. Thông tin chung
- **Cơ quan tổ chức:** Hội Tin học Việt Nam.
- **Đơn vị thường trực:** Câu lạc bộ Phần mềm tự do nguồn mở Việt Nam (VFOSSA).
- **Hình thức thi:** Lập trình Hackathon theo đội (tối đa 3 sinh viên + 1 giảng viên hướng dẫn).
- **Chủ đề 2025:** "Ứng dụng dữ liệu mở liên kết phục vụ chuyển đổi số".

## 2. Yêu cầu kỹ thuật & Công nghệ trọng tâm
- **Sản phẩm:** Hệ thống chạy thực tế trên Internet (Web hoặc Mobile).
- **Công nghệ dữ liệu:** - Web ngữ nghĩa (Semantic Web).
    - Ngôn ngữ truy vấn và định dạng: SPARQL, RDF/XML, JSON-LD, Ontology.
- **Mã nguồn:** Phải công khai trên Internet (GitHub/GitLab) và có lịch sử commit thực tế.

## 3. Hệ thống tiêu chí chấm điểm (Tổng 100 điểm)

### PHẦN I: Tiêu chí dựa trên PoF (50 điểm - Đội thi tự chấm/BTC kiểm tra)
Phần này tập trung vào quy chuẩn nguồn mở. Sai sót ở đây dẫn đến trừ điểm rất nặng.

| STT | Tiêu chí | Điểm | Lưu ý quan trọng (Lỗi trừ điểm) |
|:---:|:---|:---:|:---|
| 1 | Hệ thống quản lý mã nguồn | 5 | - Phải có web viewer công khai.<br>- Không dùng thật: -5đ.<br>- Không truy cập mở: -3đ. |
| 2 | Giấy phép PMMN (OSI-approved) | 10 | - **Bắt buộc có file LICENSE toàn văn.**<br>- Giấy phép không ghi trong từng tệp: -5đ.<br>- Không tương thích giấy phép: -5đ. |
| 3 | Bản phát hành (Release) | 5 | - Phải có ít nhất 1 bản release trước khi nộp bài.<br>- Sử dụng định dạng đóng (.rar, .zip): -3đ. |
| 4 | Cài đặt, dịch từ mã nguồn | 10 | - **Phải biên dịch được từ source.**<br>- Không có hướng dẫn dịch: -5đ.<br>- Dùng công cụ nguồn đóng để dịch: -5đ. |
| 5 | Thư viện và gói đính kèm | 10 | - Minh bạch các thư viện sử dụng.<br>- Chỉnh sửa mã nguồn thư viện đính kèm: -5đ. |
| 6 | Tài liệu và giao tiếp | 10 | - Phải có README, Changelog và Bug tracker.<br>- Thiếu README/Changelog/Bug tracker: mỗi mục -5đ. |

### PHẦN II: Tiêu chí sản phẩm (50 điểm - Chấm tại Chung kết)
| STT | Tiêu chí | Điểm | Nội dung đánh giá |
|:---:|:---|:---:|:---|
| 7 | Tính nguyên gốc | 10 | Sự sáng tạo của giải pháp kỹ thuật. |
| 8 | Mức độ hoàn thiện | 10 | Kết quả chạy trình diễn sản phẩm. |
| 9 | Mức độ thân thiện (UI/UX) | 10 | Tiện ích đối với người dùng cuối. |
| 10 | Phát triển bền vững | 10 | Tài liệu kỹ thuật, cấu trúc mã nguồn sạch, khả năng mở rộng. |
| 11 | Phong cách trình diễn | 10 | Khả năng thu hút cộng đồng và Showcase. |

## 4. Những lưu ý "Sống còn" để đạt giải cao
1. **Dữ liệu mở liên kết:** Đây là linh hồn của đề bài. Sản phẩm phải thể hiện được việc kết nối các nguồn dữ liệu mở, sử dụng các tiêu chuẩn RDF/JSON-LD.
2. **Hồ sơ năng lực trên Git:** Đừng push code 1 lần duy nhất vào ngày cuối. Ban giám khảo nhìn vào lịch sử commit để đánh giá quá trình làm việc của đội.
3. **Tính thực tiễn:** Một sản phẩm nhỏ nhưng hoàn thiện, giải quyết tốt một bài toán cụ thể sẽ có điểm cao hơn một dự án khổng lồ nhưng đầy lỗi.
4. **Tài liệu hướng dẫn:** Giám khảo sẽ tự tay build thử. Nếu không có file hướng dẫn (README) hoặc script tự động (Docker/Makefile), đội thi sẽ bị mất điểm rất nặng ở phần PoF.
5. **Checklist trước khi nộp:**
    - Kiểm tra Repo đã để chế độ Public chưa.
    - Có file LICENSE chưa.
    - Có bản Release v1.0 chưa.
    - Đã có file CHANGELOG chưa.
    - Link demo có hoạt động ổn định không.

---
*Tổng hợp dựa trên Thể lệ OLP 2025 và Hướng dẫn của VFOSSA.*

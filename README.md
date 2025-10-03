# 📚 Text Story Reader - Phân Tích Kỹ Thuật

Dự án xây dựng một ứng dụng đọc truyện text **đa nền tảng** sử dụng **Python** và **Kivy**, được thiết kế để xử lý hiệu quả các tệp văn bản lớn. README này trình bày các quyết định kỹ thuật, giải pháp tối ưu hóa hiệu suất và các vấn đề tồn đọng.

-----

## 1\. 💡 Giới Thiệu và Tính Năng

### 1.1. Mục Tiêu Dự Án

Mục tiêu chính là tạo ra một trình đọc text **gọn nhẹ**, cung cấp **trải nghiệm đọc linh hoạt** trên nhiều thiết bị, với trọng tâm ban đầu là xử lý các tệp **`.txt`** và mở rộng sang các định dạng phức tạp hơn như `.html`, `.prc`, và `.epub`.

### 1.2. Các Tính Năng Đã Triển Khai

Ứng dụng hiện tại đã có các chức năng sau:

  * **Đọc tệp tin:** Hỗ trợ đọc tệp **`.txt`** cơ bản. Bao gồm cả file txt lớn.
  * **Tùy chỉnh hiển thị:** Cho phép người dùng tùy chỉnh giao diện đọc theo thời gian thực:
      * **Kích cỡ** và **Font chữ**.
      * **Màu chữ** và **Màu nền** .
  * **Quản lý trang:** Thực hiện cơ chế **chia trang logic** (Paging) dựa trên nội dung, không phải cuộn liên tục (Scrolling).

-----

## 2\. 💻 Công Nghệ và Cài Đặt

### 2.1. Công Nghệ Cốt Lõi

| Lĩnh vực | Công nghệ | Chi tiết |
| :--- | :--- | :--- |
| **Ngôn ngữ** | **Python 3.10.12** | Ngôn ngữ chính cho logic ứng dụng và xử lý dữ liệu. |
| **Framework UI** | **Kivy** | Framework đa nền tảng, được sử dụng để xây dựng giao diện người dùng. |

### 2.2. Cấu hình Dự án

Các dependencies của dự án được quản lý thông qua **Poetry**. Mọi cài đặt cần thiết có thể được thiết lập bằng lệnh:

```bash
poetry install
```

Sau đó, chạy ứng dụng bằng lệnh:

```bash
python main.py ( python3 main.py )
```

-----

## 3\. 🧠 Xử Lý Logic và Quy Trình Thực Hiện

### 3.1. Quy Trình Logic Tổng Quát (Text Processing Flow)

Quy trình xử lý một tệp `.txt` lớn được tối ưu hóa như sau:

1.  **Input:** Người dùng chọn tệp `.txt`.
2.  **Tokenization & Indexing:** Nội dung thô được phân tích thành các **từ** (word tokens). Ứng dụng tạo ra một mảng **Index Của Từ Bắt Đầu** (Start Word Index) để đánh dấu vị trí của trang.
3.  **Paging Calculation:** Dựa trên kích thước font, kích thước cửa sổ hiển thị (Window Size), và công thức tính toán số lượng từ tối đa trên một dòng và số dòng tối đa, ứng dụng tính toán để tính số từ hiển thị từ **vị trí bắt đầu của các trang logic**.
4.  **Render Page:** Khi người dùng bấm **Next Page/Back Page**, ứng dụng lấy **Index Bắt Đầu** của trang cần hiển thị.
5.  **Output:** Widget Kivy Text Label chỉ tải và hiển thị nội dung **từ index bắt đầu đến index kết thúc**, đảm bảo hiệu năng cao.

### 3.2. Cơ Chế Chia Trang Đã Áp Dụng

Dự án hiện đang sử dụng cơ chế **chia trang dựa trên từ (Word-based Paging)**, lưu trữ **index từ bắt đầu** để chia trang.

  * **Ưu điểm:** Đảm bảo độ chính xác cao hơn so với chia trang bằng số ký tự cố định, vì nó tính toán giới hạn dựa trên từ để tránh lỗi cắt từ và dễ tính toán khi có dấu xuống dòng.
  * **Thách thức:** Tính toán lại số từ hiển thị tối đa dựa trên **font chữ thay đổi** là 1 vấn đề khó khăn khi kích cỡ của font rất khó xác định.

-----

## 4\. 🛠 Các Vấn Đề Gặp Phải và Giải Pháp Khắc Phục

Quá trình tối ưu hóa hiệu suất hiển thị text đã trải qua nhiều giai đoạn:

| Vấn đề ban đầu | Hậu quả | Giải pháp áp dụng |
| :--- | :--- | :--- |
| **Sử dụng `ScrollView`** | Toàn bộ nội dung tệp (kể cả tệp 10MB) được nhét vào Label Widget, gây **treo UI** và **tràn bộ nhớ (OOM)**. | **Loại bỏ `ScrollView`**. Chuyển sang mô hình **Chia Trang Logic** (Paging). |
| **Chia trang Vật lý/Số Ký tự cố định** | Do font chữ và kích thước Widget thay đổi, các dòng không được điền đầy đủ số ký tự dự kiến, dẫn đến **khoảng trắng thừa lớn** và trang không tối ưu, do không tính khi có dấu xuống dòng dẫn đến hiển thị không đầy đủ. | Chuyển sang **chia trang theo Từ** (Word Token). Tính toán **Index Từ Bắt Đầu** để lưu trữ vị trí chính xác nhất. |
| **Tốc độ xử lý tệp lớn** | Việc đọc và xử lý tệp lớn trên luồng chính (Main Thread) làm ứng dụng **đóng băng** khi khởi động. | **đọc tệp, Phân tách từ (tokenization) và tạo list từ** tính toán số từ cần thiết rồi truyền cho UI, giải phóng bộ nhớ cho UI khỏi phải xử lí nặng nề |

-----

## 5\. ⚠️ Các Vấn Đề Tồn Đọng và Kế Hoạch Mở Rộng

### 5.1. Vấn Đề Kỹ Thuật Tồn Đọng

  * **Công thức tính toán:** Công thức tính **số ký tự tối đa trên một dòng** và **số dòng tối đa trên một trang** chưa đạt **tối ưu hoàn hảo** trong mọi trường hợp (đặc biệt khi chuyển đổi font). Cần tinh chỉnh thêm để đảm bảo tính toán chính xác hơn cho các font có độ rộng ký tự khác nhau.
  * **Parse HTML:** Hàm xử lý (parse) nội dung **HTML** hiện tại còn sơ khai và dễ gặp lỗi khi gặp cấu trúc HTML phức tạp.

### 5.2. Kế Hoạch Mở Rộng Định Dạng

Dự án sẽ mở rộng hỗ trợ đọc các định dạng phức tạp hơn, yêu cầu thêm các module xử lý:

  * **Hỗ trợ `.html`:** Cần tối ưu hóa hàm parse hiện tại để loại bỏ các thẻ không cần thiết và trích xuất text thuần túy một cách hiệu quả.
  * **Hỗ trợ `.prc` và `.epub`:** Cần triển khai các thư viện bên thứ ba của Python (ví dụ: `EbookLib` hoặc `lxml`) để đọc cấu trúc container và nội dung XHTML bên trong các định dạng nén này.

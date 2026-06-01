# ĐỒ ÁN CƠ SỞ DỮ LIỆU PHÂN TÁN

## Mô phỏng Distributed Page-Oriented Nested Loop Join (Customer - Orders)

## 1. Tổng quan

Đồ án xây dựng chương trình mô phỏng phép nối trong cơ sở dữ liệu phân tán giữa hai quan hệ `Customers` và `Orders`, đặt tại hai site khác nhau và giao tiếp qua mạng có độ trễ.

Mục tiêu trọng tâm là đánh giá tác động của:

- Độ trễ mạng (network latency)
- Kích thước block/page

đến thời gian thực thi phép nối trong môi trường phân tán.

## 2. Mục tiêu nghiên cứu

Hệ thống cần đáp ứng các nội dung sau:

- Mô phỏng hai site dữ liệu phân tán
- Cài đặt thuật toán **Page-Oriented Nested Loop Join**
- Mô phỏng truyền dữ liệu theo packet có độ trễ nhân tạo
- Đo và so sánh thời gian thực thi
- Phân tích quan hệ giữa hiệu năng với độ trễ và kích thước block

Biểu đồ đầu ra yêu cầu:

- **Execution Time vs Network Latency**
- **Execution Time vs Block Size**

## 3. Mô hình dữ liệu và phân bố

### 3.1 Quan hệ Customers (Site A)

- `CustomerID`
- `Name`
- `City`
- `Region`

Số dòng: **1.000**

### 3.2 Quan hệ Orders (Site B)

- `OrderID`
- `CustomerID`
- `OrderAmount`
- `OrderDate`

Số dòng: **100.000**

Thuộc tính nối: `CustomerID`.

## 4. Thuật toán mô phỏng

Thuật toán được sử dụng là **Page-Oriented Nested Loop Join**, thực hiện theo quy trình tổng quát:

1. Đọc một block từ quan hệ ngoài (`Customers`)
2. Gửi yêu cầu sang site chứa quan hệ trong (`Orders`)
3. Đối sánh `CustomerID` giữa hai quan hệ
4. Thu nhận các bộ dữ liệu thỏa điều kiện nối
5. Ghi nhận thời gian và chi phí truyền thông

Cách tiếp cận theo block giúp mô phỏng gần với xử lý theo trang trong hệ quản trị cơ sở dữ liệu.

## 5. Phân rã truy vấn và định vị dữ liệu

Truy vấn toàn cục được phân rã thành các truy vấn cục bộ tại từng site trước khi thực hiện join:

```text
C' = σ_region(Customers) tại Site A
O' = σ_order_condition(Orders) tại Site B
K  = π_CustomerID(C')
O'' = Orders ⋉ K tại Site B
Result = C' ⋈ O''
```

Trong mô phỏng hiện tại, các điều kiện chọn lọc được biểu diễn bằng hệ số selectivity. Cách biểu diễn này phù hợp với mục tiêu đánh giá chi phí vì chương trình tập trung vào số dòng, số block và số packet truyền thay vì xử lý dữ liệu thật.

Cơ chế localization giúp mỗi site chỉ xử lý phần dữ liệu liên quan trước khi truyền dữ liệu qua mạng. Site A lọc quan hệ `Customers`, Site B lọc quan hệ `Orders`, sau đó Semi-Join tiếp tục giảm lượng dữ liệu `Orders` cần gửi về Site A.

## 6. Mô phỏng mạng

Mạng được mô phỏng thông qua độ trễ cố định trên mỗi packet truyền giữa các site.

- Độ trễ mặc định: **50 ms/packet**
- Miền khảo sát: **1 ms → 200 ms**

Ý nghĩa thực nghiệm:

- Độ trễ tăng làm thời gian thực thi tăng
- Block lớn thường làm giảm số lần trao đổi, từ đó giảm overhead truyền thông

## 7. Mô hình chi phí

Tổng chi phí được mô hình hóa như sau:

```text
Total_Cost = I/O + CPU + Communication
```

Trong đó:

- `I/O`: chi phí đọc/ghi theo block
- `CPU`: chi phí so sánh và xử lý tuple
- `Communication`: chi phí truyền dữ liệu liên site

Thành phần `Communication` phụ thuộc vào:

- Số block/packet truyền
- Độ trễ mỗi packet
- Số lượt yêu cầu qua lại giữa các site

## 8. Tổ chức thư mục

```text
project-root/
├── distributed_join_simulator/  # Mã nguồn Python chính
│   ├── analysis/                # Benchmark và mô hình chi phí
│   ├── graphs/                  # Mã vẽ biểu đồ
│   ├── join_algorithms/         # Thuật toán join
│   ├── network/                 # Mô phỏng latency
│   └── simulation/              # Entry point chạy mô phỏng
├── datasets/                    # Dữ liệu đầu vào
├── graphs/                      # CSV và PNG đầu ra
├── docs/assignment/             # Đề bài, rubric, guideline
├── tests/                       # Kiểm thử
├── requirements.txt
└── README.md
```

## 9. Môi trường và cài đặt

Yêu cầu Python và các thư viện cần thiết.

Cài đặt nhanh:

```bash
pip install -r requirements.txt
```

Thư viện sử dụng chính:

- `pandas`
- `numpy`
- `matplotlib`

## 10. Thực thi chương trình

Ví dụ chạy mô phỏng:

```bash
python -m distributed_join_simulator.simulation.run_simulation
```

Trường hợp đồ án tách nhiều kịch bản thí nghiệm, chạy các script tương ứng trong `simulation/` hoặc `analysis/`.

## 11. Kết quả đầu ra kỳ vọng

Sau khi thực thi, hệ thống cung cấp:

- Thời gian thực thi theo các mức độ trễ mạng
- Thời gian thực thi theo các kích thước block
- Thống kê số lần truyền dữ liệu
- Ước lượng chi phí truyền thông
- Biểu đồ trực quan trong thư mục `graphs/`

## 12. Nhận xét học thuật dự kiến

Từ mô phỏng, có thể rút ra:

- Hiệu năng truy vấn phân tán nhạy với độ trễ mạng
- Tối ưu kích thước block giúp giảm số lượt giao tiếp
- Chi phí truyền thông thường chi phối tổng chi phí
- Semi-Join là hướng tối ưu tiềm năng để giảm dữ liệu truyền

## 13. Ý nghĩa của đồ án

Đồ án hỗ trợ củng cố các khái niệm trọng tâm của cơ sở dữ liệu phân tán:

- Phân bố và định vị dữ liệu
- Phân rã truy vấn toàn cục thành truy vấn cục bộ
- Tối ưu hóa phép nối trong môi trường liên site
- Mô hình hóa và đánh giá chi phí thực thi

Qua đó, sinh viên có thể quan sát định lượng mối quan hệ giữa kiến trúc phân tán, đặc tính mạng và hiệu năng truy vấn.

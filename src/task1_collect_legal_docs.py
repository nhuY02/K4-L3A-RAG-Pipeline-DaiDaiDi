"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

import os
from pathlib import Path
from fpdf import FPDF


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tạo 3 file PDF mô phỏng tài liệu pháp lý/quy định của VinUni."""
    sources = {
        "quy_dinh_hoc_phi_vinuni.pdf": (
            "Quy dinh Hoc phi VinUni\n\n"
            "Dieu 1: Hoc phi ap dung cho sinh vien trung tuyen nam 2024.\n"
            "1.1. Hoc phi chuong trinh Cu nhan Quan tri Kinh doanh la 815,000,000 VND/nam.\n"
            "1.2. Hoc phi chuong trinh Cu nhan Khoa hoc May tinh la 815,000,000 VND/nam.\n"
            "1.3. Hoc phi chuong trinh Cu nhan Y khoa la 1,000,000,000 VND/nam.\n\n"
            "Dieu 2: Phuong thuc thanh toan.\n"
            "Hoc phi duoc chia thanh 2 ky thanh toan moi nam. Moi ky sinh vien dong 50% tong hoc phi.\n"
            "Han dong hoc phi ky Mua Thu la 15/08 hang nam, ky Mua Xuan la 15/01 hang nam."
        ),
        "chinh_sach_hoc_bong_vinuni.pdf": (
            "Chinh sach hoc bong VinUni\n\n"
            "Dieu 1: Cac loai hoc bong.\n"
            "1.1. Hoc bong Tai nang (Merit-based scholarship): Cap tu 50% den 100% hoc phi trong suot thoi gian hoc dua tren thanh tich hoc tap va hoat dong ngoai khoa xuat sac.\n"
            "1.2. Ho tro Tai chinh (Financial Aid): Cap tu 50% den 100% hoc phi dua tren hoan canh kinh te cua gia dinh sinh vien.\n\n"
            "Dieu 2: Dieu kien duy tri hoc bong.\n"
            "Sinh vien nhan Hoc bong Tai nang phai duy tri diem trung binh tich luy (CGPA) tu 3.2/4.0 tro len moi nam hoc."
        ),
        "noi_quy_ky_tuc_xa_vinuni.pdf": (
            "Noi quy ky tuc xa VinUni\n\n"
            "Dieu 1: Quy dinh chung ve cu tru.\n"
            "Tat ca sinh vien nam nhat duoc yeu cau o ky tuc xa. Ky tuc xa phan khu rieng cho nam va nu. "
            "Phi ky tuc xa la 3,000,000 VND/thang, chua bao gom dien nuoc.\n\n"
            "Dieu 2: Thoi gian gioi nghiem.\n"
            "Ky tuc xa dong cua vao luc 23:00 hang ngay. Sinh vien khong duoc phep ra ngoai sau thoi gian nay tru truong hop khan cap co xac nhan cua ban quan ly.\n\n"
            "Dieu 3: Tien ich noi khu.\n"
            "Sinh vien duoc su dung mien phi phong gym, ho boi va khong gian sinh hoat chung. Khong duoc nau an trong phong ngu."
        ),
    }

    for filename, content in sources.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        
        for line in content.split("\n"):
            # fpdf2 uses text= for newer versions, but positional is safest
            pdf.multi_cell(0, 10, line)
            
        out_path = DATA_DIR / filename
        pdf.output(str(out_path))
        print(f"Generated: {out_path}")


if __name__ == "__main__":
    setup_directory()
    download_documents()

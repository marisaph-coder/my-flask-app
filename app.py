import os
import json
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "personal_kb_secret_key_change_this"

# ตั้งค่าโฟลเดอร์สำหรับ Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

DATA_FILE = 'data.json'

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin1234"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เข้าสู่ระบบ - Hi Marisa</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Sarabun', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-2xl">
        <div class="mb-8 text-center">
            <img src="/static/pro.jpg" alt="Profile" class="w-20 h-20 rounded-2xl object-cover border-2 border-slate-700 mx-auto mb-3">
            <h2 class="text-2xl font-bold bg-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 bg-clip-text text-transparent">Hi Marisa</h2>
            <p class="text-xs text-slate-400 mt-1.5">ระบบจัดการและเก็บบันทึกข้อมูลส่วนบุคคล</p>
        </div>
        {% if error %}
        <div class="text-rose-400 text-xs mb-5 text-center bg-rose-500/10 p-3 rounded-xl border border-rose-500/20 font-medium">{{ error }}</div>
        {% endif %}
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1.5">ชื่อผู้ใช้งาน</label>
                <input type="text" name="username" placeholder="Username" required class="w-full bg-slate-950/80 border border-slate-800 p-3 rounded-xl text-xs text-slate-100">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1.5">รหัสผ่าน</label>
                <input type="password" name="password" placeholder="Password" required class="w-full bg-slate-950/80 border border-slate-800 p-3 rounded-xl text-xs text-slate-100">
            </div>
            <button type="submit" class="w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-bold p-3 rounded-xl text-xs transition shadow-lg mt-2">เข้าสู่ระบบ</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบจัดการบันทึกข้อมูลส่วนบุคคล</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: 'Sarabun', sans-serif; }
        .scrollbar-none::-webkit-scrollbar { display: none; }
        .scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-[#0b0f19] text-slate-200 min-h-screen flex flex-col md:flex-row font-normal text-[13px] antialiased">

    <!-- Header / Sidebar Nav -->
    <aside class="w-full md:w-64 bg-[#0d121f] border-b md:border-b-0 md:border-r border-slate-800/80 p-4 flex flex-col justify-between shrink-0 sticky top-0 z-40 md:relative">
        <div>
            <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
                <div class="flex items-center gap-3">
                    <img src="/static/pro.jpg" alt="Marisa Phunphoem" class="w-10 h-10 rounded-full object-cover border border-slate-700">
                    <div class="overflow-hidden">
                        <h1 class="font-bold text-slate-100 text-xs truncate">Marisa Phunphoem</h1>
                        <p class="text-[10px] text-slate-400 truncate">ระบบจัดเก็บเอกสารส่วนตัว</p>
                    </div>
                </div>
                <a href="/logout" class="md:hidden text-[10px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-1 rounded">ออก</a>
            </div>

            <nav class="flex md:flex-col gap-1.5 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
                <a href="/" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if not selected_cat %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">🏠 รายการทั้งหมด</a>
                <a href="/?cat=🧠 บันทึกไปเรื่อย" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '🧠 บันทึกไปเรื่อย' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">🧠 บันทึกไปเรื่อย</a>
                <a href="/?cat=💼 บันทึกงาน/เก็บงาน" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '💼 บันทึกงาน/เก็บงาน' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">💼 ข้อมูลของงาน</a>
                <a href="/?cat=🌐 IP Address อุปกรณ์" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '🌐 IP Address อุปกรณ์' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">🌐 IP Address อุปกรณ์</a>
                <a href="/?cat=📜 เก็บเกียรติบัตรต่างๆ" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '📜 เก็บเกียรติบัตรต่างๆ' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">📜 เกียรติบัตรต่างๆ</a>
                <a href="/?cat=📊 ใบเกรด/เอกสารสำคัญ" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '📊 ใบเกรด/เอกสารสำคัญ' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">📊 ใบเกรด / เอกสารสำคัญ</a>
                <a href="/?cat=🚗 เอกสารผ่อนรถ" class="whitespace-nowrap flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[11px] font-semibold {% if selected_cat == '🚗 เอกสารผ่อนรถ' %}bg-indigo-600 text-white{% else %}text-slate-400 hover:bg-slate-800/50{% endif %}">🚗 เอกสารผ่อนรถ</a>
            </nav>
        </div>

        <div class="hidden md:block mt-6 pt-4 border-t border-slate-800/80">
            <a href="/logout" class="flex items-center justify-center gap-2 w-full bg-rose-500/10 text-rose-300 border border-rose-500/20 px-3 py-2 rounded-xl text-[11px]">🚪 ออกจากระบบ</a>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-4 md:p-6 max-w-7xl mx-auto w-full">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6 pb-3 border-b border-slate-800">
            <div>
                <h2 class="text-lg font-bold text-slate-100">{{ current_cat_title }}</h2>
                <p class="text-[11px] text-slate-400 mt-0.5">คลังเก็บข้อมูลและระบบจัดการเอกสารส่วนบุคคล</p>
            </div>
            <div class="bg-[#111726] border border-slate-800 px-3 py-1.5 rounded-xl text-[11px]">
                <span id="realtime-date" class="text-slate-400">--/--/----</span>
                <span id="realtime-clock" class="text-indigo-300 font-bold font-mono ml-1">00:00:00</span>
            </div>
        </div>

        {% if not selected_cat %}
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
            <a href="/?cat=🧠 บันทึกไปเรื่อย" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">🧠</span>
                <p class="text-[10px] text-slate-400 mt-1">บันทึกไปเรื่อย</p>
                <p class="text-base font-bold text-indigo-400 mt-1">{{ stats.get('🧠 บันทึกไปเรื่อย', 0) }}</p>
            </a>
            <a href="/?cat=💼 บันทึกงาน/เก็บงาน" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">💼</span>
                <p class="text-[10px] text-slate-400 mt-1">ข้อมูลของงาน</p>
                <p class="text-base font-bold text-amber-400 mt-1">{{ stats.get('💼 บันทึกงาน/เก็บงาน', 0) }}</p>
            </a>
            <a href="/?cat=🌐 IP Address อุปกรณ์" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">🌐</span>
                <p class="text-[10px] text-slate-400 mt-1">IP อุปกรณ์</p>
                <p class="text-base font-bold text-emerald-400 mt-1">{{ stats.get('🌐 IP Address อุปกรณ์', 0) }}</p>
            </a>
            <a href="/?cat=📜 เก็บเกียรติบัตรต่างๆ" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">📜</span>
                <p class="text-[10px] text-slate-400 mt-1">เกียรติบัตร</p>
                <p class="text-base font-bold text-violet-400 mt-1">{{ stats.get('📜 เก็บเกียรติบัตรต่างๆ', 0) }}</p>
            </a>
            <a href="/?cat=📊 ใบเกรด/เอกสารสำคัญ" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">📊</span>
                <p class="text-[10px] text-slate-400 mt-1">ใบเกรด/เอกสาร</p>
                <p class="text-base font-bold text-cyan-400 mt-1">{{ stats.get('📊 ใบเกรด/เอกสารสำคัญ', 0) }}</p>
            </a>
            <a href="/?cat=🚗 เอกสารผ่อนรถ" class="bg-[#111726] border border-slate-800 p-3.5 rounded-2xl text-center">
                <span class="text-2xl">🚗</span>
                <p class="text-[10px] text-slate-400 mt-1">เอกสารผ่อนรถ</p>
                <p class="text-base font-bold text-rose-400 mt-1">{{ stats.get('🚗 เอกสารผ่อนรถ', 0) }}</p>
            </a>
        </div>
        {% else %}
        <!-- Form Add -->
        <div class="bg-[#111726] border border-slate-800 p-4 rounded-2xl mb-6">
            <h3 class="text-xs font-bold text-indigo-400 mb-3">+ เพิ่มรายการใหม่ใน {{ selected_cat }}</h3>
            <form action="/add_note" method="POST" enctype="multipart/form-data" class="space-y-3">
                <input type="hidden" name="selected_cat" value="{{ selected_cat }}">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[11px] text-slate-300 mb-1">ชื่อรายการ / หัวข้อเอกสาร</label>
                        <input type="text" name="title" required class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                    </div>
                    {% if selected_cat == '💼 บันทึกงาน/เก็บงาน' %}
                    <div>
                        <label class="block text-[11px] text-slate-300 mb-1">📍 สถานที่</label>
                        <input type="text" name="location" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                    </div>
                    {% endif %}
                    {% if selected_cat == '🌐 IP Address อุปกรณ์' %}
                    <div>
                        <label class="block text-[11px] text-slate-300 mb-1">🌐 IP Address</label>
                        <input type="text" name="ip_address" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                    </div>
                    {% endif %}
                </div>
                <div>
                    <label class="block text-[11px] text-slate-300 mb-1">รายละเอียด</label>
                    <textarea name="content" rows="2" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100"></textarea>
                </div>
                <div class="bg-[#0b0f19] border border-slate-800 p-3 rounded-xl">
                    <label class="block text-[11px] text-indigo-300 mb-2">📸 รูปภาพหรือไฟล์ PDF:</label>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <label class="bg-indigo-600 text-white text-center py-2 rounded-xl text-[11px] cursor-pointer">📷 ถ่ายรูป <input type="file" name="image" accept="image/*" capture="environment" class="hidden"></label>
                        <label class="bg-slate-800 text-slate-200 text-center py-2 rounded-xl text-[11px] cursor-pointer">📁 เลือกไฟล์ <input type="file" name="image_file" accept="image/*,.pdf" class="hidden"></label>
                    </div>
                </div>
                <div class="flex justify-end">
                    <button type="submit" class="bg-indigo-600 text-white font-bold px-5 py-2 rounded-xl text-[11px]">+ บันทึก</button>
                </div>
            </form>
        </div>
        {% endif %}

        <!-- Items Display Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {% for item in items %}
            <div id="card-{{ item['id'] }}" class="bg-[#111726] border border-slate-800 rounded-2xl p-3.5 flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-semibold text-slate-100 text-xs item-title">{{ item['title'] }}</h3>
                        <span class="text-[9px] text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded item-date">{{ item['date'] }}</span>
                    </div>

                    {% if item.get('location') %}
                    <p class="text-[10px] text-amber-300 mb-2 item-loc">📍 {{ item['location'] }}</p>
                    {% endif %}

                    {% if item.get('ip_address') %}
                    <p class="text-[10px] text-emerald-300 mb-2 item-ip">🌐 {{ item['ip_address'] }}</p>
                    {% endif %}

                    {% if item['image_path'] %}
                    <div class="mb-2.5 rounded-xl overflow-hidden border border-slate-800 bg-[#0b0f19] flex items-center justify-center min-h-[120px]">
                        {% if item['image_path'].endswith('.pdf') %}
                        <div class="text-center p-3">
                            <span class="text-2xl">📄</span>
                            <p class="text-[10px] text-indigo-300 font-semibold mt-1">ไฟล์เอกสาร PDF</p>
                        </div>
                        {% else %}
                        <img id="img-{{ item['id'] }}" src="/uploads/{{ item['image_path'] }}" alt="{{ item['title'] }}" class="max-h-40 object-contain rounded-lg">
                        {% endif %}
                    </div>
                    {% endif %}

                    {% if item['content'] %}
                    <p class="text-[11px] text-slate-300 bg-[#0b0f19] p-2.5 rounded-xl border border-slate-800/80 mb-2.5 leading-relaxed whitespace-pre-line item-content">{{ item['content'] }}</p>
                    {% endif %}
                </div>

                <div class="flex justify-between items-center pt-2.5 border-t border-slate-800 mt-2">
                    <div>
                        {% if item['image_path'] %}
                        <a href="/uploads/{{ item['image_path'] }}" download class="text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-1 rounded">💾 ไฟล์</a>
                        {% endif %}
                    </div>
                    <div class="flex items-center gap-1.5">
                        <button onclick="downloadCardPDF({{ item['id'] }})" class="bg-teal-500/10 text-teal-300 border border-teal-500/20 text-[10px] px-2.5 py-1 rounded">📄 PDF</button>
                        <button onclick="openEditModal({{ item['id'] }}, `{{ item['title']|replace('`', '\\`') }}`, `{{ item.get('location', '')|replace('`', '\\`') }}`, `{{ item.get('ip_address', '')|replace('`', '\\`') }}`, `{{ item.get('content', '')|replace('`', '\\`') }}`)" class="bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[10px] px-2.5 py-1 rounded">✏️ แก้ไข</button>
                        <a href="/delete_note/{{ item['id'] }}?cat={{ selected_cat }}" onclick="return confirm('ยืนยันลบรายการนี้?')" class="bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] px-2.5 py-1 rounded">🗑️ ลบ</a>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="col-span-full text-center py-12 bg-[#111726]/40 border border-dashed border-slate-800 rounded-2xl">
                <span class="text-3xl">📁</span>
                <p class="text-[11px] text-slate-400 mt-2 font-medium">ยังไม่มีข้อมูลในหมวดหมู่นี้</p>
            </div>
            {% endfor %}
        </div>
    </main>

    <!-- Modal Edit Note -->
    <div id="editModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="bg-[#111726] border border-slate-800 p-6 rounded-3xl max-w-lg w-full shadow-2xl">
            <h3 class="text-xs font-bold text-indigo-400 mb-4">✏️ แก้ไขข้อมูลรายการ</h3>
            <form id="editForm" method="POST" enctype="multipart/form-data" class="space-y-3">
                <input type="hidden" name="selected_cat" value="{{ selected_cat }}">
                <div>
                    <label class="block text-[11px] text-slate-300 mb-1">ชื่อรายการ / หัวข้อเอกสาร</label>
                    <input type="text" id="edit_title" name="title" required class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                </div>
                <div>
                    <label class="block text-[11px] text-slate-300 mb-1">📍 สถานที่</label>
                    <input type="text" id="edit_location" name="location" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                </div>
                <div>
                    <label class="block text-[11px] text-slate-300 mb-1">🌐 IP Address</label>
                    <input type="text" id="edit_ip_address" name="ip_address" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100">
                </div>
                <div>
                    <label class="block text-[11px] text-slate-300 mb-1">รายละเอียดเพิ่มเติม</label>
                    <textarea id="edit_content" name="content" rows="3" class="w-full bg-[#0b0f19] border border-slate-800 p-2.5 rounded-xl text-[11px] text-slate-100"></textarea>
                </div>
                <div class="bg-[#0b0f19] border border-slate-800 p-3 rounded-xl">
                    <label class="block text-[11px] text-indigo-300 mb-1">🖼️ เปลี่ยนรูปภาพหรือไฟล์:</label>
                    <input type="file" name="image_file" accept="image/*,.pdf" class="w-full text-[10px] text-slate-400">
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeEditModal()" class="bg-slate-800 text-slate-300 px-4 py-2 rounded-xl text-[11px]">ยกเลิก</button>
                    <button type="submit" class="bg-indigo-600 text-white font-semibold px-5 py-2 rounded-xl text-[11px]">บันทึก</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const day = String(now.getDate()).padStart(2, '0');
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const year = now.getFullYear() + 543;
            document.getElementById('realtime-date').innerText = `${day}/${month}/${year}`;

            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('realtime-clock').innerText = `${hours}:${minutes}:${seconds}`;
        }
        setInterval(updateClock, 1000);
        updateClock();

        function openEditModal(id, title, location, ip_address, content) {
            document.getElementById('editForm').action = '/edit_note/' + id;
            document.getElementById('edit_title').value = title;
            document.getElementById('edit_location').value = location;
            document.getElementById('edit_ip_address').value = ip_address;
            document.getElementById('edit_content').value = content;
            document.getElementById('editModal').classList.remove('hidden');
        }

        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        function getBase64Image(imgUrl) {
            return new Promise((resolve) => {
                if (!imgUrl) return resolve(null);
                const img = new Image();
                img.crossOrigin = 'Anonymous';
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/jpeg'));
                };
                img.onerror = () => resolve(null);
                img.src = imgUrl;
            });
        }

        async function downloadCardPDF(itemId) {
            const card = document.getElementById('card-' + itemId);
            if (!card) return;

            const title = card.querySelector('.item-title')?.innerText || 'บันทึก';
            const date = card.querySelector('.item-date')?.innerText || '';
            const loc = card.querySelector('.item-loc')?.innerText || '';
            const ip = card.querySelector('.item-ip')?.innerText || '';
            const content = card.querySelector('.item-content')?.innerText || '';
            const imgEl = document.getElementById('img-' + itemId);

            let base64Img = null;
            if (imgEl && imgEl.src) {
                base64Img = await getBase64Image(imgEl.src);
            }

            // ซ่อน Element สำหรับสร้าง PDF นอกขอบเขตหน้าจอ
            const container = document.createElement('div');
            container.style.position = 'absolute';
            container.style.left = '-9999px';
            container.style.top = '0';
            container.style.width = '700px';
            container.style.backgroundColor = '#ffffff';
            container.style.color = '#000000';
            container.style.padding = '30px';
            container.style.boxSizing = 'border-box';
            container.style.fontFamily = "'Sarabun', sans-serif";

            let html = `
                <div style="border-bottom: 2px solid #4f46e5; padding-bottom: 10px; margin-bottom: 15px;">
                    <h2 style="font-size: 20px; font-weight: bold; color: #1e1b4b; margin: 0 0 5px 0;">${title}</h2>
                    <span style="font-size: 11px; color: #64748b;">วันที่บันทึก: ${date}</span>
                </div>
            `;

            if (loc) {
                html += `<div style="font-size: 13px; color: #b45309; font-weight: bold; margin-bottom: 8px;">${loc}</div>`;
            }

            if (ip) {
                html += `<div style="font-size: 13px; color: #047857; font-weight: bold; font-family: monospace; margin-bottom: 8px;">${ip}</div>`;
            }

            if (base64Img) {
                html += `
                    <div style="text-align: center; margin: 15px 0;">
                        <img src="${base64Img}" style="max-width: 100%; max-height: 400px; border-radius: 6px; border: 1px solid #e2e8f0;">
                    </div>
                `;
            }

            if (content) {
                html += `
                    <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 15px; border-radius: 8px; font-size: 13px; color: #1e293b; white-space: pre-line; line-height: 1.6; margin-top: 15px;">
                        ${content}
                    </div>
                `;
            }

            html += `
                <div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-size: 10px; color: #94a3b8; text-align: right;">
                    เอกสารบันทึกส่วนบุคคล - Hi Marisa
                </div>
            `;

            container.innerHTML = html;
            document.body.appendChild(container);

            const opt = {
                margin:       0.3,
                filename:     `บันทึก_${itemId}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true, logging: false },
                jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
            };

            try {
                await html2pdf().set(opt).from(container).save();
            } catch (err) {
                console.error('PDF Export Error:', err);
            } finally {
                if (document.body.contains(container)) {
                    document.body.removeChild(container);
                }
            }
        }
    </script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        error = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_folder, filename)

@app.route('/')
@requires_auth
def index():
    search_query = request.args.get('search', '').strip().lower()
    selected_cat = request.args.get('cat', '').strip()

    all_data = load_data()
    filtered_data = []

    stats = {}
    for item in all_data:
        cat = item.get('category', 'ทั่วไป')
        stats[cat] = stats.get(cat, 0) + 1

    for item in all_data:
        if selected_cat and item.get('category') != selected_cat:
            continue
        
        if search_query:
            in_title = search_query in item.get('title', '').lower()
            in_content = search_query in item.get('content', '').lower()
            in_location = search_query in item.get('location', '').lower()
            in_ip = search_query in item.get('ip_address', '').lower()
            if not (in_title or in_content or in_location or in_ip):
                continue
                
        filtered_data.append(item)

    filtered_data.reverse()
    current_cat_title = selected_cat if selected_cat else "🏠 รายการทั้งหมด (Dashboard)"

    return render_template_string(
        DASHBOARD_TEMPLATE, 
        items=filtered_data, 
        search_query=search_query, 
        selected_cat=selected_cat,
        current_cat_title=current_cat_title,
        stats=stats
    )

@app.route('/add_note', methods=['POST'])
@requires_auth
def add_note():
    title = request.form.get('title')
    location = request.form.get('location', '').strip()
    ip_address = request.form.get('ip_address', '').strip()
    selected_cat = request.form.get('selected_cat', '').strip()
    
    category = selected_cat if selected_cat else "🧠 บันทึกไปเรื่อย"
    content = request.form.get('content', '')
    
    filename = None
    file = request.files.get('image') or request.files.get('image_file')
    if file and file.filename != '' and allowed_file(file.filename):
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if title:
        all_data = load_data()
        new_id = int(datetime.now().timestamp() * 1000)
        
        new_item = {
            "id": new_id,
            "title": title,
            "location": location,
            "ip_address": ip_address,
            "category": category,
            "content": content,
            "image_path": filename,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        all_data.append(new_item)
        save_data(all_data)

    return redirect(url_for('index', cat=selected_cat))

@app.route('/edit_note/<int:note_id>', methods=['POST'])
@requires_auth
def edit_note(note_id):
    selected_cat = request.form.get('selected_cat', '').strip()
    title = request.form.get('title')
    location = request.form.get('location', '').strip()
    ip_address = request.form.get('ip_address', '').strip()
    content = request.form.get('content', '')

    all_data = load_data()
    for item in all_data:
        if item.get('id') == note_id:
            item['title'] = title
            item['location'] = location
            item['ip_address'] = ip_address
            item['content'] = content

            file = request.files.get('image_file')
            if file and file.filename != '' and allowed_file(file.filename):
                if item.get('image_path'):
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], item['image_path'])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                new_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                item['image_path'] = new_filename
            break

    save_data(all_data)
    return redirect(url_for('index', cat=selected_cat))

@app.route('/delete_note/<int:note_id>')
@requires_auth
def delete_note(note_id):
    selected_cat = request.args.get('cat', '')
    all_data = load_data()
    
    updated_data = []
    for item in all_data:
        if item.get('id') == note_id:
            if item.get('image_path'):
                image_full_path = os.path.join(app.config['UPLOAD_FOLDER'], item['image_path'])
                if os.path.exists(image_full_path):
                    os.remove(image_full_path)
        else:
            updated_data.append(item)

    save_data(updated_data)
    return redirect(url_for('index', cat=selected_cat))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
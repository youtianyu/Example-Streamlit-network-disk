import streamlit as st
import os
import shutil
import zipfile
import io
import json
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import hashlib
import base64
import math

# 设置页面配置
st.set_page_config(
    page_title="文件存储系统",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化secrets配置
if 'secrets' not in st.session_state:
    st.session_state.secrets = st.secrets
    

# 初始化session_state
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'password' not in st.session_state:
    st.session_state.password = ""
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'current_path' not in st.session_state:
    st.session_state.current_path = ""
if 'language' not in st.session_state:
    st.session_state.language = "中文"
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'current_folder' not in st.session_state:
    st.session_state.current_folder = ""

# 多语言支持
def get_text(key):
    texts = {
        "中文": {
            "login_title": "欢迎使用文件存储系统",
            "username": "用户名",
            "password": "密码",
            "login": "登录",
            "register": "注册",
            "register_success": "注册成功！",
            "register_fail": "注册失败，用户已存在或达到最大用户数！",
            "login_success": "登录成功！",
            "login_fail": "登录失败，用户名或密码错误！",
            "file_manager": "文件管理器",
            "upload_file": "上传文件",
            "create_folder": "创建文件夹",
            "folder_name": "文件夹名称",
            "create": "创建",
            "delete": "删除",
            "download": "下载",
            "preview": "预览",
            "back": "返回上级",
            "settings": "设置",
            "logout": "退出登录",
            "change_password": "修改密码",
            "change_username": "修改用户名",
            "change_language": "修改语言",
            "old_password": "旧密码",
            "new_password": "新密码",
            "confirm_password": "确认密码",
            "new_username": "新用户名",
            "save": "保存",
            "admin_panel": "管理员面板",
            "user_stats": "用户统计",
            "storage_stats": "存储统计",
            "clean_inactive": "清理不活跃用户",
            "days_inactive": "不活跃天数",
            "clean": "清理",
            "download_all": "打包下载",
            "file_size_limit": "文件大小超出限制！",
            "folder_created": "文件夹创建成功！",
            "folder_exists": "文件夹已存在！",
            "file_uploaded": "文件上传成功！",
            "file_deleted": "文件删除成功！",
            "folder_deleted": "文件夹删除成功！",
            "password_changed": "密码修改成功！",
            "username_changed": "用户名修改成功！",
            "password_mismatch": "两次输入的密码不一致！",
            "old_password_wrong": "旧密码错误！",
            "username_exists": "用户名已存在！",
            "users_cleaned": "不活跃用户已清理！",
            "no_users_cleaned": "没有不活跃用户需要清理！",
            "analysis": "数据分析"
        },
        "English": {
            "login_title": "Welcome to File Storage System",
            "username": "Username",
            "password": "Password",
            "login": "Login",
            "register": "Register",
            "register_success": "Registration successful!",
            "register_fail": "Registration failed, user already exists or maximum user limit reached!",
            "login_success": "Login successful!",
            "login_fail": "Login failed, incorrect username or password!",
            "file_manager": "File Manager",
            "upload_file": "Upload File",
            "create_folder": "Create Folder",
            "folder_name": "Folder Name",
            "create": "Create",
            "delete": "Delete",
            "download": "Download",
            "preview": "Preview",
            "back": "Back",
            "settings": "Settings",
            "logout": "Logout",
            "change_password": "Change Password",
            "change_username": "Change Username",
            "change_language": "Change Language",
            "old_password": "Old Password",
            "new_password": "New Password",
            "confirm_password": "Confirm Password",
            "new_username": "New Username",
            "save": "Save",
            "admin_panel": "Admin Panel",
            "user_stats": "User Statistics",
            "storage_stats": "Storage Statistics",
            "clean_inactive": "Clean Inactive Users",
            "days_inactive": "Days Inactive",
            "clean": "Clean",
            "download_all": "Download All",
            "file_size_limit": "File size exceeds limit!",
            "folder_created": "Folder created successfully!",
            "folder_exists": "Folder already exists!",
            "file_uploaded": "File uploaded successfully!",
            "file_deleted": "File deleted successfully!",
            "folder_deleted": "Folder deleted successfully!",
            "password_changed": "Password changed successfully!",
            "username_changed": "Username changed successfully!",
            "password_mismatch": "Passwords do not match!",
            "old_password_wrong": "Old password is incorrect!",
            "username_exists": "Username already exists!",
            "users_cleaned": "Inactive users cleaned!",
            "no_users_cleaned": "No inactive users to clean!",
            "analysis": "Data Analysis"
        }
    }
    return texts[st.session_state.language][key]

# 创建必要的目录
def ensure_directories():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # 创建管理员目录
    admin_dir = os.path.join("data", st.session_state.secrets["administrator"]["name"])
    admin_pass_dir = os.path.join(admin_dir, st.session_state.secrets["administrator"]["password"])
    
    if not os.path.exists(admin_dir):
        os.makedirs(admin_dir)
    if not os.path.exists(admin_pass_dir):
        os.makedirs(admin_pass_dir)

# 加载用户信息
def load_users():
    users = {}
    if os.path.exists("data"):
        for username in os.listdir("data"):
            user_dir = os.path.join("data", username)
            if os.path.isdir(user_dir):
                for password in os.listdir(user_dir):
                    pass_dir = os.path.join(user_dir, password)
                    if os.path.isdir(pass_dir):
                        # 获取最后修改时间作为最后活跃时间
                        last_active = os.path.getmtime(pass_dir)
                        users[username] = {
                            "password": password,
                            "last_active": last_active
                        }
    return users

# 计算文件夹大小
def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

# 获取文件大小的可读形式
def get_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = int(math.log(size_bytes, 1024))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# 哈希密码
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 登录页面
def login_page():
    st.session_state.users = load_users()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title(get_text("login_title"), anchor=False)
        
        with st.form("login_form"):
            username = st.text_input(get_text("username"))
            password = st.text_input(get_text("password"), type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button(get_text("login"), use_container_width=True)
            with col2:
                if st.session_state.secrets["login"]["enroll_enable"] and len(st.session_state.users) < st.session_state.secrets["login"]["enroll_max_num"]:
                    register_button = st.form_submit_button(get_text("register"), use_container_width=True)
                else:
                    register_button = False
        
        if login_button and username and password:
            # 检查是否是管理员
            if username == st.session_state.secrets["administrator"]["name"] and password == st.session_state.secrets["administrator"]["password"]:
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.is_admin = True
                st.session_state.page = "file_manager"
                st.session_state.current_path = os.path.join("data", username, password)
                st.success(get_text("login_success"))
                st.rerun()
            # 检查普通用户
            elif username in st.session_state.users and st.session_state.users[username]["password"] == password:
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.is_admin = False
                st.session_state.page = "file_manager"
                st.session_state.current_path = os.path.join("data", username, password)
                
                # 更新最后活跃时间
                user_dir = os.path.join("data", username, password)
                if os.path.exists(user_dir):
                    # 创建或更新一个.last_active文件来更新文件夹的修改时间
                    with open(os.path.join(user_dir, ".last_active"), "w") as f:
                        f.write(str(time.time()))
                
                st.success(get_text("login_success"))
                st.rerun()
            else:
                st.error(get_text("login_fail"))
        
        if register_button and username and password:
            if username in st.session_state.users:
                st.error(get_text("register_fail"))
            else:
                # 创建用户目录
                user_dir = os.path.join("data", username)
                pass_dir = os.path.join(user_dir, password)
                
                if not os.path.exists(user_dir):
                    os.makedirs(user_dir)
                if not os.path.exists(pass_dir):
                    os.makedirs(pass_dir)
                
                # 更新用户列表
                st.session_state.users[username] = {
                    "password": password,
                    "last_active": time.time()
                }
                
                st.success(get_text("register_success"))

# 文件管理器页面
def file_manager_page():
    # 确保当前路径存在
    if not os.path.exists(st.session_state.current_path):
        os.makedirs(st.session_state.current_path)
    
    # 侧边栏
    with st.sidebar:
        st.title(get_text("file_manager"))
        
        # 创建文件夹
        with st.expander(get_text("create_folder"), expanded=False):
            with st.form("create_folder_form"):
                folder_name = st.text_input(get_text("folder_name"))
                create_button = st.form_submit_button(get_text("create"))
            
            if create_button and folder_name:
                folder_path = os.path.join(st.session_state.current_path, folder_name)
                if os.path.exists(folder_path):
                    st.error(get_text("folder_exists"))
                else:
                    os.makedirs(folder_path)
                    st.success(get_text("folder_created"))
                    st.rerun()
        
        # 上传文件
        with st.expander(get_text("upload_file"), expanded=False):
            # 添加当前路径提示，帮助用户了解文件将上传到哪里
            current_folder = os.path.relpath(st.session_state.current_path, os.path.join("data", st.session_state.username, st.session_state.password))
            if current_folder == ".":
                current_folder = "主目录"
            st.write(f"当前上传位置: {current_folder}")
            
            # 使用表单包装文件上传器和上传按钮
            with st.form("upload_form", border=False):
                uploaded_files = st.file_uploader("", accept_multiple_files=True)
                submit_button = st.form_submit_button(get_text("upload_file"))
                
                if submit_button and uploaded_files:
                    for uploaded_file in uploaded_files:
                        # 检查文件大小限制（仅对非管理员）
                        if not st.session_state.is_admin:
                            # 计算当前用户目录大小
                            user_dir = os.path.join("data", st.session_state.username, st.session_state.password)
                            current_size = get_folder_size(user_dir) / (1024 * 1024)  # 转换为MiB
                            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # 转换为MiB
                            
                            if current_size + file_size > st.session_state.secrets["normal"]["limit"]:
                                st.error(f"{uploaded_file.name}: {get_text('file_size_limit')}")
                                continue
                        
                        # 保存文件到当前路径
                        file_path = os.path.join(st.session_state.current_path, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                    st.info(get_text("file_uploaded"))
        # 设置和退出按钮
        st.button(get_text("settings"), on_click=lambda: setattr(st.session_state, "page", "settings"), use_container_width=True)
        
        # 管理员面板按钮（仅管理员可见）
        if st.session_state.is_admin:
            st.button(get_text("admin_panel"), on_click=lambda: setattr(st.session_state, "page", "admin"), use_container_width=True)
        
        st.button(get_text("logout"), on_click=logout, use_container_width=True)
    
    # 主内容区
    st.title(f"{get_text('file_manager')}")
    st.write("主目录"+f"{os.path.relpath(st.session_state.current_path, 'data')}"[len(st.session_state['username']+st.session_state['password'])+1:])
    # 返回上级按钮
    parent_path = os.path.dirname(st.session_state.current_path)
    if parent_path.startswith(os.path.join("data", st.session_state.username)):
        if "主目录"+f"{os.path.relpath(st.session_state.current_path, 'data')}"[len(st.session_state['username']+st.session_state['password'])+1:] != "主目录":
            if st.sidebar.button(get_text("back"), use_container_width=True):
                st.session_state.current_path = parent_path
                st.rerun()
    
    # 列出当前目录内容
    items = os.listdir(st.session_state.current_path)
    folders = [item for item in items if os.path.isdir(os.path.join(st.session_state.current_path, item)) and not item.startswith(".")]
    files = [item for item in items if os.path.isfile(os.path.join(st.session_state.current_path, item)) and not item.startswith(".")]
    
    # 显示文件夹
    if folders:
        st.subheader("📁 Folders")
        cols = st.columns(4)
        for i, folder in enumerate(folders):
            with cols[i % 4]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    if st.button(f"📁 {folder}", key=f"folder_{i}", use_container_width=True):
                        st.session_state.current_path = os.path.join(st.session_state.current_path, folder)
                        st.rerun()
                with col2:
                    if st.button(get_text("delete"), key=f"del_folder_{i}"):
                        folder_path = os.path.join(st.session_state.current_path, folder)
                        # 使用确认对话框
                        if "confirm_delete_folder" not in st.session_state:
                            st.session_state.confirm_delete_folder = None
                        if "folder_to_delete" not in st.session_state:
                            st.session_state.folder_to_delete = None
                        
                        st.session_state.confirm_delete_folder = True
                        st.session_state.folder_to_delete = folder_path
                        st.rerun()
                        
                # 处理文件夹删除确认
                if "confirm_delete_folder" in st.session_state and st.session_state.confirm_delete_folder and "folder_to_delete" in st.session_state and st.session_state.folder_to_delete and os.path.basename(st.session_state.folder_to_delete) == folder:
                    st.warning(f"确定要删除文件夹 '{folder}' 及其所有内容吗？")
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("确认删除", key=f"confirm_del_folder_{i}"):
                            if os.path.exists(st.session_state.folder_to_delete):
                                shutil.rmtree(st.session_state.folder_to_delete)
                                st.session_state.confirm_delete_folder = None
                                st.session_state.folder_to_delete = None
                                st.success(get_text("folder_deleted"))
                                st.rerun()
                    with col_confirm2:
                        if st.button("取消", key=f"cancel_del_folder_{i}"):
                            st.session_state.confirm_delete_folder = None
                            st.session_state.folder_to_delete = None
                            st.rerun()
                with col3:
                    if st.button(get_text("download_all"), key=f"zip_folder_{i}"):
                        folder_path = os.path.join(st.session_state.current_path, folder)
                        # 创建内存中的ZIP文件
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for root, dirs, files in os.walk(folder_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    # 添加文件存在性检查
                                    if os.path.exists(file_path):
                                        zip_file.write(
                                            file_path, 
                                            os.path.relpath(file_path, os.path.dirname(folder_path))
                                        )
                        
                        # 提供下载链接
                        zip_buffer.seek(0)
                        b64 = base64.b64encode(zip_buffer.read()).decode()
                        href = f'<a href="data:application/zip;base64,{b64}" download="{folder}.zip">点击下载</a>'
                        st.markdown(href, unsafe_allow_html=True)
    
    # 显示文件
    if files:
        st.subheader("📄 Files")
        cols = st.columns(4)
        for i, file in enumerate(files):
            with cols[i % 4]:
                file_path = os.path.join(st.session_state.current_path, file)
                # 添加文件存在性检查
                if os.path.exists(file_path):
                    file_size = get_readable_size(os.path.getsize(file_path))
                else:
                    file_size = "文件不存在"
                
                st.write(f"📄 {file} ({file_size})")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(get_text("delete"), key=f"del_file_{i}"):
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            st.success(get_text("file_deleted"))
                            st.rerun()
                        else:
                            st.error(f"文件 {file} 不存在")
                
                with col2:
                    # 下载文件
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            file_content = f.read()
                        b64 = base64.b64encode(file_content).decode()
                        mime_type = "application/octet-stream"
                        if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                            mime_type = f"image/{file.split('.')[-1].lower()}"
                        elif file.lower().endswith(".pdf"):
                            mime_type = "application/pdf"
                        
                        href = f'<a href="data:{mime_type};base64,{b64}" download="{file}">下载</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:
                        st.error(f"文件 {file} 不存在")
                
                with col3:
                    # 预览文件（仅支持图片）
                    if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")) and os.path.exists(file_path):
                        if st.button(get_text("preview"), key=f"preview_{i}"):
                            st.session_state.preview_file = file_path
                            st.session_state.page = "preview"
                            st.rerun()

# 预览页面
def preview_page():
    if "preview_file" in st.session_state and os.path.exists(st.session_state.preview_file):
        file_name = os.path.basename(st.session_state.preview_file)
        
        st.title(f"{get_text('preview')}: {file_name}")
        
        # 返回按钮
        if st.sidebar.button(get_text("back"), use_container_width=True):
            st.session_state.page = "file_manager"
            st.rerun()
        
        # 显示图片
        try:
            image = Image.open(st.session_state.preview_file)
            st.image(image, caption=file_name, use_column_width=True)
        except Exception as e:
            st.error(f"无法预览文件: {str(e)}")
    else:
        st.error("文件不存在")
        if st.sidebar.button(get_text("back"), use_container_width=True):
            st.session_state.page = "file_manager"
            st.rerun()

# 设置页面
def settings_page():
    st.title(get_text("settings"))
    
    # 返回按钮
    if st.sidebar.button(get_text("back"), use_container_width=True):
        st.session_state.page = "file_manager"
        st.rerun()
    
    tab1, tab2, tab3 = st.tabs([get_text("change_password"), get_text("change_username"), get_text("change_language")])
    
    # 修改密码
    with tab1:
        with st.form("change_password_form"):
            old_password = st.text_input(get_text("old_password"), type="password")
            new_password = st.text_input(get_text("new_password"), type="password")
            confirm_password = st.text_input(get_text("confirm_password"), type="password")
            submit_button = st.form_submit_button(get_text("save"))
        
        if submit_button:
            if old_password != st.session_state.password:
                st.error(get_text("old_password_wrong"))
            elif new_password != confirm_password:
                st.error(get_text("password_mismatch"))
            else:
                # 创建新的密码目录
                old_dir = os.path.join("data", st.session_state.username, st.session_state.password)
                new_dir = os.path.join("data", st.session_state.username, new_password)
                
                # 移动文件
                if os.path.exists(old_dir):
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    
                    # 复制所有文件和子目录
                    for item in os.listdir(old_dir):
                        s = os.path.join(old_dir, item)
                        d = os.path.join(new_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                    
                    # 删除旧目录
                    shutil.rmtree(old_dir)
                    
                    # 更新session_state
                    st.session_state.password = new_password
                    st.session_state.current_path = new_dir
                    
                    # 更新用户列表
                    st.session_state.users[st.session_state.username]["password"] = new_password
                    
                    st.success(get_text("password_changed"))
                    st.rerun()
    
    # 修改用户名
    with tab2:
        with st.form("change_username_form"):
            new_username = st.text_input(get_text("new_username"))
            password = st.text_input(get_text("password"), type="password")
            submit_button = st.form_submit_button(get_text("save"))
        
        if submit_button:
            if password != st.session_state.password:
                st.error(get_text("login_fail"))
            elif new_username in st.session_state.users and new_username != st.session_state.username:
                st.error(get_text("username_exists"))
            else:
                # 创建新的用户目录
                old_dir = os.path.join("data", st.session_state.username)
                new_dir = os.path.join("data", new_username)
                
                # 移动文件
                if os.path.exists(old_dir):
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    
                    # 复制密码目录
                    old_pass_dir = os.path.join(old_dir, st.session_state.password)
                    new_pass_dir = os.path.join(new_dir, st.session_state.password)
                    
                    if os.path.exists(old_pass_dir):
                        if not os.path.exists(new_pass_dir):
                            os.makedirs(new_pass_dir)
                        
                        # 复制所有文件和子目录
                        for item in os.listdir(old_pass_dir):
                            s = os.path.join(old_pass_dir, item)
                            d = os.path.join(new_pass_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                    
                    # 删除旧目录
                    shutil.rmtree(old_dir)
                    
                    # 更新session_state
                    old_username = st.session_state.username
                    st.session_state.username = new_username
                    st.session_state.current_path = new_pass_dir
                    
                    # 更新用户列表
                    st.session_state.users[new_username] = st.session_state.users.pop(old_username)
                    
                    st.success(get_text("username_changed"))
                    st.rerun()
    
    # 修改语言
    with tab3:
        language_options = ["中文", "English"]
        selected_language = st.selectbox(get_text("change_language"), language_options, index=language_options.index(st.session_state.language))
        
        if st.button(get_text("save"), key="save_language"):
            st.session_state.language = selected_language
            st.success(f"语言已更改为 {selected_language}" if selected_language == "中文" else f"Language changed to {selected_language}")
            st.rerun()

# 管理员面板
def admin_page():
    if not st.session_state.is_admin:
        st.error("无权访问管理员面板")
        st.session_state.page = "file_manager"
        st.rerun()
    
    st.title(get_text("admin_panel"))
    
    # 返回按钮
    if st.sidebar.button(get_text("back"), use_container_width=True):
        st.session_state.page = "file_manager"
        st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs([get_text("user_stats"), get_text("storage_stats"), get_text("clean_inactive"), get_text("analysis")])
    
    # 用户统计
    with tab1:
        users = load_users()
        user_data = []
        
        for username, data in users.items():
            if username != st.session_state.secrets["administrator"]["name"]:
                user_dir = os.path.join("data", username, data["password"])
                size = get_folder_size(user_dir) / (1024 * 1024)  # 转换为MiB
                last_active = datetime.datetime.fromtimestamp(data["last_active"]).strftime("%Y-%m-%d %H:%M:%S")
                
                user_data.append({
                    "用户名": username,
                    "存储大小 (MiB)": round(size, 2),
                    "最后活跃时间": last_active,
                    "已使用百分比": round((size / st.session_state.secrets["normal"]["limit"]) * 100, 2) if size > 0 else 0
                })
        
        if user_data:
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
            
            # 显示用户数量
            st.info(f"总用户数: {len(users) - 1}")
        else:
            st.info("暂无普通用户")
    
    # 存储统计
    with tab2:
        users = load_users()
        total_size = 0
        user_sizes = {}
        
        for username, data in users.items():
            user_dir = os.path.join("data", username, data["password"])
            size = get_folder_size(user_dir) / (1024 * 1024)  # 转换为MiB
            user_sizes[username] = size
            total_size += size
        
        # 显示总存储大小
        st.info(f"总存储大小: {round(total_size, 2)} MiB")
        
        # 绘制饼图
        if user_sizes:
            fig, ax = plt.subplots(figsize=(10, 6))
            labels = []
            sizes = []
            
            for username, size in user_sizes.items():
                if size > 0:  # 只显示有数据的用户
                    labels.append(username)
                    sizes.append(size)
            
            if sizes:  # 确保有数据才绘图
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # 确保饼图是圆的
                plt.title("用户存储空间分布")
                st.pyplot(fig)
            else:
                st.info("暂无存储数据")
    
    # 清理不活跃用户
    with tab3:
        st.subheader(get_text("clean_inactive"))
        
        days = st.slider(get_text("days_inactive"), 1, 365, 30)
        
        if st.button(get_text("clean")):
            users = load_users()
            inactive_users = []
            current_time = time.time()
            inactive_threshold = current_time - (days * 24 * 60 * 60)  # 转换为秒
            
            for username, data in users.items():
                if username != st.session_state.secrets["administrator"]["name"]:
                    if data["last_active"] < inactive_threshold:
                        inactive_users.append(username)
            
            if inactive_users:
                for username in inactive_users:
                    user_dir = os.path.join("data", username)
                    if os.path.exists(user_dir):
                        shutil.rmtree(user_dir)
                    
                    # 从用户列表中删除
                    if username in st.session_state.users:
                        del st.session_state.users[username]
                
                st.success(f"{get_text('users_cleaned')} ({len(inactive_users)} users)")
                st.rerun()
            else:
                st.info(get_text("no_users_cleaned"))
    
    # 数据分析
    with tab4:
        st.subheader(get_text("analysis"))
        
        users = load_users()
        user_data = []
        
        for username, data in users.items():
            if username != st.session_state.secrets["administrator"]["name"]:
                user_dir = os.path.join("data", username, data["password"])
                size = get_folder_size(user_dir) / (1024 * 1024)  # 转换为MiB
                last_active = data["last_active"]
                days_since_active = (time.time() - last_active) / (24 * 60 * 60)  # 转换为天
                
                user_data.append({
                    "用户名": username,
                    "存储大小 (MiB)": round(size, 2),
                    "不活跃天数": round(days_since_active, 1)
                })
        
        if user_data:
            df = pd.DataFrame(user_data)
            
            # 绘制存储大小与不活跃天数的散点图
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=df, x="不活跃天数", y="存储大小 (MiB)", s=100, ax=ax)
            
            for i, row in df.iterrows():
                ax.text(row["不活跃天数"], row["存储大小 (MiB)"], row["用户名"], fontsize=9)
            
            plt.title("用户存储大小与不活跃天数关系")
            plt.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig)
            
            # 绘制存储大小柱状图
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=df, x="用户名", y="存储大小 (MiB)", ax=ax)
            plt.title("用户存储大小比较")
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig)
        else:
            st.info("暂无用户数据可供分析")

# 退出登录
def logout():
    st.session_state.page = "login"
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.is_admin = False
    st.session_state.current_path = ""

# 主程序
def main():
    # 确保必要的目录存在
    ensure_directories()
    
    # 根据当前页面显示相应内容
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "file_manager":
        file_manager_page()
    elif st.session_state.page == "preview":
        preview_page()
    elif st.session_state.page == "settings":
        settings_page()
    elif st.session_state.page == "admin":
        admin_page()

# 导入缺失的模块
import math

# 运行主程序
if __name__ == "__main__":
    main()
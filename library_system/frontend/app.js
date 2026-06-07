/* ===== 图书馆管理系统前端 ===== */
const API_BASE = 'http://localhost:8000/api/v1';

// 全局状态
let currentUser = null;
let authToken = localStorage.getItem('library_token');
let booksData = [];
let usersData = [];
let borrowsData = [];
let bookPage = 0;
const BOOK_PAGE_SIZE = 10;

// ===== 工具函数 =====
function $(selector) { return document.querySelector(selector); }
function $$(selector) { return document.querySelectorAll(selector); }

function showToast(message, type = 'success') {
    const container = $('#toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: 'check-circle', error: 'times-circle', warning: 'exclamation-circle', info: 'info-circle' };
    toast.innerHTML = `<i class="fas fa-${icons[type]}"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

function showLoading(show = true) {
    $('#loading-overlay').classList.toggle('active', show);
}

function formatDate(dateStr) {
    if (!dateStr) return '--';
    const d = new Date(dateStr);
    return d.toLocaleDateString('zh-CN');
}

function formatMoney(cents) {
    return '¥' + (cents / 100).toFixed(2);
}

function getStatusText(status) {
    const map = { borrowed: '借阅中', returned: '已归还', overdue: '已逾期', renewed: '已续借' };
    return map[status] || status;
}

function getRoleText(role) {
    const map = { admin: '管理员', librarian: '图书管理员', reader: '读者' };
    return map[role] || role;
}

// ===== API 请求 =====
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(API_BASE + url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            logout();
            showToast('登录已过期，请重新登录', 'error');
            return null;
        }

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(data?.detail || `请求失败: ${response.status}`);
        }

        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// ===== 认证相关 =====
async function login(username, password) {
    showLoading(true);
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || '登录失败');
        }

        authToken = data.access_token;
        localStorage.setItem('library_token', authToken);

        // 获取用户信息
        currentUser = await apiRequest('/users/me');
        showApp();
        showToast('登录成功！');
    } catch (error) {
        $('#login-error').textContent = error.message;
    } finally {
        showLoading(false);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('library_token');
    showLogin();
}

async function checkAuth() {
    if (!authToken) {
        showLogin();
        return;
    }
    try {
        currentUser = await apiRequest('/users/me');
        showApp();
    } catch {
        showLogin();
    }
}

// ===== 页面切换 =====
function showLogin() {
    $('#login-page').classList.add('active');
    $('#app-page').classList.remove('active');
}

function showApp() {
    $('#login-page').classList.remove('active');
    $('#app-page').classList.add('active');

    // 更新用户信息
    $('#user-name').textContent = currentUser.full_name || currentUser.username;
    $('#user-role').textContent = getRoleText(currentUser.role);

    // 根据角色显示/隐藏菜单
    const isAdmin = currentUser.role === 'admin';
    const isAdminOrLibrarian = isAdmin || currentUser.role === 'librarian';

    $$('.admin-only').forEach(el => {
        el.style.display = isAdmin ? 'flex' : 'none';
    });
    $$('.admin-librarian-only').forEach(el => {
        el.style.display = isAdminOrLibrarian ? 'inline-flex' : 'none';
    });

    // 加载默认页面
    switchPage('dashboard');
}

function switchPage(pageName) {
    // 更新导航
    $$('.nav-item').forEach(el => el.classList.remove('active'));
    $(`.nav-item[data-page="${pageName}"]`)?.classList.add('active');

    // 更新内容
    $$('.content-page').forEach(el => el.classList.remove('active'));
    $(`#page-${pageName}`)?.classList.add('active');

    // 更新标题
    const titles = {
        dashboard: '数据概览',
        books: '图书管理',
        borrows: '借阅管理',
        users: '用户管理'
    };
    $('#page-title').textContent = titles[pageName] || '';

    // 加载数据
    if (pageName === 'dashboard') loadDashboard();
    if (pageName === 'books') loadBooks();
    if (pageName === 'borrows') loadBorrows();
    if (pageName === 'users') loadUsers();
}

// ===== 数据概览 =====
async function loadDashboard() {
    showLoading(true);
    try {
        // 并行加载数据
        const [books, stats] = await Promise.all([
            apiRequest('/books?limit=1'),
            apiRequest('/borrows/statistics')
        ]);

        $('#stat-total-books').textContent = books?.length ?? 0;
        $('#stat-active-borrows').textContent = stats?.active_borrows ?? 0;
        $('#stat-overdue').textContent = stats?.overdue_count ?? 0;
        $('#stat-fines').textContent = formatMoney(stats?.total_fines ?? 0);

        // 加载最近借阅
        const borrows = await apiRequest('/borrows/all?limit=5');
        const tbody = $('#recent-borrows');
        tbody.innerHTML = '';

        if (!borrows || borrows.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-state"><i class="fas fa-inbox"></i><p>暂无借阅记录</p></td></tr>`;
            return;
        }

        borrows.forEach(b => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${b.book_title || '--'}</td>
                <td>${b.user_name || '--'}</td>
                <td>${formatDate(b.borrow_date)}</td>
                <td>${formatDate(b.due_date)}</td>
                <td><span class="status-badge status-${b.status}">${getStatusText(b.status)}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } finally {
        showLoading(false);
    }
}

// ===== 图书管理 =====
async function loadBooks() {
    showLoading(true);
    try {
        const keyword = $('#book-search').value;
        const category = $('#book-category-filter').value;
        const availableOnly = $('#available-only').checked;

        let url = `/books?skip=${bookPage * BOOK_PAGE_SIZE}&limit=${BOOK_PAGE_SIZE}`;
        if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
        if (category) url += `&category=${encodeURIComponent(category)}`;
        if (availableOnly) url += '&available_only=true';

        booksData = await apiRequest(url) || [];
        renderBooks();

        // 更新分类筛选选项
        const allBooks = await apiRequest('/books?limit=100') || [];
        const categories = [...new Set(allBooks.map(b => b.category).filter(Boolean))];
        const select = $('#book-category-filter');
        const currentVal = select.value;
        select.innerHTML = '<option value="">全部分类</option>' +
            categories.map(c => `<option value="${c}">${c}</option>`).join('');
        select.value = currentVal;
    } finally {
        showLoading(false);
    }
}

function renderBooks() {
    const tbody = $('#books-table');
    tbody.innerHTML = '';

    if (booksData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fas fa-book"></i><p>暂无图书数据</p></div></td></tr>`;
        return;
    }

    booksData.forEach(book => {
        const tr = document.createElement('tr');
        const canBorrow = book.available_copies > 0;
        const isAdminOrLib = currentUser.role === 'admin' || currentUser.role === 'librarian';

        tr.innerHTML = `
            <td><code>${book.isbn}</code></td>
            <td><strong>${book.title}</strong></td>
            <td>${book.author}</td>
            <td><span class="tag">${book.category || '--'}</span></td>
            <td>
                <span style="color: ${canBorrow ? 'var(--success)' : 'var(--danger)'}">
                    ${book.available_copies}/${book.total_copies}
                </span>
            </td>
            <td>${book.location || '--'}</td>
            <td>
                <div class="action-btns">
                    ${canBorrow ? `<button class="btn btn-success btn-sm" onclick="openBorrowModal(${book.id}, '${book.title.replace(/'/g, "\'")}')">
                        <i class="fas fa-hand-holding-book"></i> 借阅
                    </button>` : ''}
                    ${isAdminOrLib ? `
                    <button class="btn btn-primary btn-sm" onclick="editBook(${book.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteBook(${book.id})">
                        <i class="fas fa-trash"></i>
                    </button>` : ''}
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    $('#book-page-info').textContent = `第 ${bookPage + 1} 页`;
    $('#book-prev').disabled = bookPage === 0;
    $('#book-next').disabled = booksData.length < BOOK_PAGE_SIZE;
}

async function addBook(formData) {
    showLoading(true);
    try {
        await apiRequest('/books', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        showToast('图书添加成功！');
        closeModal('modal-add-book');
        loadBooks();
    } finally {
        showLoading(false);
    }
}

async function deleteBook(bookId) {
    if (!confirm('确定要删除这本图书吗？')) return;
    showLoading(true);
    try {
        await apiRequest(`/books/${bookId}`, { method: 'DELETE' });
        showToast('图书删除成功！');
        loadBooks();
    } finally {
        showLoading(false);
    }
}

function editBook(bookId) {
    const book = booksData.find(b => b.id === bookId);
    if (!book) return;
    // 简化：直接重新填充添加表单并修改
    showToast('编辑功能暂未实现，请删除后重新添加', 'info');
}

// ===== 借阅管理 =====
async function loadBorrows() {
    showLoading(true);
    try {
        // 我的借阅
        const myBorrows = await apiRequest('/borrows/my-borrows') || [];
        const myTbody = $('#my-borrows-table');
        myTbody.innerHTML = '';

        if (myBorrows.length === 0) {
            myTbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fas fa-inbox"></i><p>您暂无借阅记录</p></div></td></tr>`;
        } else {
            myBorrows.forEach(b => {
                const isOverdue = b.status === 'overdue';
                const canReturn = ['borrowed', 'renewed', 'overdue'].includes(b.status);
                const canRenew = ['borrowed', 'renewed'].includes(b.status) && b.renew_count < 2 && !isOverdue;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${b.book_title || '--'}</strong></td>
                    <td>${b.book_author || '--'}</td>
                    <td>${formatDate(b.borrow_date)}</td>
                    <td style="color: ${isOverdue ? 'var(--danger)' : ''}">${formatDate(b.due_date)}</td>
                    <td><span class="status-badge status-${b.status}">${getStatusText(b.status)}</span></td>
                    <td style="color: ${b.fine_amount > 0 ? 'var(--danger)' : ''}">${formatMoney(b.fine_amount)}</td>
                    <td>
                        <div class="action-btns">
                            ${canReturn ? `<button class="btn btn-success btn-sm" onclick="returnBook(${b.id})">
                                <i class="fas fa-undo"></i> 归还
                            </button>` : ''}
                            ${canRenew ? `<button class="btn btn-warning btn-sm" onclick="renewBook(${b.id})">
                                <i class="fas fa-sync"></i> 续借
                            </button>` : ''}
                        </div>
                    </td>
                `;
                myTbody.appendChild(tr);
            });
        }

        // 全部借阅（管理员/图书管理员）
        if (currentUser.role === 'admin' || currentUser.role === 'librarian') {
            const allBorrows = await apiRequest('/borrows/all?limit=50') || [];
            const allTbody = $('#all-borrows-table');
            allTbody.innerHTML = '';

            if (allBorrows.length === 0) {
                allTbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fas fa-inbox"></i><p>暂无借阅记录</p></div></td></tr>`;
            } else {
                allBorrows.forEach(b => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${b.user_name || '--'}<br><small style="color:var(--text-secondary)">${b.user_email || ''}</small></td>
                        <td><strong>${b.book_title || '--'}</strong><br><small>${b.book_author || ''}</small></td>
                        <td>${formatDate(b.borrow_date)}</td>
                        <td>${formatDate(b.due_date)}</td>
                        <td><span class="status-badge status-${b.status}">${getStatusText(b.status)}</span></td>
                        <td style="color: ${b.fine_amount > 0 ? 'var(--danger)' : ''}">${formatMoney(b.fine_amount)}</td>
                        <td>
                            ${b.status !== 'returned' ? `<button class="btn btn-success btn-sm" onclick="returnBook(${b.id})">
                                <i class="fas fa-undo"></i> 归还
                            </button>` : '--'}
                        </td>
                    `;
                    allTbody.appendChild(tr);
                });
            }
        }
    } finally {
        showLoading(false);
    }
}

async function borrowBook(bookId, days) {
    showLoading(true);
    try {
        await apiRequest('/borrows/borrow', {
            method: 'POST',
            body: JSON.stringify({ book_id: bookId, days: parseInt(days) })
        });
        showToast('借阅成功！');
        closeModal('modal-borrow');
        loadBooks();
    } finally {
        showLoading(false);
    }
}

async function returnBook(recordId) {
    showLoading(true);
    try {
        await apiRequest('/borrows/return', {
            method: 'POST',
            body: JSON.stringify({ record_id: recordId })
        });
        showToast('归还成功！');
        loadBorrows();
        loadDashboard();
    } finally {
        showLoading(false);
    }
}

async function renewBook(recordId) {
    showLoading(true);
    try {
        await apiRequest('/borrows/renew', {
            method: 'POST',
            body: JSON.stringify({ record_id: recordId, days: 15 })
        });
        showToast('续借成功！');
        loadBorrows();
    } finally {
        showLoading(false);
    }
}

async function checkOverdue() {
    showLoading(true);
    try {
        const result = await apiRequest('/borrows/check-overdue', { method: 'POST' });
        showToast(result.message, 'info');
        loadBorrows();
    } finally {
        showLoading(false);
    }
}

// ===== 用户管理 =====
async function loadUsers() {
    showLoading(true);
    try {
        usersData = await apiRequest('/users?limit=100') || [];
        const tbody = $('#users-table');
        tbody.innerHTML = '';

        if (usersData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fas fa-users"></i><p>暂无用户数据</p></div></td></tr>`;
            return;
        }

        usersData.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${u.id}</td>
                <td><strong>${u.username}</strong></td>
                <td>${u.email}</td>
                <td>${u.full_name || '--'}</td>
                <td><span class="role-badge role-${u.role}">${getRoleText(u.role)}</span></td>
                <td>${u.is_active ? '<span style="color:var(--success)">● 正常</span>' : '<span style="color:var(--danger)">● 禁用</span>'}</td>
                <td>
                    <div class="action-btns">
                        <button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } finally {
        showLoading(false);
    }
}

async function addUser(formData) {
    showLoading(true);
    try {
        await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        showToast('用户添加成功！');
        closeModal('modal-add-user');
        loadUsers();
    } finally {
        showLoading(false);
    }
}

async function deleteUser(userId) {
    if (!confirm('确定要删除该用户吗？')) return;
    showLoading(true);
    try {
        await apiRequest(`/users/${userId}`, { method: 'DELETE' });
        showToast('用户已禁用！');
        loadUsers();
    } finally {
        showLoading(false);
    }
}

// ===== 弹窗管理 =====
function openModal(modalId) {
    $(`#${modalId}`).classList.add('active');
}

function closeModal(modalId) {
    $(`#${modalId}`).classList.remove('active');
    // 清空表单
    const form = $(`#${modalId} form`);
    if (form) form.reset();
}

function openBorrowModal(bookId, bookTitle) {
    $('#borrow-book-id').value = bookId;
    $('#borrow-book-title').value = bookTitle;
    openModal('modal-borrow');
}

// ===== 事件绑定 =====
document.addEventListener('DOMContentLoaded', () => {
    // 登录表单
    $('#login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const username = $('#login-username').value;
        const password = $('#login-password').value;
        $('#login-error').textContent = '';
        login(username, password);
    });

    // 退出登录
    $('#logout-btn').addEventListener('click', logout);

    // 导航切换
    $$('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            switchPage(page);
        });
    });

    // Tab 切换
    $$('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            $$('.tab-btn').forEach(b => b.classList.remove('active'));
            $$('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            $(`#tab-${tab}`).classList.add('active');
        });
    });

    // 弹窗关闭
    $$('.modal-close, .modal-close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) modal.classList.remove('active');
        });
    });

    $('.modal').addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    // 添加图书
    $('#btn-add-book').addEventListener('click', () => openModal('modal-add-book'));
    $('#form-add-book').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = Object.fromEntries(new FormData(e.target));
        formData.total_copies = parseInt(formData.total_copies);
        formData.publish_year = formData.publish_year ? parseInt(formData.publish_year) : null;
        addBook(formData);
    });

    // 添加用户
    $('#btn-add-user').addEventListener('click', () => openModal('modal-add-user'));
    $('#form-add-user').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = Object.fromEntries(new FormData(e.target));
        addUser(formData);
    });

    // 借阅表单
    $('#form-borrow').addEventListener('submit', (e) => {
        e.preventDefault();
        const bookId = $('#borrow-book-id').value;
        const days = e.target.days.value;
        borrowBook(bookId, days);
    });

    // 搜索
    $('#book-search').addEventListener('input', debounce(() => {
        bookPage = 0;
        loadBooks();
    }, 300));

    $('#book-category-filter').addEventListener('change', () => {
        bookPage = 0;
        loadBooks();
    });

    $('#available-only').addEventListener('change', () => {
        bookPage = 0;
        loadBooks();
    });

    // 分页
    $('#book-prev').addEventListener('click', () => {
        if (bookPage > 0) {
            bookPage--;
            loadBooks();
        }
    });

    $('#book-next').addEventListener('click', () => {
        bookPage++;
        loadBooks();
    });

    // 检查逾期
    $('#btn-check-overdue').addEventListener('click', checkOverdue);

    // 时间显示
    setInterval(() => {
        $('#current-time').textContent = new Date().toLocaleString('zh-CN');
    }, 1000);

    // 初始化
    checkAuth();
});

// 防抖函数
function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

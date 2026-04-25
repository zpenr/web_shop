// Конфигурация API
const API_BASE = '/api'; // Замените на ваш адрес
let authToken = localStorage.getItem('access_token') || null;
let currentUser = null;

// Элементы DOM
const authSection = document.getElementById('auth-section');
const mainSection = document.getElementById('main-section');
const contentArea = document.getElementById('content-area');
const userInfoSpan = document.getElementById('user-info');

// Проверка авторизации при загрузке
if (authToken) {
    checkAuthAndLoadMain();
} else {
    showAuth();
}

// Функции отображения разделов
function showAuth() {
    authSection.style.display = 'block';
    mainSection.style.display = 'none';
    loadJobsForRegister();
}

async function checkAuthAndLoadMain() {
    try {
        const response = await fetch(`${API_BASE}/auth/me/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            currentUser = await response.json();
            userInfoSpan.textContent = `${currentUser.name} ${currentUser.surname} (ID: ${currentUser.id})`;
            showMain();
        } else {
            logout();
        }
    } catch (e) {
        logout();
    }
}

function showMain() {
    authSection.style.display = 'none';
    mainSection.style.display = 'block';
    showSection('products');
}

function logout() {
    localStorage.removeItem('access_token');
    authToken = null;
    currentUser = null;
    showAuth();
}

document.getElementById('logout-btn').addEventListener('click', logout);

// Навигация
document.querySelectorAll('[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = e.target.dataset.section;
        showSection(section);
    });
});

async function showSection(section) {
    contentArea.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    try {
        switch (section) {
            case 'products': await renderProducts(); break;
            case 'categories': await renderCategories(); break;
            case 'employees': await renderEmployees(); break;
            case 'sales': await renderSales(); break;
            case 'receipts': await renderReceipts(); break;
            case 'jobs': await renderJobs(); break;
            case 'manager': await renderManager(); break;
            default: contentArea.innerHTML = '<h3>Раздел не найден</h3>';
        }
    } catch (error) {
        contentArea.innerHTML = `<div class="alert alert-danger">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Универсальный запрос
async function apiRequest(endpoint, method = 'GET', body = null, isForm = false) {
    const headers = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    
    const options = { method, headers };
    
    if (body) {
        if (isForm) {
            options.body = body;
        } else {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
    }
    return response.json();
}

// ------------------- Товары -------------------
async function renderProducts() {
    const products = await apiRequest('/products/');
    const categories = await apiRequest('/categories/');
    const catMap = Object.fromEntries(categories.map(c => [c.id, c.name]));
    
    let html = `
        <h2>Товары</h2>
        <button class="btn btn-primary mb-3" onclick="showAddProductForm()">Добавить товар</button>
        <div class="filter-form">
            <h5>Фильтр</h5>
            <div class="row">
                <div class="col-md-3">
                    <select class="form-select" id="filter-category">
                        <option value="">Все категории</option>
                        ${categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                    </select>
                </div>
                <div class="col-md-3">
                    <input type="number" class="form-control" id="filter-min-price" placeholder="Мин. цена" value="0">
                </div>
                <div class="col-md-3">
                    <input type="number" class="form-control" id="filter-max-price" placeholder="Макс. цена" value="100000000">
                </div>
                <div class="col-md-3">
                    <button class="btn btn-secondary" onclick="applyFilter()">Применить</button>
                    <button class="btn btn-outline-secondary" onclick="renderProducts()">Сбросить</button>
                </div>
            </div>
        </div>
        <div id="products-table-container"></div>
    `;
    contentArea.innerHTML = html;
    renderProductsTable(products, catMap);
}

function renderProductsTable(products, catMap) {
    const container = document.getElementById('products-table-container');
    if (!products.length) {
        container.innerHTML = '<p>Нет товаров</p>';
        return;
    }
    let table = `
        <table class="table table-striped">
            <thead><tr><th>ID</th><th>Название</th><th>Цена</th><th>Категория</th><th>На складе</th><th>Действия</th></tr></thead>
            <tbody>
    `;
    products.forEach(p => {
        const catName = p.category ? p.category.name : (catMap[p.id_category] || p.id_category);
        table += `<tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.price}</td>
            <td>${catName}</td>
            <td>${p.quantity_at_storage}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editProduct(${p.id})">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id})">Удалить</button>
            </td>
        </tr>`;
    });
    table += '</tbody></table>';
    container.innerHTML = table;
}

window.applyFilter = async function() {
    const category = document.getElementById('filter-category').value;
    const minPrice = document.getElementById('filter-min-price').value;
    const maxPrice = document.getElementById('filter-max-price').value;
    let url = `/products/filter/?min_price=${minPrice}&max_price=${maxPrice}`;
    if (category) url += `&category_id=${category}`;
    const products = await apiRequest(url);
    const categories = await apiRequest('/categories/');
    const catMap = Object.fromEntries(categories.map(c => [c.id, c.name]));
    renderProductsTable(products, catMap);
};

window.showAddProductForm = async function() {
    const categories = await apiRequest('/categories/');
    const formHtml = `
        <h3>Добавить товар</h3>
        <form onsubmit="addProduct(event)">
            <div class="mb-3"><input type="text" class="form-control" name="name" placeholder="Название" required></div>
            <div class="mb-3"><input type="number" class="form-control" name="price" placeholder="Цена" required></div>
            <div class="mb-3">
                <select class="form-select" name="id_category" required>
                    <option value="">Выберите категорию</option>
                    ${categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                </select>
            </div>
            <div class="mb-3"><input type="number" class="form-control" name="quantity_at_storage" placeholder="Количество на складе" required></div>
            <button type="submit" class="btn btn-success">Сохранить</button>
            <button type="button" class="btn btn-secondary" onclick="renderProducts()">Отмена</button>
        </form>
    `;
    contentArea.innerHTML = formHtml;
};

window.addProduct = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const params = new URLSearchParams(formData).toString();
    try {
        await apiRequest(`/products/?${params}`, 'POST');
        renderProducts();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

window.editProduct = async function(id) {
    const product = await apiRequest(`/products/${id}`);
    const categories = await apiRequest('/categories/');
    const html = `
        <h3>Редактировать товар #${id}</h3>
        <form onsubmit="updateProduct(event, ${id})">
            <div class="mb-3"><label>Цена</label><input type="number" class="form-control" name="price" value="${product.price}"></div>
            <div class="mb-3"><label>Количество на складе</label><input type="number" class="form-control" name="quantity_at_storage" value="${product.quantity_at_storage}"></div>
            <button type="submit" class="btn btn-warning">Обновить</button>
            <button type="button" class="btn btn-secondary" onclick="renderProducts()">Отмена</button>
        </form>
    `;
    contentArea.innerHTML = html;
};

window.updateProduct = async function(e, id) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const params = new URLSearchParams();
    params.append('product_id', id);
    for (let [key, value] of formData.entries()) {
        if (value) params.append(key, value);
    }
    try {
        await apiRequest(`/products/?${params.toString()}`, 'PATCH');
        renderProducts();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

window.deleteProduct = async function(id) {
    if (!confirm('Удалить товар?')) return;
    try {
        await apiRequest(`/products/?id=${id}`, 'DELETE');
        renderProducts();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Категории -------------------
async function renderCategories() {
    const categories = await apiRequest('/categories/');
    let html = `<h2>Категории</h2>
        <button class="btn btn-primary mb-3" onclick="showAddCategoryForm()">Добавить категорию</button>
        <table class="table"><thead><tr><th>ID</th><th>Название</th></tr></thead><tbody>`;
    categories.forEach(c => html += `<tr><td>${c.id}</td><td>${c.name}</td></tr>`);
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

window.showAddCategoryForm = function() {
    contentArea.innerHTML = `
        <h3>Добавить категорию</h3>
        <form onsubmit="addCategory(event)">
            <div class="mb-3"><input type="text" class="form-control" name="name" placeholder="Название" required></div>
            <button type="submit" class="btn btn-success">Сохранить</button>
            <button type="button" class="btn btn-secondary" onclick="renderCategories()">Отмена</button>
        </form>
    `;
};

window.addCategory = async function(e) {
    e.preventDefault();
    const name = new FormData(e.target).get('name');
    try {
        await apiRequest(`/categories/?name=${encodeURIComponent(name)}`, 'POST');
        renderCategories();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Сотрудники -------------------
async function renderEmployees() {
    const employees = await apiRequest('/employees/');
    let html = `<h2>Сотрудники</h2>
        <table class="table"><thead><tr>
            <th>ID</th><th>Имя</th><th>Фамилия</th><th>Логин</th><th>Должность</th><th>Текущий босс</th><th>Новый босс</th><th>Действие</th>
        </tr></thead><tbody>`;
    
    employees.forEach(e => {
        const bossSelect = `<select class="form-select form-select-sm" id="boss-select-${e.id}">
            <option value="">Без руководителя</option>
            ${employees.filter(emp => emp.id !== e.id).map(emp => `<option value="${emp.id}">${emp.name} ${emp.surname}</option>`).join('')}
        </select>`;
        
        const currentBoss = e.boss ? employees.find(emp => emp.id === e.boss) : null;
        const currentBossName = currentBoss ? `${currentBoss.name} ${currentBoss.surname}` : '—';
        
        html += `<tr>
            <td>${e.id}</td>
            <td>${e.name}</td>
            <td>${e.surname}</td>
            <td>${e.login || '—'}</td>
            <td>${e.id_job}</td>
            <td>${currentBossName}</td>
            <td>${bossSelect}</td>
            <td><button class="btn btn-sm btn-primary" onclick="setBoss(${e.id})">Назначить</button></td>
        </tr>`;
    });
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

window.setBoss = async function(employeeId) {
    const select = document.getElementById(`boss-select-${employeeId}`);
    const bossId = select.value;
    const params = new URLSearchParams();
    params.append('id', employeeId);
    if (bossId) params.append('boss_id', bossId);
    
    try {
        await apiRequest(`/employees/?${params.toString()}`, 'PATCH');
        alert('Руководитель обновлён');
        renderEmployees();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Продажи -------------------
async function renderSales() {
    const [sales, products, employees] = await Promise.all([
        apiRequest('/sales/'),
        apiRequest('/products/'),
        apiRequest('/employees/')
    ]);
    
    let html = `<h2>Продажи</h2>
        <button class="btn btn-primary mb-3" onclick="showAddSaleForm()">Добавить продажу</button>
        
        <div class="filter-form">
            <h5>Фильтр продаж</h5>
            <div class="row g-2">
                <div class="col-md-2">
                    <input type="number" class="form-control" id="filter-min-sum" placeholder="Мин. сумма">
                </div>
                <div class="col-md-2">
                    <input type="number" class="form-control" id="filter-max-sum" placeholder="Макс. сумма">
                </div>
                <div class="col-md-2">
                    <input type="datetime-local" class="form-control" id="filter-min-date">
                </div>
                <div class="col-md-2">
                    <input type="datetime-local" class="form-control" id="filter-max-date">
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="filter-product">
                        <option value="">Все товары</option>
                        ${products.map(p => `<option value="${p.id}">${p.name}</option>`).join('')}
                    </select>
                </div>
                <div class="col-md-2">
                    <select class="form-select" id="filter-employee">
                        <option value="">Все сотрудники</option>
                        ${employees.map(e => `<option value="${e.id}">${e.name} ${e.surname}</option>`).join('')}
                    </select>
                </div>
            </div>
            <div class="mt-2">
                <button class="btn btn-secondary" onclick="applySalesFilter()">Применить фильтр</button>
                <button class="btn btn-outline-secondary" onclick="renderSales()">Сбросить</button>
            </div>
        </div>
        
        <div id="sales-table-container"></div>`;
    contentArea.innerHTML = html;
    renderSalesTable(sales);
}

function renderSalesTable(sales) {
    const container = document.getElementById('sales-table-container');
    if (!sales.length) {
        container.innerHTML = '<p>Продаж не найдено</p>';
        return;
    }
    let table = `<table class="table"><thead><tr>
        <th>ID</th><th>Товар</th><th>Категория</th><th>Цена</th><th>Кол-во</th><th>Сумма</th><th>Продавец</th><th>Дата</th>
    </tr></thead><tbody>`;
    
    sales.forEach(s => {
        const product = s.product;
        const category = product?.category?.name || '—';
        const employee = s.receipt?.employee;
        const total = s.quintity * product.price;
        const date = s.receipt?.created_at ? new Date(s.receipt.created_at).toLocaleString() : '—';
        table += `<tr>
            <td>${s.id}</td>
            <td>${product.name}</td>
            <td>${category}</td>
            <td>${product.price} руб.</td>
            <td>${s.quintity}</td>
            <td>${total} руб.</td>
            <td>${employee ? `${employee.name} ${employee.surname}` : '—'}</td>
            <td>${date}</td>
        </tr>`;
    });
    table += '</tbody></table>';
    container.innerHTML = table;
}

window.applySalesFilter = async function() {
    const params = new URLSearchParams();
    const minSum = document.getElementById('filter-min-sum').value;
    const maxSum = document.getElementById('filter-max-sum').value;
    const minDate = document.getElementById('filter-min-date').value;
    const maxDate = document.getElementById('filter-max-date').value;
    const productId = document.getElementById('filter-product').value;
    const employeeId = document.getElementById('filter-employee').value;
    
    if (minSum) params.append('min_sum', minSum);
    if (maxSum) params.append('max_sum', maxSum);
    if (minDate) params.append('min_date', new Date(minDate).toISOString());
    if (maxDate) params.append('max_date', new Date(maxDate).toISOString());
    if (productId) params.append('product_id', productId);
    if (employeeId) params.append('employee_id', employeeId);
    
    try {
        const filteredSales = await apiRequest(`/sales/filter/?${params.toString()}`);
        renderSalesTable(filteredSales);
    } catch (error) {
        alert('Ошибка фильтрации: ' + error.message);
    }
};

window.showAddSaleForm = async function() {
    const products = await apiRequest('/products/');
    const html = `
        <h3>Добавить продажу</h3>
        <form onsubmit="addSale(event)">
            <div class="mb-3"><label>Дата и время</label><input type="datetime-local" class="form-control" name="created_at" required></div>
            <div class="mb-3"><label>Товар</label><select class="form-select" name="id_product" required>
                ${products.map(p => `<option value="${p.id}">${p.name} (в наличии: ${p.quantity_at_storage} шт.)</option>`).join('')}
            </select></div>
            <div class="mb-3"><label>Количество</label><input type="number" class="form-control" name="quintity" min="1" required></div>
            <button type="submit" class="btn btn-success">Сохранить</button>
            <button type="button" class="btn btn-secondary" onclick="renderSales()">Отмена</button>
        </form>
    `;
    contentArea.innerHTML = html;
};

window.addSale = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const params = new URLSearchParams();
    const dt = new Date(formData.get('created_at')).toISOString().slice(0,19);
    params.append('created_at', dt);
    params.append('id_product', formData.get('id_product'));
    params.append('quintity', formData.get('quintity'));
    try {
        await apiRequest(`/sales/?${params.toString()}`, 'POST');
        renderSales();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Чеки -------------------
async function renderReceipts() {
    const receipts = await apiRequest('/receipts/');
    let html = `<h2>Чеки</h2><table class="table"><thead><tr><th>ID</th><th>Дата создания</th><th>Сотрудник</th></tr></thead><tbody>`;
    receipts.forEach(r => {
        const employee = r.employee;
        const empName = employee ? `${employee.name} ${employee.surname}` : '—';
        html += `<tr><td>${r.id}</td><td>${new Date(r.created_at).toLocaleString()}</td><td>${empName}</td></tr>`;
    });
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

// ------------------- Должности -------------------
async function renderJobs() {
    const jobs = await apiRequest('/jobs/');
    let html = `<h2>Должности</h2>
        <button class="btn btn-primary mb-3" onclick="showAddJobForm()">Добавить должность</button>
        <table class="table"><thead><tr><th>ID</th><th>Название</th><th>Права</th></tr></thead><tbody>`;
    jobs.forEach(j => html += `<tr><td>${j.id}</td><td>${j.name}</td><td>${j.roots}</td></tr>`);
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

window.showAddJobForm = function() {
    contentArea.innerHTML = `
        <h3>Добавить должность</h3>
        <form onsubmit="addJob(event)">
            <div class="mb-3"><input type="text" class="form-control" name="name" placeholder="Название" required></div>
            <div class="mb-3"><input type="number" class="form-control" name="roots" placeholder="Уровень прав" required></div>
            <button type="submit" class="btn btn-success">Сохранить</button>
            <button type="button" class="btn btn-secondary" onclick="renderJobs()">Отмена</button>
        </form>
    `;
};

window.addJob = async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const params = new URLSearchParams(formData).toString();
    try {
        await apiRequest(`/jobs/?${params}`, 'POST');
        renderJobs();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Управление (менеджер) -------------------
async function renderManager() {
    if (!currentUser || !currentUser.id) {
        contentArea.innerHTML = '<div class="alert alert-danger">Ошибка: не определён ID пользователя</div>';
        return;
    }
    const children = await apiRequest(`/manager/childrens/?boss_id=${currentUser.id}`);
    
    let html = `<h2>Управление подчиненными</h2>`;
    html += `<h4>Ваши подчиненные</h4>`;
    if (children.length) {
        html += `<table class="table"><thead><tr><th>ID</th><th>Имя</th><th>Фамилия</th><th>Действия</th></tr></thead><tbody>`;
        children.forEach(c => {
            html += `<tr><td>${c.id}</td><td>${c.name}</td><td>${c.surname}</td>
                <td><button class="btn btn-sm btn-danger" onclick="dismissEmployee(${c.id})">Уволить</button></td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p>Нет подчиненных</p>';
    }
    html += `<h4 class="mt-4">Продажи подчиненных</h4><button class="btn btn-info mb-2" onclick="loadChildrenSales()">Загрузить</button><div id="children-sales"></div>`;
    contentArea.innerHTML = html;
}

window.loadChildrenSales = async function() {
    if (!currentUser || !currentUser.id) return;
    const sales = await apiRequest(`/manager/sales/?boss_id=${currentUser.id}`);
    const container = document.getElementById('children-sales');
    if (!sales.length) {
        container.innerHTML = '<p>Продаж нет</p>';
        return;
    }
    let table = `<table class="table"><thead><tr><th>ID</th><th>Товар</th><th>Кол-во</th><th>Продавец</th><th>Дата</th></tr></thead><tbody>`;
    sales.forEach(s => {
        const product = s.product;
        const employee = s.receipt?.employee;
        const date = s.receipt?.created_at ? new Date(s.receipt.created_at).toLocaleString() : '—';
        table += `<tr>
            <td>${s.id}</td>
            <td>${product.name}</td>
            <td>${s.quintity}</td>
            <td>${employee ? `${employee.name} ${employee.surname}` : '—'}</td>
            <td>${date}</td>
        </tr>`;
    });
    table += '</tbody></table>';
    container.innerHTML = table;
};

window.dismissEmployee = async function(employeeId) {
    if (!confirm('Уволить сотрудника?')) return;
    try {
        await apiRequest(`/manager/childrens/?id=${employeeId}&boss_id=${currentUser.id}`, 'DELETE');
        renderManager();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Аутентификация -------------------
async function loadJobsForRegister() {
    try {
        const jobs = await fetch(`${API_BASE}/jobs/`).then(r => r.json());
        const select = document.getElementById('reg-id-job');
        select.innerHTML = jobs.map(j => `<option value="${j.id}">${j.name} (права: ${j.roots})</option>`).join('');
    } catch (e) {
        console.error('Не удалось загрузить должности', e);
    }
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorDiv = document.getElementById('login-error');
    errorDiv.textContent = '';
    const formData = new FormData();
    formData.append('login', document.getElementById('login-login').value);
    formData.append('password', document.getElementById('login-password').value);
    
    try {
        const response = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Неверный логин или пароль');
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('access_token', authToken);
        await checkAuthAndLoadMain();
    } catch (error) {
        errorDiv.textContent = error.message;
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorDiv = document.getElementById('register-error');
    errorDiv.textContent = '';
    const formData = new FormData();
    formData.append('name', document.getElementById('reg-name').value);
    formData.append('surname', document.getElementById('reg-surname').value);
    formData.append('login', document.getElementById('reg-login').value);
    formData.append('password', document.getElementById('reg-password').value);
    formData.append('password2', document.getElementById('reg-password2').value);
    formData.append('id_job', document.getElementById('reg-id-job').value);
    
    try {
        const response = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const err = await response.text();
            throw new Error(err || 'Ошибка регистрации');
        }
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('access_token', authToken);
        await checkAuthAndLoadMain();
    } catch (error) {
        errorDiv.textContent = error.message;
    }
});

// Глобальные функции для onclick
window.renderProducts = renderProducts;
window.renderCategories = renderCategories;
window.renderEmployees = renderEmployees;
window.renderSales = renderSales;
window.renderReceipts = renderReceipts;
window.renderJobs = renderJobs;
window.renderManager = renderManager;
window.showSection = showSection;
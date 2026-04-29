const API_BASE = 'http://localhost:8000';
let authToken = localStorage.getItem('access_token') || null;
let currentUser = null;
let currentPermissions = {
    make_sales: false,
    add_categories: false,
    add_products: false,
    redact_products: false,
    add_jobs: false,
    add_boss: false
};

const authSection = document.getElementById('auth-section');
const mainSection = document.getElementById('main-section');
const contentArea = document.getElementById('content-area');
const userInfoSpan = document.getElementById('user-info');

if (authToken) {
    checkAuthAndLoadMain();
} else {
    showAuth();
}

function showAuth() {
    authSection.style.display = 'block';
    mainSection.style.display = 'none';
    loadJobsForRegister();
}

async function checkAuthAndLoadMain() {
    try {
        const [userResponse, permResponse] = await Promise.all([
            fetch(`${API_BASE}/auth/me/`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/auth/permission/`, { headers: { 'Authorization': `Bearer ${authToken}` } })
        ]);
        if (userResponse.ok && permResponse.ok) {
            currentUser = await userResponse.json();
            currentPermissions = await permResponse.json();
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
    currentPermissions = {};
    showAuth();
}

document.getElementById('logout-btn').addEventListener('click', logout);

document.querySelectorAll('[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(e.target.dataset.section);
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

    let html = `<h2>Товары</h2>`;
    if (currentPermissions.add_products) {
        html += `<button class="btn btn-primary mb-3" onclick="showAddProductForm()">Добавить товар</button>`;
    }
    html += `
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
    let table = `<table class="table table-striped"><thead><tr><th>ID</th><th>Название</th><th>Цена</th><th>Категория</th><th>На складе</th>`;
    if (currentPermissions.add_products) table += `<th>Действия</th>`;
    table += `</tr></thead><tbody>`;
    products.forEach(p => {
        const catName = p.category ? p.category.name : (catMap[p.id_category] || p.id_category);
        table += `<tr><td>${p.id}</td><td>${p.name}</td><td>${p.price}</td><td>${catName}</td><td>${p.quantity_at_storage}</td>`;
        if (currentPermissions.add_products) {
            table += `<td>
                <button class="btn btn-sm btn-warning" onclick="editProduct(${p.id})">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id})">Удалить</button>
            </td>`;
        }
        table += `</tr>`;
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
    if (!currentPermissions.add_products) {
        alert('Недостаточно прав');
        return;
    }
    const categories = await apiRequest('/categories/');
    contentArea.innerHTML = `
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
    if (!currentPermissions.add_products) {
        alert('Недостаточно прав');
        return;
    }
    const product = await apiRequest(`/products/${id}`);
    contentArea.innerHTML = `
        <h3>Редактировать товар #${id}</h3>
        <form onsubmit="updateProduct(event, ${id})">
            <div class="mb-3"><label>Цена</label><input type="number" class="form-control" name="price" value="${product.price}"></div>
            <div class="mb-3"><label>Количество на складе</label><input type="number" class="form-control" name="quantity_at_storage" value="${product.quantity_at_storage}"></div>
            <button type="submit" class="btn btn-warning">Обновить</button>
            <button type="button" class="btn btn-secondary" onclick="renderProducts()">Отмена</button>
        </form>
    `;
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
    let html = `<h2>Категории</h2>`;
    if (currentPermissions.add_categories) {
        html += `<button class="btn btn-primary mb-3" onclick="showAddCategoryForm()">Добавить категорию</button>`;
    }
    html += `<table class="table"><thead><tr><th>ID</th><th>Название</th></tr></thead><tbody>`;
    categories.forEach(c => html += `<tr><td>${c.id}</td><td>${c.name}</td></tr>`);
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

window.showAddCategoryForm = function() {
    if (!currentPermissions.add_categories) {
        alert('Недостаточно прав');
        return;
    }
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
            <th>ID</th><th>Имя</th><th>Фамилия</th><th>Логин</th><th>Должность</th><th>Текущий босс</th>`;
    if (currentPermissions.add_boss) {
        html += `<th>Новый босс</th><th>Действие</th>`;
    }
    html += `</tr></thead><tbody>`;

    employees.forEach(e => {
        let bossSelect = '';
        let actionBtn = '';
        if (currentPermissions.add_boss && currentUser && e.id !== currentUser.id) {
            bossSelect = `<td><select class="form-select form-select-sm" id="boss-select-${e.id}">
                <option value="">Без руководителя</option>
                ${employees.filter(emp => emp.id !== e.id).map(emp => `<option value="${emp.id}">${emp.name} ${emp.surname}</option>`).join('')}
            </select></td>`;
            actionBtn = `<td><button class="btn btn-sm btn-primary" onclick="setBoss(${e.id})">Назначить</button></td>`;
        } else if (currentPermissions.add_boss) {
            bossSelect = '<td></td>';
            actionBtn = '<td></td>';
        }
        const currentBoss = e.boss ? employees.find(emp => emp.id === e.boss) : null;
        const currentBossName = currentBoss ? `${currentBoss.name} ${currentBoss.surname}` : '—';

        html += `<tr>
            <td>${e.id}</td>
            <td>${e.name}</td>
            <td>${e.surname}</td>
            <td>${e.login || '—'}</td>
            <td>${e.id_job}</td>
            <td>${currentBossName}</td>
            ${bossSelect}
            ${actionBtn}
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

// ------------------- Продажи (чек + позиции) -------------------
async function renderSales() {
    const [sales, products, employees] = await Promise.all([
        apiRequest('/sales/'),
        apiRequest('/products/'),
        apiRequest('/employees/')
    ]);

    let html = `<h2>Продажи</h2>`;
    if (currentPermissions.make_sales) {
        html += `<button class="btn btn-primary mb-3" onclick="showNewReceiptForm()">Создать чек (продажу)</button>`;
    }
    html += `
        <div class="filter-form">
            <h5>Фильтр продаж</h5>
            <div class="row g-2">
                <div class="col-md-2"><input type="number" class="form-control" id="filter-min-sum" placeholder="Мин. сумма"></div>
                <div class="col-md-2"><input type="number" class="form-control" id="filter-max-sum" placeholder="Макс. сумма"></div>
                <div class="col-md-2"><input type="datetime-local" class="form-control" id="filter-min-date"></div>
                <div class="col-md-2"><input type="datetime-local" class="form-control" id="filter-max-date"></div>
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
        const receipt = s.receipt;
        const employee = receipt?.employee;
        const total = s.quintity * product.price;
        const date = receipt?.created_at ? new Date(receipt.created_at).toLocaleString() : '—';
        table += `<tr>
            <td>${s.id}</td><td>${product.name}</td><td>${category}</td>
            <td>${product.price} руб.</td><td>${s.quintity}</td><td>${total} руб.</td>
            <td>${employee ? `${employee.name} ${employee.surname}` : '—'}</td><td>${date}</td>
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

// Форма создания чека с позициями
window.showNewReceiptForm = async function() {
    if (!currentPermissions.make_sales) {
        alert('Недостаточно прав');
        return;
    }
    const products = await apiRequest('/products/');
    const now = new Date().toISOString().slice(0, 16); // формат для datetime-local

    const html = `
        <h3>Создание чека (продажи)</h3>
        <form id="receipt-form">
            <div class="mb-3">
                <label>Дата и время</label>
                <input type="datetime-local" class="form-control" name="created_at" value="${now}" required>
            </div>
            <h5>Позиции</h5>
            <div id="items-container">
                <div class="row mb-2 item-row">
                    <div class="col-md-6">
                        <select class="form-select product-select" required>
                            <option value="">Выберите товар</option>
                            ${products.map(p => `<option value="${p.id}">${p.name} (в наличии: ${p.quantity_at_storage} шт.)</option>`).join('')}
                        </select>
                    </div>
                    <div class="col-md-4">
                        <input type="number" class="form-control quantity-input" placeholder="Количество" min="1" required>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-item" style="display:none;">×</button>
                    </div>
                </div>
            </div>
            <button type="button" class="btn btn-secondary mb-3" onclick="addItemRow()">+ Добавить товар</button>
            <br>
            <button type="submit" class="btn btn-success">Создать чек</button>
            <button type="button" class="btn btn-secondary" onclick="renderSales()">Отмена</button>
        </form>
    `;
    contentArea.innerHTML = html;

    // Показать кнопки удаления для всех строк, кроме последней
    updateRemoveButtons();
    
    document.getElementById('receipt-form').addEventListener('submit', submitReceipt);
};

window.addItemRow = function() {
    const container = document.getElementById('items-container');
    const firstRow = container.querySelector('.item-row');
    const newRow = firstRow.cloneNode(true);
    newRow.querySelector('.product-select').value = '';
    newRow.querySelector('.quantity-input').value = '';
    container.appendChild(newRow);
    updateRemoveButtons();
};

function updateRemoveButtons() {
    const rows = document.querySelectorAll('.item-row');
    rows.forEach((row, index) => {
        const btn = row.querySelector('.remove-item');
        if (rows.length > 1) {
            btn.style.display = 'inline-block';
            btn.onclick = () => {
                row.remove();
                updateRemoveButtons();
            };
        } else {
            btn.style.display = 'none';
        }
    });
}

async function submitReceipt(e) {
    e.preventDefault();
    const created_at = document.querySelector('input[name="created_at"]').value;
    if (!created_at) {
        alert('Введите дату');
        return;
    }
    const isoDate = new Date(created_at).toISOString();

    // Собираем позиции
    const rows = document.querySelectorAll('.item-row');
    const items = [];
    for (const row of rows) {
        const productId = row.querySelector('.product-select').value;
        const quantity = row.querySelector('.quantity-input').value;
        if (!productId || !quantity || quantity < 1) {
            alert('Заполните все позиции корректно');
            return;
        }
        items.push({ id_product: parseInt(productId), quintity: parseInt(quantity) });
    }

    try {
        // 1. Создаём чек
        const receiptParams = new URLSearchParams();
        receiptParams.append('created_at', isoDate);
        const receipt = await apiRequest(`/receipts/?${receiptParams.toString()}`, 'POST');
        const receiptId = receipt.id;

        // 2. Добавляем все позиции
        for (const item of items) {
            const saleParams = new URLSearchParams();
            saleParams.append('id_product', item.id_product);
            saleParams.append('quintity', item.quintity);
            saleParams.append('receipt_id', receiptId);
            await apiRequest(`/sales/?${saleParams.toString()}`, 'POST');
        }

        renderSales();
    } catch (error) {
        alert('Ошибка создания продажи: ' + error.message);
    }
}

// ------------------- Чеки -------------------
async function renderReceipts() {
    const receipts = await apiRequest('/receipts/');
    let html = `<h2>Чеки</h2>
        <table class="table"><thead><tr><th>ID</th><th>Дата создания</th><th>Сотрудник</th><th></th></tr></thead><tbody>`;
    receipts.forEach(r => {
        const employee = r.employee;
        const empName = employee ? `${employee.name} ${employee.surname}` : '—';
        html += `<tr>
            <td>${r.id}</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
            <td>${empName}</td>
            <td><button class="btn btn-sm btn-outline-info" onclick="toggleReceiptDetails(${r.id}, this)">Состав</button></td>
        </tr>`;
        html += `<tr id="receipt-details-${r.id}" style="display:none;"><td colspan="4"><div class="p-3 bg-light">Загрузка...</div></td></tr>`;
    });
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

// ------------------- Должности -------------------
async function renderJobs() {
    const [jobs, roots] = await Promise.all([
        apiRequest('/jobs/'),
        apiRequest('/roots/')
    ]);
    let html = `<h2>Должности</h2>`;
    if (currentPermissions.add_jobs) {
        html += `<button class="btn btn-primary mb-3" onclick="showAddJobForm()">Добавить должность</button>`;
    }
    html += `<table class="table"><thead><tr><th>ID</th><th>Название</th><th>Набор прав (ID)</th></tr></thead><tbody>`;
    jobs.forEach(j => html += `<tr><td>${j.id}</td><td>${j.name}</td><td>${j.root_id}</td></tr>`);
    html += '</tbody></table>';
    contentArea.innerHTML = html;
}

window.showAddJobForm = async function() {
    if (!currentPermissions.add_jobs) {
        alert('Недостаточно прав');
        return;
    }
    const roots = await apiRequest('/roots/');
    const rootsOptions = roots.map(r => `<option value="${r.id}">ID ${r.id} – продажи: ${r.make_sales}, кат.: ${r.add_categories}, тов.: ${r.add_products}, ред.тов.: ${r.redact_products}, должн.: ${r.add_jobs}, босс: ${r.add_boss}</option>`).join('');

    const html = `
        <h3>Добавить должность</h3>
        <form onsubmit="addJob(event)">
            <div class="mb-3">
                <label>Название</label>
                <input type="text" class="form-control" name="name" required>
            </div>
            <div class="mb-3">
                <label>Выберите набор прав</label>
                <select class="form-select" id="existing-roots" onchange="toggleCustomRoots()">
                    <option value="">-- Выберите существующий --</option>
                    ${rootsOptions}
                    <option value="custom">Создать новый набор...</option>
                </select>
            </div>
            <div id="custom-roots-block" style="display:none;">
                <h5>Права нового набора</h5>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-make_sales"><label class="form-check-label">Продажи</label></div>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-add_categories"><label class="form-check-label">Добавление категорий</label></div>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-add_products"><label class="form-check-label">Добавление товаров</label></div>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-redact_products"><label class="form-check-label">Редактирование товаров</label></div>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-add_jobs"><label class="form-check-label">Добавление должностей</label></div>
                <div class="form-check"><input class="form-check-input" type="checkbox" id="perm-add_boss"><label class="form-check-label">Назначение руководителей</label></div>
            </div>
            <button type="submit" class="btn btn-success mt-3">Сохранить</button>
            <button type="button" class="btn btn-secondary mt-3" onclick="renderJobs()">Отмена</button>
        </form>
    `;
    contentArea.innerHTML = html;
};

window.toggleCustomRoots = function() {
    const select = document.getElementById('existing-roots');
    const customBlock = document.getElementById('custom-roots-block');
    customBlock.style.display = (select.value === 'custom') ? 'block' : 'none';
};

window.addJob = async function(e) {
    e.preventDefault();
    const name = document.querySelector('input[name="name"]').value;
    const select = document.getElementById('existing-roots');
    const selectedValue = select.value;

    let rootId;

    if (selectedValue === 'custom') {
        const newPerms = {
            make_sales: document.getElementById('perm-make_sales').checked,
            add_categories: document.getElementById('perm-add_categories').checked,
            add_products: document.getElementById('perm-add_products').checked,
            redact_products: document.getElementById('perm-redact_products').checked,
            add_jobs: document.getElementById('perm-add_jobs').checked,
            add_boss: document.getElementById('perm-add_boss').checked
        };
        try {
            const result = await apiRequest('/roots/', 'POST', newPerms);
            rootId = result.id;
        } catch (error) {
            alert('Ошибка создания набора прав: ' + error.message);
            return;
        }
    } else {
        rootId = parseInt(selectedValue, 10);
    }

    if (!rootId) {
        alert('Выберите или создайте набор прав');
        return;
    }

    const params = new URLSearchParams();
    params.append('name', name);
    params.append('root_id', rootId);

    try {
        await apiRequest(`/jobs/?${params.toString()}`, 'POST');
        renderJobs();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
};

// ------------------- Управление -------------------
async function renderManager() {
    if (!currentUser || !currentUser.id) {
        contentArea.innerHTML = '<div class="alert alert-danger">Ошибка: не определён ID пользователя</div>';
        return;
    }
    const children = await apiRequest(`/manager/childrens/?boss_id=${currentUser.id}`);
    let html = `<h2>Управление подчиненными</h2><h4>Ваши подчиненные</h4>`;
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

window.toggleReceiptDetails = async function(receiptId, btn) {
    const detailsRow = document.getElementById(`receipt-details-${receiptId}`);
    if (!detailsRow) return;
    const isVisible = detailsRow.style.display !== 'none';
    if (isVisible) {
        detailsRow.style.display = 'none';
        btn.textContent = 'Состав';
        return;
    }
    // Показать строку и загрузить данные
    detailsRow.style.display = '';
    btn.textContent = 'Скрыть';
    const cell = detailsRow.querySelector('td');
    if (cell.dataset.loaded === 'true') return; // уже загружено
    try {
        // Новый URL: /sales/receipt/{receiptId}
        const sales = await apiRequest(`/sales/receipt/${receiptId}`);
        cell.innerHTML = renderSalesForReceipt(sales);
        cell.dataset.loaded = 'true';
    } catch (e) {
        cell.innerHTML = `<div class="alert alert-danger">Ошибка загрузки</div>`;
    }
};

function renderSalesForReceipt(sales) {
    if (!sales.length) return '<p>Нет позиций</p>';
    let html = '<table class="table table-sm"><thead><tr><th>Товар</th><th>Категория</th><th>Цена</th><th>Кол-во</th><th>Сумма</th></tr></thead><tbody>';
    sales.forEach(s => {
        const product = s.product;
        const cat = product?.category?.name || '—';
        const total = s.quintity * product.price;
        html += `<tr>
            <td>${product.name}</td><td>${cat}</td><td>${product.price} руб.</td><td>${s.quintity}</td><td>${total} руб.</td>
        </tr>`;
    });
    html += '</tbody></table>';
    return html;
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
        const receipt = s.receipt;
        const employee = receipt?.employee;
        const date = receipt?.created_at ? new Date(receipt.created_at).toLocaleString() : '—';
        table += `<tr><td>${s.id}</td><td>${product.name}</td><td>${s.quintity}</td>
            <td>${employee ? `${employee.name} ${employee.surname}` : '—'}</td><td>${date}</td></tr>`;
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
        select.innerHTML = jobs.map(j => `<option value="${j.id}">${j.name} (права: ${j.root_id})</option>`).join('');
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

// Глобальные функции
window.renderProducts = renderProducts;
window.renderCategories = renderCategories;
window.renderEmployees = renderEmployees;
window.renderSales = renderSales;
window.renderReceipts = renderReceipts;
window.renderJobs = renderJobs;
window.renderManager = renderManager;
window.showSection = showSection;
/*
 * Logika daftar data berbasis AJAX yang dipakai halaman Education, Experience,
 * dan Project. Bagian yang butuh tag template Django ({% url %}, perms) tetap
 * berada di <script> inline tiap halaman dan dikirim ke sini lewat config.
 *
 * Halaman yang memakainya harus punya elemen dengan id:
 *   loading, error, empty, grid, search-form, search-input
 * dan untuk akun yang boleh menambah data: add-modal, add-form
 */

const SEARCH_DEBOUNCE_DELAY = 300;
const DUMMY_UUID = '00000000-0000-0000-0000-000000000000';

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie.split(';').map(value => value.trim())
        .find(value => value.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function entityEndpoint(pattern, id) {
    return pattern.replace(DUMMY_UUID, id);
}

function closeAddModal() {
    const modal = document.getElementById('add-modal');
    if (modal) modal.hidePopover();
}

// Membaca bentuk error datar serializer ({"title": ["..."]}) atau error umum
// ({"detail": "..."}).
function apiErrorMessage(data, statusCode) {
    const messages = Object.values(data || {}).flat()
        .filter(value => typeof value === 'string');
    return messages.join(' ') || `Permintaan gagal (status ${statusCode}).`;
}

// Satu tempat untuk POST, PUT, PATCH, dan DELETE: method, JSON, token CSRF,
// dan error ditangani konsisten.
async function writeEntity(url, method, payload) {
    const response = await fetch(url, {
        method,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
    });

    if (response.status === 204) return null;

    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
    return data;
}

/**
 * config:
 *   listEndpoint     URL daftar; GET membaca, POST menambah
 *   detailEndpoint   template URL detail, dipakai DELETE
 *   starEndpoint     template URL star, dipakai POST
 *   searchParam      nama query parameter pencarian
 *   formFields       field form yang dikirim sebagai payload JSON
 *   booleanFields    field checkbox di dalam formFields (opsional)
 *   buildCard        fungsi(item) -> HTMLElement
 *   entityLabel      nama entitas pada pesan toast
 *   deleteConfirm    kalimat konfirmasi sebelum menghapus
 */
function initEntityList(config) {
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const emptyState = document.getElementById('empty');
    const gridContainer = document.getElementById('grid');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const addForm = document.getElementById('add-form');

    let searchDebounceTimer;
    let listAbortController;

    function displayPageSection({
        showLoading = false,
        showError = false,
        showEmpty = false,
        showGrid = false,
    }) {
        loadingState.classList.toggle('hide', !showLoading);
        errorState.classList.toggle('hide', !showError);
        emptyState.classList.toggle('hide', !showEmpty);
        gridContainer.classList.toggle('hide', !showGrid);
    }

    async function fetchEntities(searchQuery = '') {
        // AbortController mencegah hasil pencarian lama menimpa hasil terbaru.
        if (listAbortController) listAbortController.abort();
        listAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });

            const url = new URL(config.listEndpoint, window.location.origin);
            if (searchQuery) url.searchParams.set(config.searchParam, searchQuery);

            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: listAbortController.signal,
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const entityData = await response.json();
            gridContainer.replaceChildren(...entityData.map(config.buildCard));
            displayPageSection({
                showGrid: entityData.length > 0,
                showEmpty: entityData.length === 0,
            });
        } catch (error) {
            if (error.name === 'AbortError') return;
            console.error(error);
            displayPageSection({ showError: true });
        }
    }

    function searchEntities() {
        fetchEntities(searchInput.value.trim());
    }

    searchInput.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchEntities, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchEntities();
    });

    // Field dipilih eksplisit agar csrfmiddlewaretoken tidak ikut dianggap data
    // model. Checkbox yang tidak dicentang tidak muncul di FormData, dan field
    // opsional yang dikosongkan tidak dikirim karena field angka serta tanggal
    // menolak string kosong.
    function buildPayload() {
        const fields = new FormData(addForm);
        const booleanFields = config.booleanFields || [];
        const payload = {};

        config.formFields.forEach(name => {
            if (booleanFields.includes(name)) {
                payload[name] = fields.has(name);
                return;
            }
            const value = fields.get(name);
            if (value !== null && value !== '') payload[name] = value;
        });

        return payload;
    }

    async function addEntity(event) {
        event.preventDefault();

        const submitButton = addForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            await writeEntity(config.listEndpoint, 'POST', buildPayload());
            addForm.reset();
            closeAddModal();
            showToast('Berhasil', `Data ${config.entityLabel} berhasil ditambahkan.`, 'success');
            await fetchEntities(searchInput.value.trim());
        } catch (error) {
            showToast(`Gagal menambahkan ${config.entityLabel}`, error.message, 'error');
        } finally {
            submitButton.disabled = false;
        }
    }

    // Modal hanya dirender untuk akun yang berhak, jadi addForm bisa null.
    if (addForm) {
        addForm.addEventListener('submit', addEntity);
    }

    // Event delegation: tombol pada kartu yang baru dirender ikut tertangani.
    gridContainer.addEventListener('click', async function (event) {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;

        const action = button.dataset.action;
        if (action === 'delete' && !window.confirm(config.deleteConfirm)) return;

        button.disabled = true;
        try {
            if (action === 'star') {
                await writeEntity(
                    entityEndpoint(config.starEndpoint, button.dataset.id), 'POST');
                showToast('Berhasil', 'Status star diperbarui.', 'success');
            } else {
                await writeEntity(
                    entityEndpoint(config.detailEndpoint, button.dataset.id), 'DELETE');
                showToast('Berhasil', `Data ${config.entityLabel} berhasil dihapus.`, 'success');
            }
            await fetchEntities(searchInput.value.trim());
        } catch (error) {
            showToast('Permintaan gagal', error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    fetchEntities(searchInput.value.trim());
}

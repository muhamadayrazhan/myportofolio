/*
 * Logika daftar data berbasis AJAX yang dipakai halaman Education, Experience,
 * dan Project. Bagian yang butuh tag template Django ({% url %}, perms) tetap
 * berada di <script> inline tiap halaman dan dikirim ke sini lewat config.
 *
 * Halaman yang memakainya harus punya elemen dengan id:
 *   loading, error, empty, grid, search-form, search-input
 * dan, sesuai permission akun:
 *   add-modal + add-form    untuk menambah data
 *   edit-modal + edit-form  untuk mengubah data
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

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.hidePopover();
}

// Membaca bentuk error datar serializer ({"title": ["..."]}) atau error umum
// ({"detail": "..."}).
function apiErrorMessage(data, statusCode) {
    const messages = Object.values(data || {}).flat()
        .filter(value => typeof value === 'string');
    return messages.join(' ') || `Permintaan gagal (status ${statusCode}).`;
}

async function readEntity(url) {
    const response = await fetch(url, { headers: { 'Accept': 'application/json' } });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
    return data;
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
 *   detailEndpoint   template URL detail, dipakai GET, PATCH, dan DELETE
 *   starEndpoint     template URL star, dipakai POST
 *   searchParam      nama query parameter pencarian
 *   formFields       field form yang dikirim sebagai payload JSON
 *   booleanFields    field checkbox di dalam formFields (opsional)
 *   nullableFields   field di dalam formFields yang dikosongkan dengan null,
 *                    bukan string kosong (opsional)
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
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-form');

    const booleanFields = config.booleanFields || [];
    const nullableFields = config.nullableFields || [];

    let searchDebounceTimer;
    let listAbortController;
    let editingId = null;

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
    // model. Checkbox yang tidak dicentang tidak muncul di FormData.
    //
    // omitEmpty dipakai saat menambah: field opsional yang dikosongkan tidak
    // dikirim, karena field angka dan tanggal menolak string kosong. Saat
    // mengubah, field tetap dikirim supaya isinya benar-benar bisa dihapus,
    // memakai null untuk field di nullableFields dan string kosong untuk sisanya.
    function buildPayload(formElement, omitEmpty) {
        const fields = new FormData(formElement);
        const payload = {};

        config.formFields.forEach(name => {
            if (booleanFields.includes(name)) {
                payload[name] = fields.has(name);
                return;
            }

            const value = fields.get(name);
            if (value !== null && value !== '') {
                payload[name] = value;
            } else if (!omitEmpty) {
                payload[name] = nullableFields.includes(name) ? null : '';
            }
        });

        return payload;
    }

    function fillForm(formElement, item) {
        config.formFields.forEach(name => {
            const input = formElement.elements[name];
            if (!input) return;

            if (booleanFields.includes(name)) {
                input.checked = Boolean(item[name]);
            } else {
                input.value = item[name] ?? '';
            }
        });
    }

    async function addEntity(event) {
        event.preventDefault();

        const submitButton = addForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            await writeEntity(config.listEndpoint, 'POST', buildPayload(addForm, true));
            addForm.reset();
            closeModal('add-modal');
            showToast('Berhasil', `Data ${config.entityLabel} berhasil ditambahkan.`, 'success');
            await fetchEntities(searchInput.value.trim());
        } catch (error) {
            showToast(`Gagal menambahkan ${config.entityLabel}`, error.message, 'error');
        } finally {
            submitButton.disabled = false;
        }
    }

    async function editEntity(event) {
        event.preventDefault();
        if (!editingId) return;

        const submitButton = editForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            await writeEntity(
                entityEndpoint(config.detailEndpoint, editingId),
                'PATCH',
                buildPayload(editForm, false),
            );
            closeModal('edit-modal');
            showToast('Berhasil', `Data ${config.entityLabel} berhasil diperbarui.`, 'success');
            await fetchEntities(searchInput.value.trim());
        } catch (error) {
            showToast(`Gagal memperbarui ${config.entityLabel}`, error.message, 'error');
        } finally {
            submitButton.disabled = false;
        }
    }

    // Modal hanya dirender untuk akun yang berhak, jadi kedua form bisa null.
    if (addForm) addForm.addEventListener('submit', addEntity);
    if (editForm) editForm.addEventListener('submit', editEntity);

    // Event delegation: tombol pada kartu yang baru dirender ikut tertangani.
    gridContainer.addEventListener('click', async function (event) {
        const button = event.target.closest('button[data-action]');
        if (!button || button.disabled) return;

        const action = button.dataset.action;
        if (action === 'edit' && !editForm) return;
        if (action === 'delete' && !window.confirm(config.deleteConfirm)) return;

        button.disabled = true;
        try {
            if (action === 'star') {
                await writeEntity(
                    entityEndpoint(config.starEndpoint, button.dataset.id), 'POST');
                showToast('Berhasil', 'Status star diperbarui.', 'success');
                await fetchEntities(searchInput.value.trim());
            } else if (action === 'edit') {
                // Data diambil ulang dari endpoint detail supaya form berisi
                // nilai terbaru, bukan nilai dari daftar yang mungkin usang.
                const item = await readEntity(
                    entityEndpoint(config.detailEndpoint, button.dataset.id));
                editingId = button.dataset.id;
                fillForm(editForm, item);
                editModal.showPopover();
            } else {
                await writeEntity(
                    entityEndpoint(config.detailEndpoint, button.dataset.id), 'DELETE');
                showToast('Berhasil', `Data ${config.entityLabel} berhasil dihapus.`, 'success');
                await fetchEntities(searchInput.value.trim());
            }
        } catch (error) {
            showToast('Permintaan gagal', error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    fetchEntities(searchInput.value.trim());
}

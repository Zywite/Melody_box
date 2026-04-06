let allSongs = [];
let filteredSongs = [];
let currentPage = 'home';
let token = localStorage.getItem('token');
let currentUser = localStorage.getItem('username');

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.addEventListener('input', debounce(handleSearch, 300));

    if (token && currentUser) {
        showApp();
        loadLibrary();
    } else {
        showAuthModal();
    }

    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.addEventListener('change', handleFileSelect);
});

function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

async function login() {
    const email = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    if (!email || !password) { alert('Completa todos los campos'); return; }

    try {
        const data = await api.login(email, password);
        token = data.access_token;
        currentUser = data.username;
        localStorage.setItem('username', currentUser);
        showApp();
        loadLibrary();
    } catch (error) {
        showToast('Error de inicio de sesión', 'Usuario o contraseña incorrecta', 'error');
    }
}

async function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm').value;

    if (!username || !email || !password || !confirm) { alert('Completa todos los campos'); return; }
    if (password !== confirm) { alert('Las contraseñas no coinciden'); return; }

    try {
        await api.register(username, email, password);
        showToast('Registro exitoso', 'Ahora puedes iniciar sesión', 'success');
        toggleAuthForm();
    } catch (error) {
        showToast('Error en el registro', error.message, 'error');
    }
}

function logout() {
    api.logout();
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    token = null;
    currentUser = null;
    showAuthModal();
}

function toggleAuthForm() {
    document.getElementById('login-form').classList.toggle('hidden');
    document.getElementById('register-form').classList.toggle('hidden');
    document.querySelectorAll('.auth-form input').forEach(i => i.value = '');
}

function showAuthModal() {
    document.getElementById('auth-modal').classList.remove('hidden');
    document.getElementById('app-content').classList.add('hidden');
}

function showApp() {
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('app-content').classList.remove('hidden');
    const el = document.getElementById('welcome-user');
    if (el) el.textContent = currentUser;
}

function showPage(name) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.mobile-nav-item').forEach(n => n.classList.remove('active'));

    const page = document.getElementById(name);
    if (page) page.classList.add('active');

    const nav = document.querySelector(`.nav-item[data-page="${name}"]`);
    if (nav) nav.classList.add('active');

    const mobileNav = document.querySelector(`.mobile-nav-item[data-page="${name}"]`);
    if (mobileNav) mobileNav.classList.add('active');

    currentPage = name;

    if (name === 'library') loadLibrary();
    else if (name === 'playlists') loadPlaylists();
    else if (name === 'home') loadStats();
}

function showToast(title, message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
        error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>',
        info: '<svg class="toast-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'
    };

    toast.innerHTML = `${icons[type] || icons.info}
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            ${message ? `<div class="toast-message">${message}</div>` : ''}
        </div>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

async function loadStats() {
    try {
        const songs = await api.getSongs();
        const playlists = await api.getPlaylists();
        const audioCount = songs.filter(s => s.media_type !== 'video').length;
        const videoCount = songs.filter(s => s.media_type === 'video').length;

        const s = document.getElementById('stat-songs');
        const v = document.getElementById('stat-videos');
        const p = document.getElementById('stat-playlists');
        if (s) s.textContent = audioCount;
        if (v) v.textContent = videoCount;
        if (p) p.textContent = playlists.length;
    } catch (e) { console.error(e); }
}

async function loadLibrary() {
    try {
        allSongs = await api.getSongs();
        filteredSongs = [...allSongs];
        displaySongs(filteredSongs);
        loadStats();
    } catch (e) { console.error(e); }
}

function filterLibrary(type) {
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.filter-tab[data-filter="${type}"]`)?.classList.add('active');

    filteredSongs = type === 'all'
        ? [...allSongs]
        : allSongs.filter(s => s.media_type === type);
    displaySongs(filteredSongs);
}

function displaySongs(songs) {
    const container = document.getElementById('library-content');
    if (!container) return;

    if (songs.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px">No hay archivos aún. Sube música o video.</p>';
        return;
    }

    container.innerHTML = songs.map(song => {
        const isVid = song.media_type === 'video';
        const icon = isVid
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>'
            : '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55C7.79 13 6 14.79 6 17s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>';

        return `
        <div class="media-item" data-id="${song.id}">
            <div class="media-art">${icon}</div>
            <div class="media-info">
                <div class="media-title">${song.title}</div>
                <div class="media-subtitle">${song.artist}${song.album ? ' • ' + song.album : ''}</div>
            </div>
            <span class="media-type-badge ${isVid ? 'badge-video' : 'badge-audio'}">${isVid ? 'Video' : 'Audio'}</span>
            <span class="media-duration">${formatDuration(song.duration)}</span>
            <div class="media-actions">
                <button class="action-btn" onclick="event.stopPropagation(); playMedia('${song.id}')" title="Reproducir">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                </button>
                <button class="action-btn" onclick="event.stopPropagation(); deleteMedia('${song.id}')" title="Eliminar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
            </div>
        </div>`;
    }).join('');

    container.querySelectorAll('.media-item').forEach(item => {
        item.addEventListener('click', () => playMedia(item.dataset.id));
    });
}

function playMedia(id) {
    const song = allSongs.find(s => s.id === id);
    if (!song) return;
    player.setPlaylist(allSongs);
    player.currentIndex = allSongs.indexOf(song);
    player.play(song);
}

async function deleteMedia(id) {
    if (!confirm('¿Eliminar este archivo permanentemente?')) return;
    try {
        await api.request(`/songs/${id}`, { method: 'DELETE' });
        allSongs = allSongs.filter(s => s.id !== id);
        filteredSongs = filteredSongs.filter(s => s.id !== id);
        displaySongs(filteredSongs);
        loadStats();
        showToast('Archivo eliminado', 'El archivo ha sido eliminado correctamente', 'success');
    } catch (e) {
        showToast('Error al eliminar', e.message, 'error');
    }
}

async function loadPlaylists() {
    try {
        const playlists = await api.getPlaylists();
        const container = document.getElementById('playlists-list');
        if (!container) return;

        if (playlists.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px;grid-column:1/-1">No tienes playlists aún</p>';
            return;
        }

        container.innerHTML = playlists.map(pl => `
            <div class="playlist-card" onclick="viewPlaylist('${pl.id}')">
                <div class="playlist-card-art">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="white" opacity="0.8"><path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/></svg>
                </div>
                <div class="playlist-card-name">${pl.name}</div>
                <div class="playlist-card-desc">${pl.description || ''}</div>
                <div class="playlist-card-count">${pl.songs?.length || 0} canciones</div>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
}

async function createPlaylist() {
    const name = prompt('Nombre de la playlist:');
    if (!name) return;
    const desc = prompt('Descripción (opcional):') || '';
    try {
        await api.createPlaylist(name, desc);
        loadPlaylists();
    } catch (e) { alert('Error: ' + e.message); }
}

async function viewPlaylist(id) {
    try {
        const pl = await api.getPlaylist(id);
        showPage('home');
        document.querySelector('#home .page-header h1').textContent = pl.name;
        if (pl.description) {
            document.querySelector('#home .page-header').insertAdjacentHTML('afterend',
                `<p style="color:var(--text-secondary);margin-bottom:20px">${pl.description}</p>`);
        }
        if (pl.songs && pl.songs.length > 0) {
            const songIds = pl.songs.map(ps => ps.song_id);
            const songs = allSongs.filter(s => songIds.includes(s.id));
            songs.sort((a, b) => {
                const pa = pl.songs.find(ps => ps.song_id === a.id)?.position || 0;
                const pb = pl.songs.find(ps => ps.song_id === b.id)?.position || 0;
                return pa - pb;
            });
            displaySongs(songs);
        }
    } catch (e) { alert('No se pudo cargar la playlist'); }
}

async function handleSearch(e) {
    const query = e.target.value;
    const container = document.getElementById('search-results');
    if (query.length < 2) { container.innerHTML = ''; return; }

    try {
        const results = await api.searchSongs(query);
        if (results.length === 0) {
            container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px">Sin resultados</p>';
            return;
        }

        container.innerHTML = results.map(song => {
            const isVid = song.media_type === 'video';
            const icon = isVid
                ? '<svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>'
                : '<svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55C7.79 13 6 14.79 6 17s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>';
            return `
            <div class="media-card" onclick="playMedia('${song.id}')">
                <div class="media-card-art">${icon}</div>
                <div class="media-card-title">${song.title}</div>
                <div class="media-card-subtitle">${song.artist}</div>
            </div>`;
        }).join('');
    } catch (e) { console.error(e); }
}

function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('upload-zone').classList.add('drag-over');
}

function handleDragLeave(e) {
    document.getElementById('upload-zone').classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    document.getElementById('upload-zone').classList.remove('drag-over');
    uploadFiles(e.dataTransfer.files);
}

async function handleFileSelect(e) {
    uploadFiles(e.target.files);
}

async function uploadFiles(files) {
    const progressDiv = document.getElementById('upload-progress');
    progressDiv.innerHTML = '';

    const defArtist = prompt('Artista / Creador por defecto para todos los archivos:', 'Desconocido') || 'Desconocido';
    const defAlbum = prompt('Álbum / Colección (opcional, Enter para saltar):', '') || '';

    for (const file of files) {
        const name = file.name.replace(/\.[^/.]+$/, '');
        const title = prompt(`Título para "${name}":`, name);
        if (!title) continue;

        try {
            await api.uploadSong(file, title, defArtist, defAlbum);
            const div = document.createElement('div');
            div.className = 'upload-progress-item';
            div.textContent = `✅ ${file.name} subido correctamente`;
            progressDiv.appendChild(div);
        } catch (e) {
            const div = document.createElement('div');
            div.className = 'upload-error-item';
            div.textContent = `❌ Error con ${file.name}: ${e.message}`;
            progressDiv.appendChild(div);
        }
    }

    loadLibrary();
}

function formatDuration(s) {
    if (!s) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
}

function togglePlay() { player.togglePlay(); }
function nextSong() { player.nextSong(); }
function previousSong() { player.previousSong(); }
function setVolume(v) { player.setVolume(v); }
function seekTo(e) { player.seekTo(e); }

function closeVideoFlyout() {
    player.closeFlyout();
}

function toggleMute() {
    const slider = document.getElementById('volume');
    const icon = document.getElementById('volume-icon');
    if (player.volume > 0) {
        player._prevVol = player.volume;
        player.setVolume(0);
        slider.value = 0;
        icon.innerHTML = '<path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>';
    } else {
        player.setVolume(player._prevVol || 0.7);
        slider.value = player._prevVol * 100 || 70;
        icon.innerHTML = '<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>';
    }
}

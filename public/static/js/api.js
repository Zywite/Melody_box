const API_BASE_URL = window.location.origin || 'http://localhost:8001';

class SpotifyAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {};

        if (!options.skipContentType) {
            headers['Content-Type'] = 'application/json';
        }

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        Object.assign(headers, options.headers || {});

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                }
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
            }

            const text = await response.text();
            return text ? JSON.parse(text) : {};
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        if (data.access_token) {
            this.token = data.access_token;
            localStorage.setItem('token', this.token);
        }
        return data;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('token');
    }

    async getSongs() {
        return this.request('/songs');
    }

    async getSong(songId) {
        return this.request(`/songs/${songId}`);
    }

    async searchSongs(query) {
        return this.request(`/songs/search?q=${encodeURIComponent(query)}`);
    }

    async uploadSong(file, title, artist, album = '') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        formData.append('artist', artist);
        if (album) formData.append('album', album);

        const url = `${this.baseUrl}/songs/upload`;
        const headers = {};
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async getPlaylists() {
        return this.request('/playlists');
    }

    async getPlaylist(playlistId) {
        return this.request(`/playlists/${playlistId}`);
    }

    async createPlaylist(name, description = '') {
        return this.request('/playlists', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
    }

    async addSongToPlaylist(playlistId, songId) {
        return this.request(`/playlists/${playlistId}/songs`, {
            method: 'POST',
            body: JSON.stringify({ song_id: songId })
        });
    }

    async removeSongFromPlaylist(playlistId, songId) {
        return this.request(`/playlists/${playlistId}/songs/${songId}`, {
            method: 'DELETE'
        });
    }

    async getFavorites() {
        return this.request('/favorites');
    }

    async addFavorite(songId) {
        return this.request('/favorites', {
            method: 'POST',
            body: JSON.stringify({ song_id: songId })
        });
    }

    async removeFavorite(songId) {
        return this.request(`/favorites/${songId}`, {
            method: 'DELETE'
        });
    }

    streamUrl(mediaId) {
        return `${this.baseUrl}/songs/${mediaId}/stream`;
    }
}

const api = new SpotifyAPI();

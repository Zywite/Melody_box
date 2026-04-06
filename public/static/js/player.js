class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.videoEl = document.getElementById('video-player');
        this.flyoutVideoEl = document.getElementById('flyout-video-player');
        this.currentMedia = null;
        this.isPlaying = false;
        this.isVideo = false;
        this.playlist = [];
        this.currentIndex = 0;
        this.volume = 0.7;

        this.audio.addEventListener('ended', () => this.nextSong());
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => this.updateDuration());

        if (this.videoEl) {
            this.videoEl.addEventListener('ended', () => this.nextSong());
            this.videoEl.addEventListener('timeupdate', () => this.updateProgress());
            this.videoEl.addEventListener('loadedmetadata', () => this.updateDuration());
        }

        if (this.flyoutVideoEl) {
            this.flyoutVideoEl.addEventListener('ended', () => this.onVideoEnded());
            this.flyoutVideoEl.addEventListener('play', () => this.onVideoPlay());
            this.flyoutVideoEl.addEventListener('pause', () => this.onVideoPause());
        }

        this.audio.volume = this.volume;
    }

    play(media) {
        this.currentMedia = media;
        this.isVideo = media.media_type === 'video';
        const streamUrl = api.streamUrl(media.id);

        this.audio.pause();

        if (this.isVideo) {
            this.closeFlyout();
            this.flyoutVideoEl.src = streamUrl;
            this.flyoutVideoEl.volume = this.volume;
            
            const flyoutTitle = document.getElementById('flyout-video-title');
            if (flyoutTitle) flyoutTitle.textContent = media.title;
            
            document.getElementById('video-flyout')?.classList.remove('hidden');
            document.getElementById('video-section')?.classList.add('hidden');
            
            setTimeout(() => this.flyoutVideoEl.play(), 100);
        } else {
            this.closeFlyout();
            document.getElementById('video-section')?.classList.add('hidden');
            this.audio.src = streamUrl;
            this.audio.play();
        }

        this.isPlaying = true;
        this.updateUI();
    }

    onVideoPlay() {
        this.isPlaying = true;
        this.updateUI();
    }

    onVideoPause() {
        this.isPlaying = false;
        this.updateUI();
    }

    onVideoEnded() {
        this.nextSong();
    }

    closeFlyout() {
        if (this.flyoutVideoEl) {
            this.flyoutVideoEl.pause();
            this.flyoutVideoEl.src = '';
        }
        const flyout = document.getElementById('video-flyout');
        if (flyout) flyout.classList.add('hidden');
    }

    togglePlay() {
        if (this.isVideo && this.flyoutVideoEl) {
            if (this.isPlaying) { this.flyoutVideoEl.pause(); }
            else { this.flyoutVideoEl.play(); }
        } else {
            if (this.isPlaying) { this.audio.pause(); }
            else { this.audio.play(); }
        }
        this.isPlaying = !this.isPlaying;
        this.updateUI();
    }

    pause() {
        this.audio.pause();
        if (this.flyoutVideoEl) this.flyoutVideoEl.pause();
        this.isPlaying = false;
        this.updateUI();
    }

    nextSong() {
        this.closeFlyout();
        if (this.currentIndex < this.playlist.length - 1) {
            this.currentIndex++;
            this.play(this.playlist[this.currentIndex]);
        }
    }

    previousSong() {
        this.closeFlyout();
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.play(this.playlist[this.currentIndex]);
        }
    }

    setVolume(value) {
        this.volume = value / 100;
        this.audio.volume = this.volume;
        if (this.flyoutVideoEl) this.flyoutVideoEl.volume = this.volume;
    }

    seekTo(event) {
        const el = this.isVideo ? this.flyoutVideoEl : this.audio;
        if (!el || !el.duration) return;
        const rect = event.currentTarget.getBoundingClientRect();
        const pct = (event.clientX - rect.left) / rect.width;
        el.currentTime = pct * el.duration;
    }

    updateProgress() {
        if (this.isVideo) return;
        
        const el = this.audio;
        if (!el || !el.duration) return;
        const pct = (el.currentTime / el.duration) * 100;
        const fill = document.getElementById('progress-fill');
        if (fill) fill.style.width = pct + '%';

        const cur = document.getElementById('current-time');
        if (cur) cur.textContent = this.formatTime(el.currentTime);
    }

    updateDuration() {
        if (this.isVideo) return;
        
        const el = this.audio;
        if (!el || !el.duration) return;
        const total = document.getElementById('total-time');
        if (total) total.textContent = this.formatTime(el.duration);
    }

    updateUI() {
        const playBtn = document.getElementById('play-btn');
        const playIcon = document.getElementById('play-icon');
        if (playIcon) {
            playIcon.innerHTML = this.isPlaying
                ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'
                : '<path d="M8 5v14l11-7z"/>';
        }

        const titleEl = document.getElementById('player-title');
        const artistEl = document.getElementById('player-artist');
        const nowTitle = document.getElementById('current-song-title');
        const nowArtist = document.getElementById('current-song-artist');
        const playerBar = document.getElementById('player-bar');

        if (this.currentMedia) {
            if (titleEl) titleEl.textContent = this.currentMedia.title;
            if (artistEl) artistEl.textContent = this.currentMedia.artist;
            if (nowTitle) nowTitle.textContent = this.currentMedia.title;
            if (nowArtist) nowArtist.textContent = this.currentMedia.artist;
            if (!this.isVideo) playerBar?.classList.remove('hidden');
        }
    }

    setPlaylist(media) {
        this.playlist = media;
        this.currentIndex = 0;
    }

    formatTime(s) {
        if (!s || isNaN(s)) return '0:00';
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60);
        return `${m}:${sec.toString().padStart(2, '0')}`;
    }
}

const player = new MusicPlayer();

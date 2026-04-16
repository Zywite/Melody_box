import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  const currentSong = ref(null)
  const playlist = ref([])
  const currentIndex = ref(-1)
  const isPlaying = ref(false)
  const volume = ref(0.7)
  const currentTime = ref(0)
  const duration = ref(0)
  const isMuted = ref(false)
  const prevVolume = ref(0.7)

  const audio = ref(null)
  const videoElement = ref(null)

  const hasCurrent = computed(() => !!currentSong.value)
  const isVideo = computed(() => {
    if (!currentSong.value) return false
    return currentSong.value.media_type === 'video'
  })
  const showVideoFlyout = ref(false)
  const showModeSelector = ref(false)
  const progress = computed(() => duration.value ? (currentTime.value / duration.value) * 100 : 0)

  function initAudio(element) {
    audio.value = element
    audio.value.volume = volume.value
    audio.value.addEventListener('timeupdate', updateTime)
    audio.value.addEventListener('loadedmetadata', updateDuration)
    audio.value.addEventListener('ended', playNext)
  }

  function updateTime() {
    if (audio.value && audio.value.currentTime) {
      currentTime.value = audio.value.currentTime
    }
  }

  function updateDuration() {
    if (audio.value && audio.value.duration && isFinite(audio.value.duration)) {
      duration.value = audio.value.duration
    }
  }

  function playNext() {
    if (currentIndex.value < playlist.value.length - 1) {
      currentIndex.value++
      play(playlist.value[currentIndex.value])
    } else {
      isPlaying.value = false
    }
  }

  function playPrev() {
    if (currentIndex.value > 0) {
      currentIndex.value--
      play(playlist.value[currentIndex.value])
    }
  }

  function setPlaylist(list, startIndex = 0) {
    playlist.value = list
    currentIndex.value = startIndex
    if (list.length > 0) {
      play(list[startIndex])
    }
  }

  function play(song, songList = null) {
    showModeSelector.value = false
    closeVideoFlyout()

    if (songList && songList.length > 0) {
      playlist.value = songList
      currentIndex.value = songList.findIndex(s => s.id === song.id)
    } else if (playlist.value.length === 0) {
      playlist.value = [song]
      currentIndex.value = 0
    } else {
      currentIndex.value = playlist.value.findIndex(s => s.id === song.id)
    }
    
    currentSong.value = song
    isPlaying.value = true

    if (song.media_type === 'video') {
      showSelectorForVideo(song, songList)
    } else if (audio.value) {
      audio.value.src = `/songs/${song.id}/stream`
      audio.value.play().catch(e => console.error('Play error:', e))
    }
  }

  function playSong(song, songList = null) {
    if (song.media_type === 'video') {
      showSelectorForVideo(song, songList)
    } else {
      play(song, songList)
    }
  }

  function playWithMode(song, mode, songList = null) {
    showModeSelector.value = false
    
    if (songList && songList.length > 0) {
      playlist.value = songList
      currentIndex.value = songList.findIndex(s => s.id === song.id)
    } else if (playlist.value.length === 0) {
      playlist.value = [song]
      currentIndex.value = 0
    } else {
      currentIndex.value = playlist.value.findIndex(s => s.id === song.id)
    }
    
    currentSong.value = song
    isPlaying.value = true

    if (mode === 'video' && song.media_type === 'video') {
      showVideoFlyout.value = true
    } else {
      if (audio.value) {
        audio.value.src = `/songs/${song.id}/stream`
        audio.value.play().catch(e => console.error('Play error:', e))
      }
    }
  }

  function showSelectorForVideo(song, songList = null) {
    closeVideoFlyout()
    cleanupAudio()
    
    if (songList && songList.length > 0) {
      playlist.value = songList
      currentIndex.value = songList.findIndex(s => s.id === song.id)
    } else if (playlist.value.length === 0) {
      playlist.value = [song]
      currentIndex.value = 0
    } else {
      currentIndex.value = playlist.value.findIndex(s => s.id === song.id)
    }
    
    currentSong.value = song
    isPlaying.value = true
    showModeSelector.value = true
  }

  function cleanupAudio() {
    if (audio.value) {
      audio.value.pause()
      audio.value.src = ''
    }
    currentTime.value = 0
    duration.value = 0
  }

  function switchToAudio() {
    if (currentSong.value) {
      cleanupAudio()
      showVideoFlyout.value = false
      if (audio.value) {
        audio.value.src = `/songs/${currentSong.value.id}/stream`
        audio.value.play().catch(e => console.error('Play error:', e))
      }
    }
  }

  function togglePlay() {
    if (!currentSong.value) return
    if (isPlaying.value) {
      audio.value?.pause()
      if (videoElement.value) videoElement.value.pause()
    } else {
      audio.value?.play()
      if (videoElement.value) videoElement.value.play()
    }
    isPlaying.value = !isPlaying.value
  }

  function pause() {
    audio.value?.pause()
    if (videoElement.value) videoElement.value.pause()
    isPlaying.value = false
  }

  function setVolume(val) {
    volume.value = val
    if (audio.value) audio.value.volume = val
    if (videoElement.value) videoElement.value.volume = val
    if (val > 0) isMuted.value = false
  }

  function toggleMute() {
    if (isMuted.value) {
      setVolume(prevVolume.value || 0.7)
    } else {
      prevVolume.value = volume.value
      setVolume(0)
    }
    isMuted.value = !isMuted.value
  }

  function seek(percent) {
    if (audio.value && duration.value) {
      audio.value.currentTime = (percent / 100) * duration.value
    }
  }

  function closeVideoFlyout() {
    if (videoElement.value) {
      videoElement.value.pause()
      videoElement.value = null
    }
    showVideoFlyout.value = false
  }

  function toggleVideoFlyout() {
    showVideoFlyout.value = !showVideoFlyout.value
  }

  function setVideoElement(element) {
    videoElement.value = element
  }

  function closeModeSelector() {
    showModeSelector.value = false
  }

  return {
    currentSong,
    playlist,
    currentIndex,
    isPlaying,
    volume,
    currentTime,
    duration,
    isMuted,
    hasCurrent,
    isVideo,
    showVideoFlyout,
    showModeSelector,
    progress,
    initAudio,
    setPlaylist,
    play,
    playSong,
    playWithMode,
    showSelectorForVideo,
    cleanupAudio,
    switchToAudio,
    togglePlay,
    pause,
    setVolume,
    toggleMute,
    seek,
    playNext,
    playPrev,
    closeVideoFlyout,
    toggleVideoFlyout,
    setVideoElement,
    closeModeSelector
  }
})
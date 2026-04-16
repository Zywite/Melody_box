import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  const currentSong = ref(null)
  const playlist = ref([])
  const originalPlaylist = ref([])
  const currentIndex = ref(-1)
  const isPlaying = ref(false)
  const volume = ref(0.7)
  const currentTime = ref(0)
  const duration = ref(0)
  const isMuted = ref(false)
  const prevVolume = ref(0.7)
  
  const shuffle = ref(false)
  const repeat = ref('none') // 'none', 'one', 'all'

  const audio = ref(null)
  const videoElement = ref(null)

  const hasCurrent = computed(() => !!currentSong.value)
  const isVideo = computed(() => {
    if (!currentSong.value) return false
    return currentSong.value.media_type === 'video'
  })
  const showVideoFlyout = ref(false)
  const showModeSelector = ref(false)
  const showQueue = ref(false)
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

  function getShuffledIndex() {
    if (playlist.value.length <= 1) return currentIndex.value
    let newIndex
    do {
      newIndex = Math.floor(Math.random() * playlist.value.length)
    } while (newIndex === currentIndex.value && playlist.value.length > 1)
    return newIndex
  }

  function playNext() {
    if (repeat.value === 'one') {
      if (audio.value) {
        audio.value.currentTime = 0
        audio.value.play().catch(e => console.error('Play error:', e))
      }
      return
    }
    
    if (shuffle.value) {
      currentIndex.value = getShuffledIndex()
    } else if (currentIndex.value < playlist.value.length - 1) {
      currentIndex.value++
    } else if (repeat.value === 'all') {
      currentIndex.value = 0
    } else {
      isPlaying.value = false
      return
    }
    play(playlist.value[currentIndex.value])
  }

  function playPrev() {
    if (currentTime.value > 3) {
      currentTime.value = 0
      if (audio.value) audio.value.currentTime = 0
      return
    }
    if (shuffle.value) {
      currentIndex.value = getShuffledIndex()
    } else if (currentIndex.value > 0) {
      currentIndex.value--
    } else if (repeat.value === 'all') {
      currentIndex.value = playlist.value.length - 1
    } else {
      currentTime.value = 0
      if (audio.value) audio.value.currentTime = 0
      return
    }
    play(playlist.value[currentIndex.value])
  }

  function toggleShuffle() {
    shuffle.value = !shuffle.value
    if (shuffle.value && originalPlaylist.value.length === 0) {
      originalPlaylist.value = [...playlist.value]
    }
  }

  function toggleRepeat() {
    const modes = ['none', 'all', 'one']
    const currentModeIndex = modes.indexOf(repeat.value)
    repeat.value = modes[(currentModeIndex + 1) % modes.length]
  }

  function setPlaylist(list, startIndex = 0) {
    playlist.value = list
    originalPlaylist.value = [...list]
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
      originalPlaylist.value = [...songList]
      currentIndex.value = songList.findIndex(s => s.id === song.id)
    } else if (playlist.value.length === 0) {
      playlist.value = [song]
      originalPlaylist.value = [song]
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

  function toggleQueue() {
    showQueue.value = !showQueue.value
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
    shuffle,
    repeat,
    showQueue,
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
    toggleShuffle,
    toggleRepeat,
    closeVideoFlyout,
    toggleVideoFlyout,
    setVideoElement,
    closeModeSelector,
    toggleQueue
  }
})
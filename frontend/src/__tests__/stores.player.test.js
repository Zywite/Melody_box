import { setActivePinia, createPinia } from 'pinia'
import { usePlayerStore } from '@/stores/player'
import { beforeEach, describe, expect, it, vi } from 'vitest'

beforeEach(() => {
  setActivePinia(createPinia())
})

const mockSong = { id: 1, title: 'Test Song', artist: 'Artist', media_type: 'audio' }
const mockSong2 = { id: 2, title: 'Song 2', artist: 'Artist 2', media_type: 'audio' }

describe('player store', () => {
  it('starts with no song', () => {
    const player = usePlayerStore()
    expect(player.hasCurrent).toBe(false)
    expect(player.isPlaying).toBe(false)
    expect(player.currentSong).toBeNull()
    expect(player.progress).toBe(0)
  })

  it('playSong sets current song and playlist', () => {
    const player = usePlayerStore()
    const playlist = [mockSong, mockSong2]

    player.playSong(mockSong, playlist)

    expect(player.currentSong).toEqual(mockSong)
    expect(player.isPlaying).toBe(true)
    expect(player.playlist).toEqual(playlist)
    expect(player.currentIndex).toBe(0)
  })

  it('playSong sets correct index for song in list', () => {
    const player = usePlayerStore()
    const playlist = [mockSong, mockSong2]

    player.playSong(mockSong2, playlist)

    expect(player.currentIndex).toBe(1)
  })

  it('togglePlay toggles isPlaying', () => {
    const player = usePlayerStore()
    player.currentSong = mockSong
    player.isPlaying = true

    player.togglePlay()
    expect(player.isPlaying).toBe(false)

    player.togglePlay()
    expect(player.isPlaying).toBe(true)
  })

  it('toggleShuffle toggles shuffle flag', () => {
    const player = usePlayerStore()
    expect(player.shuffle).toBe(false)

    player.toggleShuffle()
    expect(player.shuffle).toBe(true)

    player.toggleShuffle()
    expect(player.shuffle).toBe(false)
  })

  it('toggleRepeat cycles through modes', () => {
    const player = usePlayerStore()
    expect(player.repeat).toBe('none')

    player.toggleRepeat()
    expect(player.repeat).toBe('all')

    player.toggleRepeat()
    expect(player.repeat).toBe('one')

    player.toggleRepeat()
    expect(player.repeat).toBe('none')
  })

  it('setVolume updates volume', () => {
    const player = usePlayerStore()
    player.setVolume(0.5)
    expect(player.volume).toBe(0.5)
  })

  it('toggleMute toggles isMuted', () => {
    const player = usePlayerStore()
    player.setVolume(0.7)

    expect(player.isMuted).toBe(false)
    player.toggleMute()
    expect(player.isMuted).toBe(true)
    expect(player.volume).toBe(0)

    player.toggleMute()
    expect(player.isMuted).toBe(false)
    expect(player.volume).toBe(0.7)
  })

  it('progress is 0 when no duration', () => {
    const player = usePlayerStore()
    expect(player.progress).toBe(0)
  })

  it('playNext does nothing with empty playlist', () => {
    const player = usePlayerStore()
    player.playNext()
    expect(player.currentSong).toBeNull()
  })
})

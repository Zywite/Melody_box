import { setActivePinia, createPinia } from 'pinia'
import { useSongsStore } from '@/stores/songs'
import { useAuthStore } from '@/stores/auth'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockApi } = vi.hoisted(() => ({
  mockApi: {
    getSongs: vi.fn(),
    deleteSong: vi.fn(),
    searchSongs: vi.fn(),
  },
}))

vi.mock('@/composables/useApi', () => ({
  default: mockApi,
}))

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
  vi.clearAllMocks()
  sessionStorage.clear()
})

const mockSongs = [
  { id: 1, title: 'Song A', artist: 'Artist 1', media_type: 'audio' },
  { id: 2, title: 'Song B', artist: 'Artist 2', media_type: 'video' },
  { id: 3, title: 'Song C', artist: 'Artist 3', media_type: 'audio' },
]

describe('songs store', () => {
  it('starts empty', () => {
    const store = useSongsStore()
    expect(store.songs).toEqual([])
    expect(store.isLoading).toBe(false)
  })

  it('fetchSongs loads songs when authenticated', async () => {
    mockApi.getSongs.mockResolvedValue(mockSongs)

    const auth = useAuthStore()
    auth.token = 'valid-token'

    const store = useSongsStore()
    await store.fetchSongs(1, 50)

    expect(store.songs).toEqual(mockSongs)
    expect(store.isLoading).toBe(false)
  })

  it('filteredSongs returns all when filterType is all', () => {
    const store = useSongsStore()
    store.songs = mockSongs

    expect(store.filteredSongs).toEqual(mockSongs)
  })

  it('filteredSongs filters by media_type', () => {
    const store = useSongsStore()
    store.songs = mockSongs

    store.setFilter('video')
    expect(store.filteredSongs).toHaveLength(1)
    expect(store.filteredSongs[0].media_type).toBe('video')

    store.setFilter('audio')
    expect(store.filteredSongs).toHaveLength(2)
  })

  it('audioCount and videoCount are correct', () => {
    const store = useSongsStore()
    store.songs = mockSongs

    expect(store.audioCount).toBe(2)
    expect(store.videoCount).toBe(1)
  })

  it('upsertSong adds new song', () => {
    const store = useSongsStore()
    store.songs = [mockSongs[0]]

    store.upsertSong(mockSongs[1])
    expect(store.songs).toHaveLength(2)
  })

  it('upsertSong updates existing song', () => {
    const store = useSongsStore()
    store.songs = [mockSongs[0]]

    store.upsertSong({ id: 1, title: 'Updated Title' })
    expect(store.songs).toHaveLength(1)
    expect(store.songs[0].title).toBe('Updated Title')
  })

  it('removeSongLocal removes song by id', () => {
    const store = useSongsStore()
    store.songs = [...mockSongs]

    store.removeSongLocal(2)
    expect(store.songs).toHaveLength(2)
    expect(store.songs.find(s => s.id === 2)).toBeUndefined()
  })

  it('deleteSong calls api and removes locally', async () => {
    mockApi.deleteSong.mockResolvedValue(undefined)

    const store = useSongsStore()
    store.songs = [...mockSongs]

    await store.deleteSong(1)
    expect(mockApi.deleteSong).toHaveBeenCalledWith(1)
    expect(store.songs.find(s => s.id === 1)).toBeUndefined()
  })

  it('searchSongs returns empty for short queries', async () => {
    const store = useSongsStore()
    const result = await store.searchSongs('a')
    expect(result).toEqual([])
  })
})

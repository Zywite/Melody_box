import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useSongsStore } from './songs'
import { usePlaylistsStore } from './playlists'
import { useFavoritesStore } from './favorites'

export const useLibraryStore = defineStore('library', () => {
  const songsStore = useSongsStore()
  const playlistsStore = usePlaylistsStore()
  const favoritesStore = useFavoritesStore()

  const isLoading = computed(
    () => songsStore.isLoading || playlistsStore.isLoading
  )
  const error = computed(
    () => songsStore.error || playlistsStore.error || favoritesStore.error
  )

  return {
    songs: songsStore.songs,
    filteredSongs: songsStore.filteredSongs,
    audioCount: songsStore.audioCount,
    videoCount: songsStore.videoCount,
    filterType: songsStore.filterType,
    fetchSongs: songsStore.fetchSongs,
    deleteSong: songsStore.deleteSong,
    searchSongs: songsStore.searchSongs,
    setFilter: songsStore.setFilter,

    playlists: playlistsStore.playlists,
    playlistCount: playlistsStore.playlistCount,
    fetchPlaylists: playlistsStore.fetchPlaylists,
    createPlaylist: playlistsStore.createPlaylist,
    getPlaylist: playlistsStore.getPlaylist,

    favorites: favoritesStore.favorites,
    fetchFavorites: favoritesStore.fetchFavorites,
    addFavorite: favoritesStore.addFavorite,
    removeFavorite: favoritesStore.removeFavorite,

    isLoading,
    error,
  }
})

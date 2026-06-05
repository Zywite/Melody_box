import { useFavoritesStore } from '@/stores/favorites'

export function useFavorite() {
  const favoritesStore = useFavoritesStore()

  function isSongFavorite(songId) {
    return favoritesStore.favorites.some(f => f.song_id === songId)
  }

  async function toggleFavorite(song, { onSuccess, onError } = {}) {
    try {
      const isFav = favoritesStore.favorites.some(f => f.song_id === song.id)
      if (isFav) {
        await favoritesStore.removeFavorite(song.id)
        if (onSuccess) onSuccess('Eliminado de favoritos')
      } else {
        await favoritesStore.addFavorite(song.id)
        if (onSuccess) onSuccess('Agregado a favoritos')
      }
    } catch (e) {
      if (onError) onError(e.message || 'Error al cambiar favorito')
    }
  }

  return { isSongFavorite, toggleFavorite }
}

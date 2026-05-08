<template>
  <div class="faq-view">
    <div class="faq-header">
      <div class="header-icon">
        <HelpCircle :size="28" />
      </div>
      <h1 class="page-title">Preguntas Frecuentes</h1>
      <p class="page-subtitle">Todo lo que necesitas saber sobre MelodyBox</p>
    </div>

    <div class="faq-list">
      <div
        v-for="(item, index) in faqItems"
        :key="index"
        class="faq-item"
        :class="{ open: openIndex === index }"
        @click="toggleItem(index)"
      >
        <div class="faq-question">
          <span class="question-text">{{ item.question }}</span>
          <ChevronDown :size="20" class="chevron" />
        </div>
        <div class="faq-answer" v-if="openIndex === index">
          <p>{{ item.answer }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { HelpCircle, ChevronDown } from 'lucide-vue-next'

const openIndex = ref(null)

function toggleItem(index) {
  openIndex.value = openIndex.value === index ? null : index
}

const faqItems = [
  {
    question: '¿Cómo subir música a MelodyBox?',
    answer: 'Ve a la sección "Subir" en el menú lateral, selecciona uno o más archivos de audio desde tu computadora y haz clic en "Subir". Los formatos compatibles son MP3, WAV, FLAC, OGG, M4A, AAC y WMA. Una vez subida, la canción se analizará automáticamente para mostrarte su espectro de frecuencia (FFT).'
  },
  {
    question: '¿Cómo descargar música de YouTube?',
    answer: 'En la sección "Buscar", ingresa un término de búsqueda y ve a los resultados de YouTube. Puedes filtrar por duración (corto, medio, largo) y ordenar por relevancia, fecha o vistas. Selecciona el video que desees, elige formato (M4A o MP3) y calidad, y haz clic en "Descargar". La canción se agregará automáticamente a tu biblioteca.'
  },
  {
    question: '¿Qué es el análisis FFT y para qué sirve?',
    answer: 'FFT (Fast Fourier Transform) es un análisis que descompone una canción en sus frecuencias componentes. Te permite visualizar el espectro de frecuencias (graves, medios y agudos) y ver un espectrograma que muestra cómo cambian las frecuencias a lo largo del tiempo. Es útil para entender la composición sonora de tus canciones y apreciar detalles del audio.'
  },
  {
    question: '¿Cómo crear y gestionar playlists?',
    answer: 'En la sección "Biblioteca", selecciona una o más canciones y haz clic en "Agregar a playlist". Puedes crear una playlist nueva o agregar a una existente. También puedes ir a la sección "Playlists" para ver, editar y organizar todas tus listas de reproducción.'
  },
  {
    question: '¿Qué formatos de audio son compatibles?',
    answer: 'MelodyBox soporta los formatos MP3, WAV, FLAC, OGG, M4A, AAC y WMA. Para subir archivos desde tu computadora, todos estos formatos están permitidos. Las descargas de YouTube están disponibles en M4A y MP3 con varias calidades (128kbps, 192kbps, 256kbps y 320kbps).'
  },
  {
    question: '¿Cómo funciona el modo oscuro?',
    answer: 'Puedes alternar entre modo claro y oscuro usando el botón de sol/luna que aparece en la esquina inferior izquierda de la barra lateral (o en el menú en dispositivos móviles). Tu preferencia se guarda automáticamente y se recordará en tu próxima visita.'
  },
  {
    question: '¿Cómo buscar canciones en mi biblioteca?',
    answer: 'En la sección "Biblioteca" puedes buscar canciones por nombre. También puedes navegar por todas tus canciones ordenadas alfabéticamente. Cada canción muestra información como artista, duración y si tiene análisis FFT disponible.'
  },
  {
    question: '¿Dónde se almacenan mis canciones?',
    answer: 'Las canciones que subes o descargas se almacenan en el servidor en el directorio data/music/. Puedes acceder a ellas desde cualquier dispositivo iniciando sesión en tu cuenta de MelodyBox.'
  }
]
</script>

<style scoped>
.faq-view {
  padding: 32px;
  max-width: 800px;
  margin: 0 auto;
}

.faq-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.page-title {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  color: var(--text-secondary);
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition);
}

.faq-item:hover {
  border-color: var(--accent-light);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px var(--accent-glow);
}

.faq-item.open {
  border-color: var(--accent);
  box-shadow: 0 4px 15px var(--accent-glow);
}

.faq-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  gap: 16px;
}

.question-text {
  font-family: 'Nunito', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.4;
}

.chevron {
  color: var(--text-secondary);
  flex-shrink: 0;
  transition: transform var(--transition);
}

.faq-item.open .chevron {
  transform: rotate(180deg);
  color: var(--accent);
}

.faq-answer {
  padding: 0 24px 20px;
  animation: slideDown 0.2s ease;
}

.faq-answer p {
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .faq-view {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .faq-question {
    padding: 16px 18px;
  }

  .question-text {
    font-size: 0.95rem;
  }

  .faq-answer {
    padding: 0 18px 16px;
  }
}
</style>

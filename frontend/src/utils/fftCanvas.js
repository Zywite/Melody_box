const FALLBACK_THEME = {
  bgColor: '#ffe4ec',
  textColor: '#7a7a7a',
  accentColor: '#ff9ebb',
  accentLight: '#ffb7c5',
  secondaryColor: '#b19cd9',
}

export function readThemeColors() {
  if (typeof document === 'undefined') return { ...FALLBACK_THEME }
  const style = getComputedStyle(document.documentElement)
  return {
    bgColor: style.getPropertyValue('--bg-secondary').trim() || FALLBACK_THEME.bgColor,
    textColor: style.getPropertyValue('--text-secondary').trim() || FALLBACK_THEME.textColor,
    accentColor: style.getPropertyValue('--accent').trim() || FALLBACK_THEME.accentColor,
    accentLight: style.getPropertyValue('--accent-light').trim() || FALLBACK_THEME.accentLight,
    secondaryColor: style.getPropertyValue('--secondary').trim() || FALLBACK_THEME.secondaryColor,
  }
}

function getColor(value) {
  if (value < 0.25) {
    const t = value / 0.25
    return `rgb(0, ${Math.round(t * 255)}, ${Math.round(255 - t * 100)})`
  }
  if (value < 0.5) {
    const t = (value - 0.25) / 0.25
    return `rgb(0, ${Math.round(255 - t * 100)}, ${Math.round(155 + t * 100)})`
  }
  if (value < 0.75) {
    const t = (value - 0.5) / 0.25
    return `rgb(${Math.round(t * 255)}, ${Math.round(155 + t * 100)}, 0)`
  }
  const t = (value - 0.75) / 0.25
  return `rgb(255, ${Math.round(255 - t * 200)}, 0)`
}

const FREQ_LABELS = [
  { freq: 20, label: '20' },
  { freq: 100, label: '100' },
  { freq: 500, label: '500' },
  { freq: 1000, label: '1K' },
  { freq: 5000, label: '5K' },
  { freq: 10000, label: '10K' },
  { freq: 20000, label: '20K' },
]

const AMP_LABELS = ['100%', '90%', '80%', '70%', '60%', '50%', '40%', '30%', '20%', '10%', '0%']
const BAR_COUNT = 64

export function drawSpectrumCanvas(canvas, result, themeColors) {
  if (!result || !canvas) return
  const colors = { ...FALLBACK_THEME, ...themeColors }
  const ctx = canvas.getContext('2d')
  const width = canvas.width = 800
  const height = canvas.height = 300

  const { bgColor, textColor, accentColor, accentLight, secondaryColor } = colors
  const nyquist = result.sample_rate / 2
  const bins = result.bins
  const barWidth = (width - 80) / BAR_COUNT
  const barMaxHeight = height * 0.75
  const step = Math.floor(bins.length / BAR_COUNT)

  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)

  ctx.strokeStyle = 'rgba(128,128,128,0.2)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const y = (height - 30) * (i / 10)
    ctx.beginPath()
    ctx.moveTo(60, y)
    ctx.lineTo(width - 20, y)
    ctx.stroke()
  }

  ctx.fillStyle = textColor
  ctx.font = '10px Nunito'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 10; i++) {
    const y = (height - 30) * (i / 10) + 4
    ctx.fillText(AMP_LABELS[i], 55, y)
  }

  let maxValue = 0
  let maxIndex = 0
  for (let i = 0; i < bins.length; i++) {
    if (bins[i] > maxValue) {
      maxValue = bins[i]
      maxIndex = i
    }
  }
  const peakFreq = (maxIndex / bins.length) * nyquist

  for (let i = 0; i < BAR_COUNT; i++) {
    let sum = 0
    for (let j = 0; j < step && (i * step + j) < bins.length; j++) {
      sum += bins[i * step + j]
    }
    const value = (sum / step) / 255
    const barHeight = value * barMaxHeight
    const x = 60 + i * (barWidth + 2)
    const y = (height - 30) - barHeight

    const gradient = ctx.createLinearGradient(x, (height - 30), x, y)
    gradient.addColorStop(0, accentColor)
    gradient.addColorStop(0.5, accentLight)
    gradient.addColorStop(1, secondaryColor)

    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.roundRect(x, y, barWidth, barHeight, 3)
    ctx.fill()
  }

  ctx.fillStyle = textColor
  ctx.font = '10px Nunito'
  ctx.textAlign = 'center'
  for (const label of FREQ_LABELS) {
    const x = 60 + (Math.log10(label.freq / 20) / Math.log10(nyquist / 20)) * (width - 80)
    if (x >= 60 && x <= width - 20) {
      ctx.fillText(label.label, x, height - 10)
    }
  }

  ctx.fillText('Frecuencia (Hz)', width / 2, height - 2)

  ctx.fillStyle = accentColor
  ctx.font = 'bold 11px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText(`🔺 Pico: ${Math.round(peakFreq)} Hz`, width - 120, 20)

  ctx.fillStyle = textColor
  ctx.font = 'bold 12px Nunito'
  ctx.fillText('Espectro de Frecuencias', 70, 15)

  ctx.font = '10px Nunito'
  ctx.save()
  ctx.translate(12, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.fillText('Amplitud', 0, 0)
  ctx.restore()
}

export function drawSpectrogramCanvas(canvas, result, themeColors) {
  if (!result || !canvas || !result.spectrogram) return
  const colors = { ...FALLBACK_THEME, ...themeColors }
  const ctx = canvas.getContext('2d')
  const width = canvas.width = 800
  const height = canvas.height = 200

  const { textColor, bgColor } = colors
  const spectrogram = result.spectrogram
  const numFrames = spectrogram.length
  const numFreqBins = spectrogram[0].length

  const graphLeft = 50
  const graphTop = 20
  const graphWidth = width - 70
  const graphHeight = height - 40
  const colsPerFrame = graphWidth / numFrames

  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)

  for (let frame = 0; frame < numFrames; frame++) {
    const x = graphLeft + frame * colsPerFrame
    const bins = spectrogram[frame]
    for (let bin = 0; bin < numFreqBins; bin++) {
      const value = bins[bin] / 255
      const y = graphTop + (bin / numFreqBins) * graphHeight
      const binHeight = Math.max(1, graphHeight / numFreqBins)
      ctx.fillStyle = getColor(value)
      ctx.fillRect(x, graphHeight + graphTop - y - binHeight, Math.ceil(colsPerFrame), binHeight)
    }
  }

  ctx.fillStyle = textColor
  ctx.font = '9px Nunito'
  ctx.textAlign = 'right'
  const nyquist = result.sample_rate / 2
  const freqLabels = [20, 100, 1000, 10000]
  for (const freq of freqLabels) {
    const y = graphTop + graphHeight - (Math.log10(freq / 20) / Math.log10(nyquist / 20)) * graphHeight
    if (y >= graphTop && y <= graphTop + graphHeight) {
      const label = freq >= 1000 ? `${freq / 1000}K` : freq.toString()
      ctx.fillText(label, graphLeft - 5, y + 4)
    }
  }

  ctx.textAlign = 'center'
  ctx.fillText('Tiempo →', width / 2 + 20, height - 5)

  ctx.save()
  ctx.translate(10, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.fillText('Frecuencia', 0, 0)
  ctx.restore()

  ctx.fillStyle = textColor
  ctx.font = 'bold 12px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText('Espectrograma (frecuencia vs tiempo)', graphLeft, 12)

  ctx.font = '9px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText('🔵 Bajo', width - 80, 15)
  ctx.fillText('🟢 Medio', width - 80, 28)
  ctx.fillText('🔴 Alto', width - 80, 41)
}

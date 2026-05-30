Component({
  properties: {
    sources: {
      type: Array,
      value: [],
    },
    activeSource: {
      type: String,
      value: '',
    },
  },

  data: {
    showPanel: false,
    priceRange: '',
    credibilityLevel: '',
  },

  methods: {
    onToggle() {
      this.setData({ showPanel: !this.data.showPanel })
    },

    onSourceTap(e) {
      const source = e.currentTarget.dataset.source
      this.triggerEvent('sourcechange', {
        source: this.data.activeSource === source ? '' : source,
      })
    },

    onPriceTap(e) {
      const { min, max } = e.currentTarget.dataset
      this.setData({ priceRange: `${min}-${max}` })
      this.triggerEvent('pricechange', { min, max })
    },

    onCredibilityTap(e) {
      const score = e.currentTarget.dataset.score
      this.setData({ credibilityLevel: score })
      this.triggerEvent('credibilitychange', { score })
    },

    onClear() {
      this.setData({ priceRange: '', credibilityLevel: '' })
      this.triggerEvent('clear')
    },
  },
})

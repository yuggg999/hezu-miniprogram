Component({
  properties: {
    score: {
      type: Number,
      value: 0,
    },
    text: {
      type: String,
      value: '',
    },
    color: {
      type: String,
      value: '#999',
    },
    size: {
      type: String,
      value: 'normal', // normal | small | large
    },
  },

  computed: {},

  data: {
    levelText: '',
    levelColor: '',
  },

  observers: {
    'score': function(score) {
      let levelText = '风险较高'
      let levelColor = '#e74c3c'

      if (score >= 80) {
        levelText = '高度可信'
        levelColor = '#27ae60'
      } else if (score >= 60) {
        levelText = '较为可信'
        levelColor = '#f39c12'
      } else if (score >= 40) {
        levelText = '需谨慎'
        levelColor = '#e67e22'
      }

      this.setData({
        levelText: this.data.text || levelText,
        levelColor: this.data.color || levelColor,
      })
    },
  },
})

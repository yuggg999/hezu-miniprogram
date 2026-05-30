Component({
  properties: {
    post: {
      type: Object,
      value: {},
    },
  },

  methods: {
    onTap() {
      this.triggerEvent('tap', { id: this.data.post.id })
    },
  },
})

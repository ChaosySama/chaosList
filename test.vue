
// localStorage persistence
var STORAGE_KEY = 'w-list'
var listStorage = {
  fetch: function () {
    var lists = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    lists.forEach(function (list, index) {
      list.id = index
    })
    listStorage.uid = lists.length
    return lists
  },
  save: function (lists) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lists))
  }
}

// visibility filters
var filters = {
  all: function (lists) {
    return lists
  },
  watching: function (lists) {
    return lists.filter(function (list) {
      return !list.end
    })
  },
  end: function (lists) {
    return lists.filter(function (list) {
      return list.end
    })
  }
}

var app = new Vue({
  data: {
    lists: listStorage.fetch(),
    newList: '',
    editedList: null,
    visibility: 'all'
  },

  // watch lists change for localStorage persistence
  watch: {
    lists: {
      handler: function (lists) {
        listStorage.save(lists)
      },
      deep: true
    }
  },

  computed: {
    filteredLists: function () {
      return filters[this.visibility](this.lists)
    }
  },

  filters: {
    pluralize: function (n) {
      return n === 1 ? 'item' : 'items'
    }
  },

  methods: {
    addList: function () {
      var value = this.newList && this.newList.trim()
      if (!value) {
        return
      }
      this.lists.push({
        id: listStorage.uid++,
        title: value,
        process: 1,
        end: false
      })
      this.newList = ''
    },

    removeList: function (list) {
      this.lists.splice(this.lists.indexOf(list), 1)
    },

    editList: function (list) {
      if(list.end) {
      	return
      }
      this.beforeEditCache = list.title
      this.editedList = list
    },

    doneEdit: function (list) {
      if (!this.editedList) {
        return
      }
      this.editedList = null
      list.title = list.title.trim()
      if (!list.title) {
        this.removeList(list)
      }
    },

    cancelEdit: function (list) {
      this.editedList = null
      list.title = this.beforeEditCache
    },

	subProcess: function (list) {
	  if (!list.process || list.process <= 1) {
	  	list.process = 1;
	  	return
	  }
      list.process -= 1; 
    },

    addProcess: function (list) {
	  if (!list.process) {
	  	return
	  }
      list.process += 1; 
    },

  },

  directives: {
    'list-focus': function (el) {
    	el.focus()
    }
  }
})

// handle routing
function onHashChange () {
  var visibility = window.location.hash.replace(/#\/?/, '')
  if (filters[visibility]) {
    app.visibility = visibility
  } else {
    window.location.hash = ''
    app.visibility = 'all'
  }
}

window.addEventListener('hashchange', onHashChange)
onHashChange()

// mount
app.$mount('.listapp')

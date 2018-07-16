
// localStorage persistence
var STORAGE_KEY = 'w-list'
var listStorage = {
  fetch: function () {
    var lists = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    lists.forEach(function (list, index) {
      list.id = index
      list.func = false
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
    visibility: 'all',
    timerFlag: false
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
      for(l of this.lists) {
      	l.func = false
      }
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
        end: false,
        func: false,
      })
      this.newList = ''
    },

    change: function (list) {
    	list.func = false
    },

    removeList: function (list) {
      this.lists.splice(this.lists.indexOf(list), 1)
    },

    editList: function (list) {
      list.func = false
      this.listCache = list
      setTimeout(function(){
        this.beforeEditCache = this.listCache.title
        this.editedList = this.listCache
      }.bind(this),500) 
    },

    toggleTools: function (list) {
      if(list.end) {
      	return
      }
      for(l of this.lists) {
      	if(l == list) continue
      	l.func = false
      }
      list.func = !list.func
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

    cancelTool: function () {
      for(l of this.lists) {
      	l.func = false
      }
    },

    drag: function (event) {
      var label = event.target.lastChild.firstChild.innerHTML
      event.dataTransfer.setData("Text", label.toString())
    },

    drop: function (event) {
      var data = event.dataTransfer.getData("Text")
      var label = event.target.innerHTML
      if(data == label) return
      var v1,v2
      for(i of this.lists) {
        if(data == i.title) v1 = i
        if(label == i.title) v2 = i
      }
      var idx1 = this.lists.indexOf(v1)
      var idx2 = this.lists.indexOf(v2)
      var tempid = v1.id
      v1.id = v2.id
      v2.id = tempid
      this.lists.splice(idx1, 1, v2)
      this.lists.splice(idx2, 1, v1)
    },

    allowDrop: function (event) {
      event.preventDefault()
    },

    isMobile: function () {
      if ((navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i))) {
      	return true
      }
      return false
    },

    mouseDown: function (list,flag) {
      var interval = 130
	  this.timerFlag = false
	  this.setTimer(interval,list,flag)
    },

    mouseUp: function () {
      this.timerFlag = true
    },

    setTimer: function(interval,list,flag) {
    	var inter
    	if(interval > 100) {
    		inter = Math.floor(parseInt(interval)-10)
    	}else if(interval > 40) {
    		inter = Math.floor(parseInt(interval)-5)
    	}else {
    		inter = 40
    	}
    	var tempTimer = setTimeout(function() {
    		flag ? list.process++ : list.process--
    	}, inter)
    	setTimeout(function(){
    		if(this.timerFlag) return
    		this.setTimer(inter,list,flag)
    	}.bind(app),interval)
    },

  },

  directives: {
    'list-focus': function (el) {
      el.focus()
    },
    // v-longtouch="list.title"
    // v-longtouch.self="{test: '123'}"
    'longtouch': function (el, binding) {
      var oDiv = el,
        value = binding.value,
        x = 0, y = 0, z = 0, timer = null;
      oDiv.addEventListener("touchstart",function(e) {
        if(e.touches.length > 1) {
          return false;
        }
        z = 0;
        timer =  setTimeout(function() {
          z = 1;
        }, 500);
        x = e.touches[0].clientX;
        y = e.touches[0].clientY;
        e.preventDefault();
      }, false);
      document.addEventListener("touchmove", function(e) {
        if(x != e.touches[0].clientX || y!= e.touches[0].clientY) {
          clearTimeout(timer);
          return false;
        }
      }, false);
      document.addEventListener("touchend", function(ev) {
        if(z != 1) {
          clearTimeout(timer);
          x = 0;
          y = 0;
          return false;
        } else {
          x = 0;
          y = 0;
          z= 0;
          console.log("long touch")
          console.log(value)
        }
      }, false);
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

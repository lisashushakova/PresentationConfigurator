export default class CustomDropList {
    constructor(listBodyElement, func) {
        this.listBodyElement = listBodyElement
        this.input = this.listBodyElement.querySelector('.custom-drop-list-input')
        this.input.addEventListener('input', () => {
            for (const listItem of this.content.children) {
                if (listItem.innerHTML.toLowerCase().startsWith(this.input.value.toLowerCase())) {
                    listItem.style.display = 'flex'
                } else {
                    listItem.style.display = 'none'
                }
            }
        })
        this.content = this.listBodyElement.querySelector('.custom-drop-list-content')
        this.func = func
        this.contentList = null
        this.selectedElement = null
    }

    loadList(contentList, showProperty) {
        this.content.innerHTML = ''
        this.contentList = contentList
        for (const contentElement of this.contentList) {
            contentElement.classList.add('custom-drop-list-item')
            contentElement.addEventListener('click', () => {
                if (this.selectedElement) this.selectedElement.classList.remove('selected')
                this.selectedElement = contentElement
                this.selectedElement.classList.add('selected')
                this.input.value = contentElement[showProperty]
                this.func(contentElement)
            })
            this.content.appendChild(contentElement)
        }
    }
  }
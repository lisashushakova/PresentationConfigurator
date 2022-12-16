export default class SmallDropList {
    constructor(htmlElement, func) {
        // HTML элемент списка
        this.htmlElement = htmlElement

        // HTML элемент, в который помещается содержимое
        this.contentHTML = this.htmlElement.querySelector('.small-drop-list-content')

        // Строка поиска
        this.input = this.htmlElement.querySelector('.small-drop-list-input')
        this.expanded = false
        this.input.addEventListener('click', () => {
            if (this.expanded) this.contentHTML.style.display = 'flex'
            else this.contentHTML.style.display = 'none'
            this.expanded = !this.expanded
        })
        this.input.addEventListener('input', () => {
            for (const listItem of this.contentHTML.children) {
                if (listItem.innerHTML.toLowerCase().startsWith(this.input.value.toLowerCase())) {
                    listItem.style.display = 'flex'
                } else {
                    listItem.style.display = 'none'
                }
            }
        })



        // Содержимое в виде объекта
        this.contentObject = null

        // Выбранный элемент
        this.selectedElement = null

        // Функция, применяемая к выбранному элементу
        this.func = func
    }

    loadList(itemsList) {
        this.input.value = ''
        this.contentHTML.innerHTML = ''
        this.contentObject = itemsList

        for (const item of itemsList) {
            const itemHTML = document.createElement('div')
            itemHTML.classList.add('small-drop-list-item')
            itemHTML.innerHTML = `${item.name}`
            itemHTML.addEventListener('click', () => {
                this.input.value = `${item.name}`
                this.selectedElement = item
                this.expanded = false
                this.contentHTML.style.display = 'none'
                this.func(item)
            })
            this.contentHTML.appendChild(itemHTML)
        }
    }
}
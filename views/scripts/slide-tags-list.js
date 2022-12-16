export default class SlideTagsList {
    constructor(htmlElement, func) {
        // HTML элемент списка
        this.htmlElement = htmlElement

        // Строка поиска
        this.input = this.htmlElement.querySelector('.custom-drop-list-input')
        this.input.addEventListener('input', () => {
            for (const tagItem of this.contentHTML.children) {
                if (tagItem.innerHTML.toLowerCase().includes(this.input.value.toLowerCase())) {
                    tagItem.style.display = 'flex'
                } else {
                    tagItem.style.display = 'none'
                }
            }
            if (this.input.value !== '') {
                this.contentHTML.children[0].style.display = 'none'
                this.contentHTML.children[1].style.display = 'none'
            } else {
                this.contentHTML.children[0].style.display = 'none'
                this.contentHTML.children[1].style.display = 'flex'
            }
        })

        // HTML элемент, в который помещается содержимое
        this.contentHTML = this.htmlElement.querySelector('.custom-drop-list-content')

        // Содержимое в виде объекта
        this.contentObject = null

        // Выбранный элемент
        this.selectedElement = null

        // Функция, применяемая к выбранному элементу
        this.func = func

    }

    loadList(selectedSlide, tags, updateCallback) {
        this.contentHTML.innerHTML = ''
        this.contentObject = tags

        const createTagModal = document.createElement('div')
        createTagModal.classList.add('create-tag-modal')
        createTagModal.innerHTML = `
            <div>
                <input type="text" class="tagName" placeholder="Имя тега"/>
                <input type="text" class="tagValue" placeholder="Значение"/>
            </div>
            <div>
                <button class="btn-create-tag-accept">Добавить</button>
                <button class="btn-create-tag-cancel">Отмена</button>         
            </div>
        `
        createTagModal.classList.add('create-tag-modal')


        createTagModal.querySelector('.btn-create-tag-accept')
            .addEventListener('click', async () => {
                await this.createTag(selectedSlide)
                this.hideCreateTagModal()
                await updateCallback(selectedSlide)
            })

        createTagModal.querySelector('.btn-create-tag-cancel')
            .addEventListener('click', () => {
                addTagButton.style.display = 'flex'
                this.hideCreateTagModal()
            })

        createTagModal.style.display = 'none'
        this.contentHTML.appendChild(createTagModal)

        const addTagButton = document.createElement('button')
        addTagButton.innerHTML = 'Добавить тег'
        addTagButton.addEventListener('click', async () => {
            addTagButton.style.display = 'none'
            this.showCreateTagModal()
        })
        this.contentHTML.appendChild(addTagButton)
        for (const tag of this.contentObject) {
            const tagElement = document.createElement("div")
            tagElement.style.flexDirection = 'row'
            tagElement.style.gap = '10px'
            if (tag.value) tagElement.innerHTML = `${tag.name}: ${tag.value}`
            else tagElement.innerHTML = `${tag.name}`

            tagElement.addEventListener('click', () => {
                if (this.selectedElement) this.selectedElement.removeChild(this.selectedElement.lastChild)
                const removeTagButton = document.createElement('button')
                removeTagButton.addEventListener('click', async () => {
                    console.log(`Removing ${tag.name}`)
                    await fetch(`http://localhost:8000/links/remove?` + new URLSearchParams({
                        slide_id: selectedSlide.id,
                        tag_name: tag.name,
                    }), {
                        method: 'POST'
                    })
                    updateCallback(selectedSlide)
                })
                removeTagButton.innerHTML='X'
                tagElement.appendChild(removeTagButton)
                this.selectedElement = tagElement

            })


            this.contentHTML.appendChild(tagElement)
        }
    }

    showCreateTagModal() {
        document.querySelector('.create-tag-modal').style.display = 'flex'
    }

    hideCreateTagModal() {
        const createTagModal = document.querySelector('.create-tag-modal')
        createTagModal.querySelector(".tagName").value = ''
        createTagModal.querySelector(".tagValue").value = ''
        createTagModal.style.display = 'none'
    }

    async createTag(selectedSlide) {
        const createTagModal = document.querySelector('.create-tag-modal')
        const tagName = createTagModal.querySelector(".tagName").value
        const tagValue = createTagModal.querySelector(".tagValue").value
        console.log(`Test: ${tagValue} ${tagValue === ''}`)
        await fetch(`http://localhost:8000/links/create?` + new URLSearchParams({
            slide_id: selectedSlide.id,
            tag_name: tagName,
            ...(tagValue !== '' && {value: tagValue})
        }), {
            method: 'POST'
        })

    }


}

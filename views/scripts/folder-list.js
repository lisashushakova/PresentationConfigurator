export default class FolderList {
    constructor(htmlElement, func) {
        // HTML элемент списка
        this.htmlElement = htmlElement

        // HTML элемент, в который помещается содержимое
        this.contentHTML = this.htmlElement.querySelector('.custom-drop-list-content')

        // Строка поиска
        this.input = this.htmlElement.querySelector('.custom-drop-list-input')
        this.input.addEventListener('input', () => {
            for (const folderItem of this.contentHTML.children) {
                if (folderItem.innerHTML.toLowerCase().includes(this.input.value.toLowerCase())) {
                    folderItem.style.display = 'flex'
                    for (const presItem of folderItem.children[1].children) {
                        if (presItem.innerHTML.toLowerCase().includes(this.input.value.toLowerCase())) {
                            console.log(presItem)
                            presItem.style.display = 'flex'
                        } else {
                            console.log(presItem)
                            presItem.style.display = 'none'
                        }
                    }
                } else {
                    folderItem.style.display = 'none'
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

    loadList(folders) {
        this.contentHTML.innerHTML = ''
        this.contentObject = folders
        for (const folder of this.contentObject) {
            const folderElement = document.createElement("div")
            folderElement.classList.add('folder-list-folder-element')
            const folderElementHeader = document.createElement("div")

            const folderElementContents = document.createElement("div")
            folderElementContents.style.display = 'none'
            let contentsVisibility = false
            for (const pres of folder.presentations) {
                const presElement = document.createElement("div")
                presElement.innerHTML = `<div>${pres.name}</div>`
                presElement.classList.add('folder-list-pres-element')
                presElement.addEventListener('click', async () => {
                    document.querySelector('.lds-dual-ring').style.display = 'inline-block'
                    const slides = await fetch('http://localhost:8000/presentations/get', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(pres)
                    }).then(res => res.json())
                    document.querySelector('.lds-dual-ring').style.display = 'none'
                    this.func(pres, slides)

                })
                folderElementContents.appendChild(presElement)
            }

            folderElementHeader.addEventListener('click', () => {
                folderElementContents.style.display = contentsVisibility ? 'none' : 'flex'
                contentsVisibility = !contentsVisibility
            })
            folderElementHeader.innerHTML = `${folder.name}`
            folderElement.appendChild(folderElementHeader)
            folderElement.appendChild(folderElementContents)



            this.contentHTML.appendChild(folderElement)
        }


    }

}

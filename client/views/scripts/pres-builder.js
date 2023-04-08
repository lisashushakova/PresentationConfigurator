import {route} from "./script.js";

export default class PresBuilder {

    buildCompleteEvent = new CustomEvent('build-complete')

    constructor() {
        this.slideBuffer = []

        this.lastBuild = null

        this.backStack = []

        this.container = document.querySelector('.pres-builder')
        this.container.addEventListener('build-complete', () => {
            const buildComplete = document.createElement('div')
            buildComplete.classList.add('pres-builder-build-complete')
            buildComplete.innerHTML = 'Сборка презентации завершена'
            this.body.innerHTML = ''
            this.body.appendChild(buildComplete)

            this.footer.innerHTML = ''

            const downloadBtn = document.createElement('div')
            downloadBtn.classList.add('pres-builder-download-btn')
            this.footer.appendChild(downloadBtn)

            downloadBtn.innerHTML = 'Скачать'

            downloadBtn.addEventListener('click', async () => {
                const blob = await fetch(route + 'presentations/download?' + new URLSearchParams({
                    pres_id: this.lastBuild.id
                })).then(res => res.blob())
                console.log(blob)

                const a = document.createElement('a')
                a.style.display = 'none'
                this.body.appendChild(a)

                const blobURL = window.URL.createObjectURL(blob)
                a.href = blobURL
                a.download = this.lastBuild.name
                a.click()
                window.URL.revokeObjectURL(blobURL)

                skipBtn.click()
            })

            const skipBtn = document.createElement('div')
            skipBtn.classList.add('pres-builder-skip-btn')
            this.footer.appendChild(skipBtn)

            skipBtn.innerHTML = 'Пропустить'

            skipBtn.addEventListener('click', async () => {
                this.init()
                await fetch(route + 'presentations/clear-generated?' + new URLSearchParams({
                    pres_id: this.lastBuild.pres_id
                }), {
                    method: 'POST'
                })
            })

        })

        this.header = document.querySelector('.pres-builder-header')
        this.body = document.querySelector('.pres-builder-body')
        this.footer = document.querySelector('.pres-builder-footer')

    }

    init() {
        this.slideBuffer = []
        this.header.innerHTML = ''
        this.body.innerHTML = ''
        this.footer.innerHTML = ''
        this.nowDragging = null

        const nameField = document.createElement('input')
        nameField.classList.add('pres-builder-name-field')
        nameField.type = 'text'
        nameField.placeholder = 'Новая презентация'
        this.header.appendChild(nameField)

        const dragSpot = document.createElement('div')
        dragSpot.classList.add('pres-builder-drag-spot')
        dragSpot.index = 0
        this.body.appendChild(dragSpot)

        this.body.addEventListener('dragover', (e) => {
            e.preventDefault()
        })

        this.body.addEventListener('dragend', () => {
            this.nowDragging = null
        })


        dragSpot.addEventListener('drop', (e) => {
            e.preventDefault();
            array_move(this.slideBuffer, this.nowDragging.index, dragSpot.index)
            const temp = this.slideBuffer
            this.init()
            this.addSlides(temp)
        })

        const buildBtn = document.createElement('div')
        buildBtn.innerHTML = 'Собрать презентацию'
        buildBtn.classList.add('pres-builder-build-btn')
        buildBtn.addEventListener('click', async () => {
            const foldersTree = await fetch(route + 'folders/tree').then(res => res.json())
            this.drawFolders(foldersTree)
        })
        this.footer.appendChild(buildBtn)
    }

    async buildPres(folder_id) {
        const buildBtn = document.querySelector('.pres-builder-build-btn')
        buildBtn.classList.add('build-wait')
        const nameField = document.querySelector('.pres-builder-name-field')
        let name = nameField.value
        if (name === '') {
            name = 'New Presentation'
        }
        this.lastBuild = await fetch(route + 'presentations/build', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                build_from: this.slideBuffer,
                folder: folder_id
            })
        }).then(res => res.json())
        buildBtn.classList.remove('build-wait')
        this.container.dispatchEvent(this.buildCompleteEvent)
    }

    addSlides(slides) {

        for (const [index, slide] of slides.entries()) {
            this.slideBuffer.push(slide)

            const card = document.createElement('div')
            card.slide = slide
            card.index = index
            card.classList.add('pres-builder-card')
            card.draggable = true
            this.body.appendChild(card)


            const img = document.createElement('img')
            img.src = 'data:image/png;base64,' + slide.thumbnail
            img.classList.add('pres-builder-image')
            img.draggable = true
            card.appendChild(img)

            const dragSpot = document.createElement('div')
            dragSpot.classList.add('pres-builder-drag-spot')
            dragSpot.index = index + 1
            card.dragSpot = dragSpot
            card.appendChild(dragSpot)

            dragSpot.addEventListener('dragover', (e) => {
                e.preventDefault()
            })

            dragSpot.addEventListener('drop', (e) => {
                e.preventDefault();
                array_move(this.slideBuffer, this.nowDragging.index, dragSpot.index)
                const temp = this.slideBuffer
                this.init()
                this.addSlides(temp)
                console.log(this.slideBuffer)
            })


            card.addEventListener('dblclick', () => {
                this.slideBuffer.splice(index, 1)
                const dragSpots = document.querySelectorAll('.pres-builder-drag-spot')
                for (const dragSpot of dragSpots) {
                    if (dragSpot.index > card.index) {
                        dragSpot.index--
                    }
                }
                card.remove()
            })

            card.addEventListener('click', () => {
                console.log(`Card index: ${card.index}`)
                console.log(`Next drag spot index: ${card.dragSpot.index}`)
            })

            card.addEventListener('dragstart', () => {
                this.nowDragging = card
                console.log(this.nowDragging)
            })
        }
    }

    drawFolders(folders) {
        const selectFolderModal = document.querySelector('.builder-select-folder-modal')
        selectFolderModal.classList.remove('hidden')
        const selectFolderModalBody = document.querySelector('.builder-select-folder-modal-body')
        const selectFolderModalFooter = document.querySelector('.builder-select-folder-modal-footer')
        selectFolderModalBody.innerHTML = ''
        selectFolderModalFooter.innerHTML = ''
        for (const folder of folders) {
            const folderObject = document.createElement('div')
            folderObject.classList.add('select-folder-modal-folder')
            selectFolderModalBody.appendChild(folderObject)


            const folderImg = document.createElement('img')
            folderImg.classList.add('select-folder-modal-folder-img')
            folderImg.src = '/views/icons/folder.svg'
            folderObject.appendChild(folderImg)
            folderObject.folderImg = folderImg
            folderObject.innerHTML += folder.name

            folderObject.addEventListener('dblclick', async () => {
                this.selectedFolder = folder.id
                this.backStack.push(folders)
                this.drawFolders(folder.children)
            })
        }

        const confirmFolderSelectBtn = document.createElement('div')
        confirmFolderSelectBtn.classList.add('builder-select-folder-modal-confirm-btn')
        confirmFolderSelectBtn.innerHTML = 'OK'

        confirmFolderSelectBtn.addEventListener('click', async () => {
            selectFolderModal.classList.add('hidden')
            await this.buildPres(this.selectedFolder)
        })

        selectFolderModalFooter.appendChild(confirmFolderSelectBtn)

        const backBtn = document.createElement('div')
        backBtn.classList.add('builder-select-folder-modal-back-btn')
        backBtn.innerHTML = 'Назад'

        backBtn.addEventListener('click', () => {
            if (this.backStack.length > 0) {
                folders = this.backStack.pop()
                this.drawFolders(folders)
            }
        })

        selectFolderModalFooter.appendChild(backBtn)
    }


}


const array_move = (arr, old_index, new_index) => {
    const el = arr[old_index]
    arr.splice(old_index, 1)
    if (new_index > old_index) {
        new_index--
    }
    arr.splice(new_index, 0, el)
}

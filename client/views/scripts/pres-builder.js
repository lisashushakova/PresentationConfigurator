import {route} from "./script.js";

export default class PresBuilder {

    buildCompleteEvent = new CustomEvent('build-complete')

    constructor() {
        this.slideBuffer = []

        this.lastBuild = null

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
            })

             const skipBtn = document.createElement('div')
            skipBtn.classList.add('pres-builder-skip-btn')
            this.footer.appendChild(skipBtn)

            skipBtn.innerHTML = 'Пропустить'

            skipBtn.addEventListener('click', () => {
                this.init()
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
            console.log(this.slideBuffer)
        })

        const buildBtn = document.createElement('div')
        buildBtn.innerHTML = 'Собрать презентацию'
        buildBtn.classList.add('pres-builder-build-btn')
        buildBtn.addEventListener('click', async () => {
            buildBtn.classList.add('build-wait')
            this.lastBuild = await fetch(route + 'presentations/build', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: nameField.value,
                    build_from: this.slideBuffer
                })
            }).then(res => res.json())
            buildBtn.classList.remove('build-wait')
            this.container.dispatchEvent(this.buildCompleteEvent)
        })
        this.footer.appendChild(buildBtn)
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
}

const array_move = (arr, old_index, new_index) => {
    const el = arr[old_index]
    arr.splice(old_index, 1)
    if (new_index > old_index) {
        new_index--
    }
    arr.splice(new_index, 0, el)
}

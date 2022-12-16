export default class PresentationDrawer {
    constructor(drawerElement, func) {

        this.drawerElement = drawerElement
        this.func = func
        this.selectedElement = null
        console.log(drawerElement)
        console.log(this.drawerElement)
    }

    draw(slides) {
        console.log(this)
        this.drawerElement.innerHTML = ''
        this.slides = slides
        for (const slide of this.slides) {
            const img = document.createElement('img')
            img.src = 'data:image/png;base64,' + slide.thumbnail
            img.classList.add('presentation-drawer-image')
            img.addEventListener('click', () => {
                if (this.selectedElement) this.selectedElement.classList.remove('selected')
                this.selectedElement = img
                this.selectedElement.classList.add('selected')
                this.func(slide)
            })
            const tagList = document.createElement('div')
            tagList.classList.add('presentation-drawer-image-taglist')
            this.drawerElement.appendChild(img)
        }
    }
}


class presentationDrawer {
    constructor(drawerElement, func) {
        this.drawerElement = drawerElement
        this.func = func
        this.selectedElement = null
    }

    draw(slides) {
        this.drawerElement.innerHTML = ''
        this.slides = slides
        for (const slide of this.slides) {
            const img = document.createElement('img')
            const bytes_base64 = slide.thumbnail
            img.src = 'data:image/png;base64,' + bytes_base64
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
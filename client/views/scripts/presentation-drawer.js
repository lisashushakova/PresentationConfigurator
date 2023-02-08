import {route} from "./script.js";

export default class PresentationDrawer {

    constructor() {
        this.selectedSlides = []
    }

    async draw(drawerElement, slides) {
        drawerElement.innerHTML = ''
        this.slides = slides
        if (slides != null) {
            if (slides.length === 0) {
                const slidesNotFoundPanel = document.createElement('div')
                slidesNotFoundPanel.classList.add('pres-drawer-not-found')
                slidesNotFoundPanel.innerHTML = 'Слайдов не найдено'
                drawerElement.appendChild(slidesNotFoundPanel)
            }
            for (const [index, slide] of this.slides.entries()) {
                const card = document.createElement('div')
                card.classList.add('pres-drawer-card')
                drawerElement.appendChild(card)
                card.slide = slide
                card.index = index
                card.selected = false

                if (slide.pres_name != null) {
                    const cardHeader = document.createElement('div')
                    cardHeader.classList.add('pres-drawer-card-header')
                    card.appendChild(cardHeader)

                    cardHeader.innerHTML = `${slide.pres_name}, слайд ${slide.index + 1}`
                }

                const cardBody = document.createElement('div')
                cardBody.classList.add('pres-drawer-card-body')
                card.appendChild(cardBody)


                const img = document.createElement('img')
                cardBody.appendChild(img)
                card.img = img
                img.src = 'data:image/png;base64,' + slide.thumbnail
                img.classList.add('pres-drawer-image')

                const tagFooterCurtain = document.createElement('div')
                tagFooterCurtain.classList.add('pres-drawer-tag-footer-curtain')
                cardBody.appendChild(tagFooterCurtain)

                const tagFooterCurtainLabel = document.createElement('div')
                tagFooterCurtainLabel.classList.add('pres-drawer-tag-footer-curtain-label')
                tagFooterCurtain.appendChild(tagFooterCurtainLabel)
                tagFooterCurtainLabel.innerHTML = 'Теги'

                const tagFooter = document.createElement('div')
                tagFooter.classList.add('pres-drawer-tag-footer')
                cardBody.appendChild(tagFooter)

                tagFooter.closed = true
                tagFooterCurtain.classList.add('closed')
                tagFooter.classList.add('closed')
                tagFooterCurtain.addEventListener('dblclick', () => {
                    tagFooter.closed = !tagFooter.closed
                    if (tagFooter.closed) {
                        tagFooterCurtain.classList.add('closed')
                        tagFooter.classList.add('closed')
                    } else {
                        tagFooterCurtain.classList.remove('closed')
                        tagFooter.classList.remove('closed')
                    }
                })

                const addTagLabel = document.createElement('div')
                addTagLabel.classList.add('pres-drawer-add-tag-label')
                tagFooter.appendChild(addTagLabel)

                const addTagName = document.createElement('input')
                addTagName.classList.add('pres-drawer-add-tag-name')
                addTagLabel.appendChild(addTagName)
                addTagName.type = 'text'
                addTagName.placeholder = 'Имя тега'


                const addTagValue = document.createElement('input')
                addTagValue.classList.add('pres-drawer-add-tag-value')
                addTagLabel.appendChild(addTagValue)
                addTagValue.type = 'text'
                addTagValue.placeholder = 'Значение'

                const addTagBtn = document.createElement('div')
                addTagBtn.classList.add('pres-drawer-add-tag-btn')
                addTagLabel.appendChild(addTagBtn)
                addTagBtn.innerHTML = '+'


                addTagBtn.addEventListener('click', async () => {
                    await fetch(route + 'links/create?' + new URLSearchParams({
                        slide_id: card.slide.id,
                        tag_name: addTagName.value,
                        value: addTagValue.value
                    }), {
                        method: 'POST'
                    })
                    createTagLabel(card, tagFooter, addTagName.value, addTagValue.value)
                    addTagName.value = ''
                    addTagValue.value = ''
                })

                const slideTags = await fetch(route + 'links/slide-tags?' + new URLSearchParams({
                    slide_id: card.slide.id
                })).then(res => res.json())

                for (const tag of slideTags) {
                    createTagLabel(card, tagFooter, tag.name, tag.value)
                }

                card.addEventListener('click', (e) => {
                    if (card.img === e.target) {
                        card.selected = !card.selected
                        if (card.selected) {
                            this.selectedSlides.push(card.slide)
                            card.classList.add('selected')
                        } else {
                            this.selectedSlides.splice(card.index)
                            card.classList.remove('selected')
                        }
                    }
                })
            }
        }
    }
}

const createTagLabel = (card, tagFooter, name, value) => {
    const tagLabel = document.createElement('div')
    tagLabel.classList.add('pres-drawer-tag-label')
    tagFooter.appendChild(tagLabel)

    const tagName = document.createElement('div')
    tagName.classList.add('pres-drawer-tag-name')
    tagLabel.appendChild(tagName)
    tagName.innerHTML = name

    const tagValue = document.createElement('input')
    tagValue.classList.add('pres-drawer-tag-value')
    tagLabel.appendChild(tagValue)
    tagValue.type = 'text'
    tagValue.value = value

    tagValue.addEventListener('change', async () => {
        await fetch(route + 'links/create?' + new URLSearchParams({
            slide_id: card.slide.id,
            tag_name: name,
            value: tagValue.value
        }), {
            method: 'POST'
        })
    })

    const removeTagBtn = document.createElement('div')
    removeTagBtn.classList.add('pres-drawer-remove-tag-btn')
    tagLabel.appendChild(removeTagBtn)
    removeTagBtn.innerHTML = 'x'
    removeTagBtn.addEventListener('click', async () => {
        await fetch(route + 'links/remove?' + new URLSearchParams({
            slide_id: card.slide.id,
            tag_name: name
        }), {
            method: 'POST'
        })
        tagLabel.remove()
    })
}


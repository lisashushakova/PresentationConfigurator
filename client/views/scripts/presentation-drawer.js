import {route} from "./script.js";

export default class PresentationDrawer {

    constructor() {
        this.selectedSlides = []
    }

    async draw(drawerElement, slides, pres_id) {
        this.drawerElement = drawerElement

        drawerElement.innerHTML = ''
        this.slides = slides
        this.ratio = -1
        this.pres_id = pres_id
        this.selectedSlides = []
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
                card.tagNames = []
                card.selected = false

                if (slide.pres_name != null) {
                    const cardHeader = document.createElement('div')
                    cardHeader.classList.add('pres-drawer-card-header')
                    card.appendChild(cardHeader)

                    cardHeader.innerHTML = `${slide.pres_name}, слайд ${slide.index + 1}`
                }

                const cardBody = document.createElement('div')
                cardBody.classList.add('pres-drawer-card-body')
                if (card.slide.ratio === 0) {
                    cardBody.classList.add('ratio-4-to-3')
                } else {
                    cardBody.classList.add('ratio-16-to-9')
                }
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

                const slideTags = await fetch(route + 'links/slide-tags?' + new URLSearchParams({
                    slide_id: card.slide.id
                })).then(res => res.json())

                tagFooter.tags = slideTags.map(tag => tag.name)

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
                    if (addTagName.value !== '' && /^[0-9]*$/.test(addTagValue.value)) {
                        const query = {
                            slide_id: card.slide.id,
                            tag_name: addTagName.value
                        }
                        if (addTagValue.value !== '') {
                            query.value = addTagValue.value
                        }
                        await fetch(route + 'links/create-slide-link?' + new URLSearchParams(query), {
                            method: 'POST'
                        })

                        if (tagFooter.tags.includes(addTagName.value)) {
                            const tagLabels = document.querySelectorAll('.pres-drawer-tag-label')
                            for (const tagLabel of tagLabels) {
                                const tagName = tagLabel.querySelector('.pres-drawer-tag-name')
                                if (tagName.innerHTML === addTagName.value) {
                                    const tagValue = tagLabel.querySelector('.pres-drawer-tag-value')
                                    tagValue.value = addTagValue.value
                                }
                            }
                        } else {
                            tagFooter.tags.push(addTagName.value)
                            createTagLabel(card, tagFooter, addTagName.value, addTagValue.value)
                        }


                        addTagName.value = ''
                        addTagValue.value = ''
                    }

                })


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

    async drawPresentationCard(drawerElement) {
        drawerElement.innerHTML = ''

        const card = document.createElement('div')
        card.classList.add('pres-drawer-card')
        card.classList.add('pres-tags')
        drawerElement.appendChild(card)
        card.innerHTML = 'Теги презентации'
        card.pres_id = this.pres_id

        const tagFooter = document.createElement('div')
        tagFooter.classList.add('pres-drawer-tag-footer')
        card.appendChild(tagFooter)

        const presTags = await fetch(route + 'links/pres-tags?' + new URLSearchParams({
            pres_id: this.pres_id
        })).then(res => res.json())

        tagFooter.tags = presTags.map(tag => tag.name)

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
            if (addTagName.value !== '' && /^[0-9]*$/.test(addTagValue.value)) {
                const query = {
                    pres_id: card.pres_id,
                    tag_name: addTagName.value
                }
                if (addTagValue.value !== '') {
                    query.value = addTagValue.value
                }
                await fetch(route + 'links/create-pres-link?' + new URLSearchParams(query), {
                    method: 'POST'
                })

                if (tagFooter.tags.includes(addTagName.value)) {
                    const tagLabels = document.querySelectorAll('.pres-drawer-tag-label')
                    for (const tagLabel of tagLabels) {
                        const tagName = tagLabel.querySelector('.pres-drawer-tag-name')
                        if (tagName.innerHTML === addTagName.value) {
                            const tagValue = tagLabel.querySelector('.pres-drawer-tag-value')
                            tagValue.value = addTagValue.value
                        }
                    }
                } else {
                    tagFooter.tags.push(addTagName.value)
                    createPresTagLabel(card, tagFooter, addTagName.value, addTagValue.value)
                }

                addTagName.value = ''
                addTagValue.value = ''
            }

        })

        for (const tag of presTags) {
            createPresTagLabel(card, tagFooter, tag.name, tag.value)
        }
    }

    filterSlides(ratio) {
        this.ratio = ratio
        for (const slideCard of this.drawerElement.children) {
            if (slideCard.slide.ratio !== ratio && ratio !== -1) {
                slideCard.classList.add('hidden')
            } else {
                slideCard.classList.remove('hidden')
            }
        }
    }

    getSelectedDisplayedSlides() {
        return this.selectedSlides.filter(slide => slide.ratio === this.ratio || this.ratio === -1)
    }

    getAllDisplayedSlides() {
        const exportSlides = []
        for (const slide of this.slides) {
            if (slide.ratio === this.ratio || this.ratio === -1) {
                exportSlides.push(slide)
            }
        }
        return exportSlides
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
        if (/^[0-9]*$/.test(tagValue.value)) {
            const query = {
                slide_id: card.slide.id,
                tag_name: name
            }
            if (tagValue.value !== '') {
                query.value = tagValue.value
            }
            await fetch(route + 'links/create-slide-link?' + new URLSearchParams(query), {
                method: 'POST'
            })
        } else {
            tagValue.value = value
        }

    })

    const removeTagBtn = document.createElement('div')
    removeTagBtn.classList.add('pres-drawer-remove-tag-btn')
    tagLabel.appendChild(removeTagBtn)
    removeTagBtn.innerHTML = 'x'
    removeTagBtn.addEventListener('click', async () => {
        await fetch(route + 'links/remove-slide-link?' + new URLSearchParams({
            slide_id: card.slide.id,
            tag_name: name
        }), {
            method: 'POST'
        })
        tagFooter.tags = tagFooter.tags.map(tagName => tagName !== name)
        tagLabel.remove()
    })
}

const createPresTagLabel = (card, tagFooter, name, value) => {
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
        if (/^[0-9]*$/.test(tagValue.value)) {
            const query = {
                pres_id: card.pres_id,
                tag_name: name
            }
            if (tagValue.value !== '') {
                query.value = tagValue.value
            }
            await fetch(route + 'links/create-pres-link?' + new URLSearchParams(query), {
                method: 'POST'
            })
        } else {
            tagValue.value = value
        }

    })

    const removeTagBtn = document.createElement('div')
    removeTagBtn.classList.add('pres-drawer-remove-tag-btn')
    tagLabel.appendChild(removeTagBtn)
    removeTagBtn.innerHTML = 'x'
    removeTagBtn.addEventListener('click', async () => {
        await fetch(route + 'links/remove-pres-link?' + new URLSearchParams({
            pres_id: card.pres_id,
            tag_name: name
        }), {
            method: 'POST'
        })
        tagFooter.tags = tagFooter.tags.map(tagName => tagName !== name)
        tagLabel.remove()
    })
}


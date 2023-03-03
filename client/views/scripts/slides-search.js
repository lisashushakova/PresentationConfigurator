import {route} from "./script.js";

export default function initSlideSearch(drawerElement, presDrawer) {
    const slideSearchField = document.querySelector('.pres-drawer-search-field')
    const tagSearchBtn = document.querySelector('#pres-drawer-tag-search-btn')
    const textSearchBtn = document.querySelector('#pres-drawer-text-search-btn')
    const slideRatioSearch = document.querySelector('#pres-drawer-slide-ratio-btn')

    const mainPresColumnHeader = document.querySelector('.main-pres-column-header')

    const SlideRatio = {
        'RATIO_AUTO': -1,
        'RATIO_4_TO_3': 0,
        'RATIO_16_TO_9': 1
    }

    slideRatioSearch.innerHTML = 'Авто'
    let slideRatioState = SlideRatio.RATIO_AUTO
    slideRatioSearch.addEventListener('click', () => {
        switch (slideRatioState) {
            case SlideRatio.RATIO_AUTO:
                slideRatioState = SlideRatio.RATIO_4_TO_3
                slideRatioSearch.innerHTML = '4:3'
                presDrawer.filterSlides(slideRatioState)
                break
            case SlideRatio.RATIO_4_TO_3:
                slideRatioState = SlideRatio.RATIO_16_TO_9
                slideRatioSearch.innerHTML = '16:9'
                presDrawer.filterSlides(slideRatioState)
                break
            case SlideRatio.RATIO_16_TO_9:
                slideRatioState = SlideRatio.RATIO_AUTO
                slideRatioSearch.innerHTML = 'Авто'
                presDrawer.filterSlides(slideRatioState)
                break
        }
    })


    tagSearchBtn.addEventListener('click', async () => {
        const slidesFound = await fetch(route + 'slides/by-tag-query?' + new URLSearchParams({
            query: slideSearchField.value,
            ratio: slideRatioState
        })).then(res => res.json())
        mainPresColumnHeader.innerHTML = 'Результаты поиска по тегам'
        await presDrawer.draw(drawerElement, slidesFound, null)

    })

    textSearchBtn.addEventListener('click', async () => {
        console.log(slideRatioState)
        const slidesFound = await fetch(route + 'slides/by-text?' + new URLSearchParams({
            search_phrase: slideSearchField.value,
            ratio: slideRatioState
        })).then(res => res.json())
        mainPresColumnHeader.innerHTML = 'Результаты поиска по тексту'
        await presDrawer.draw(drawerElement, slidesFound, null)
    })


}

